import inspect
import logging
from pathlib import Path

from django import apps
from django.apps import AppConfig
from django.db.models.signals import post_migrate

import yaml

from pfx.pfxcore.shortcuts import permissions, settings

logger = logging.getLogger(__name__)


def update_groups_permissions(
        groups, base_path, group_cache, is_last, module, out=True):
    from django.contrib.auth.models import Group

    out and print(f"Import file {base_path}/groups.yaml", end=" ")
    todo = False

    def log(txt):
        if not out:
            return
        nonlocal todo
        if not todo:
            print()
            todo = True
        print("  * ", txt)

    db_groups = {g.name: g for g in Group.objects.all()}

    for name, perms in groups.items():
        group_cache.add(name)
        created = name not in db_groups
        group = Group.objects.create(name=name) if created else db_groups[name]
        if created:
            log(f"Create group {name}")
        current_perms = {
            f'{p.content_type.app_label}.{p.codename}'
            for p in group.permissions.filter(content_type__app_label=module)}
        if created or not settings.PFX_AUTH_GROUPS_CREATE_ONLY:
            to_add = set(perms) - current_perms
            to_remove = current_perms - set(perms)
            if to_add:
                log(f"Add permissions for group {name}: {', '.join(to_add)}")
                group.permissions.add(*permissions(*to_add))
            if to_remove:
                log(f"Remove permissions for group {name}: "
                    f"{', '.join(to_remove)}")
                group.permissions.remove(*permissions(*to_remove))

    if is_last and not settings.PFX_AUTH_GROUPS_CREATE_ONLY:
        names = db_groups.keys() - group_cache
        if names:
            log(f"Delete groups: {', '.join(names)}")
            Group.objects.filter(name__in=names).delete()

    if not todo:
        out and print("[nothing to do]")


def update_groups_permissions_action(sender, **kwargs):
    if not isinstance(sender, PfxAppConfig):
        return

    base_path = '/'.join(sender.__class__.__module__.split('.')[:-1])
    is_last = [
        a for a in apps.apps.get_app_configs()
        if isinstance(a, PfxAppConfig)][-1].name == sender.name
    module = Path(inspect.getfile(sender.__class__)).parent.name

    groups_file = Path(
        Path(inspect.getfile(sender.__class__)).parent, 'groups.yaml')
    if not groups_file.exists():
        return

    with groups_file.open() as file:
        groups = yaml.safe_load(file)

    update_groups_permissions(
        groups, base_path, sender._processed_groups, is_last, module)


class PfxAppConfig(AppConfig):
    _processed_groups = set()

    def ready(self):
        post_migrate.connect(update_groups_permissions_action, sender=self)
        return super().ready()


class PfxCoreConfig(AppConfig):
    name = 'pfx.pfxcore'
    default = True
