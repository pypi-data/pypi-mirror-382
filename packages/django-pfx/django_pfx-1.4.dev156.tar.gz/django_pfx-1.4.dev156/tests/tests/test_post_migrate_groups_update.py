from django.contrib.auth.models import Group
from django.test import TestCase
from django.test.utils import override_settings

from pfx.pfxcore.apps import update_groups_permissions
from pfx.pfxcore.test import TestAssertMixin


class TestPostMigrateGroupsUpdate(TestAssertMixin, TestCase):

    def test_groups(self):
        update_groups_permissions(dict(
            reader=[
                'tests.view_author'],
            editor=[
                'tests.view_author',
                'tests.add_author']), 'tests', set(), True, 'tests', False)

        groups = {g.name: g for g in Group.objects.all()}
        self.assertEqual(groups.keys(), {'reader', 'editor'})
        perms = {p.codename for p in groups['reader'].permissions.all()}
        self.assertEqual(perms, {'view_author'})
        perms = {p.codename for p in groups['editor'].permissions.all()}
        self.assertEqual(perms, {'view_author', 'add_author'})

        update_groups_permissions(dict(
            editor=[
                'tests.view_author',
                'tests.change_author'],
            new=[]), 'tests', set(), True, 'tests', False)

        groups = {g.name: g for g in Group.objects.all()}
        self.assertEqual(groups.keys(), {'editor', 'new'})
        perms = {p.codename for p in groups['editor'].permissions.all()}
        self.assertEqual(perms, {'view_author', 'change_author'})
        perms = {p.codename for p in groups['new'].permissions.all()}
        self.assertEqual(perms, set())

    @override_settings(PFX_AUTH_GROUPS_CREATE_ONLY=True)
    def test_groups_create_only(self):
        update_groups_permissions(dict(
            reader=[
                'tests.view_author'],
            editor=[
                'tests.view_author',
                'tests.add_author']), 'tests', set(), True, 'tests', False)

        groups = {g.name: g for g in Group.objects.all()}
        self.assertEqual(groups.keys(), {'reader', 'editor'})
        perms = {p.codename for p in groups['reader'].permissions.all()}
        self.assertEqual(perms, {'view_author'})
        perms = {p.codename for p in groups['editor'].permissions.all()}
        self.assertEqual(perms, {'view_author', 'add_author'})

        update_groups_permissions(dict(
            editor=[
                'tests.view_author',
                'tests.change_author'],
            new=[]), 'tests', set(), True, 'tests', False)

        groups = {g.name: g for g in Group.objects.all()}
        self.assertEqual(groups.keys(), {'reader', 'editor', 'new'})
        perms = {p.codename for p in groups['reader'].permissions.all()}
        self.assertEqual(perms, {'view_author'})
        perms = {p.codename for p in groups['editor'].permissions.all()}
        self.assertEqual(perms, {'view_author', 'add_author'})
        perms = {p.codename for p in groups['new'].permissions.all()}
        self.assertEqual(perms, set())
