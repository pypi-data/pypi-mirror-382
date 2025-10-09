from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore.settings import settings


class LoginBanQuerySet(models.QuerySet):
    def is_ban(self, username):
        if not username or settings.PFX_LOGIN_BAN_FAILED_NUMBER == 0:
            return False
        try:
            ban = self.get(username=username)
        except LoginBan.DoesNotExist:
            return False
        if ban.failed_counter % settings.PFX_LOGIN_BAN_FAILED_NUMBER == 0:
            seconds = settings.PFX_LOGIN_BAN_SECONDS_START + (
                settings.PFX_LOGIN_BAN_SECONDS_STEP * (
                    ban.failed_counter //
                    settings.PFX_LOGIN_BAN_FAILED_NUMBER - 1))
            ban_time = ban.last_failed + timedelta(seconds=seconds)
            now = timezone.now()
            if now < ban_time:
                return ban_time - now
        return False

    def ban(self, username):
        if not username:
            return
        try:
            ban = self.get(username=username)
            ban.save()
        except LoginBan.DoesNotExist:
            LoginBan.objects.create(username=username)

    def unban(self, username):
        if not username:
            return
        self.filter(username=username).delete()


class LoginBan(models.Model):
    username = models.CharField(_("Username"), max_length=150, unique=True)
    failed_counter = models.IntegerField(_("Failed counter"))
    last_failed = models.DateTimeField(_("Last failed"), auto_now=True)

    objects = LoginBanQuerySet.as_manager()

    class Meta:
        verbose_name = _("Login ban")
        verbose_name_plural = _("Login bans")

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.failed_counter = (self.failed_counter or 0) + 1
        return super().save(*args, **kwargs)
