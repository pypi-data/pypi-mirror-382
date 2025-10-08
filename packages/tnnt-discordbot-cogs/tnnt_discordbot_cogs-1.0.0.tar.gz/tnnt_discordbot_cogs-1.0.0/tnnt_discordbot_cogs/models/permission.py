"""
Permission model for the TNNT Discord bot.
"""

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class for the Permission model.
        """

        managed = False
        default_permissions = ()
        permissions = (
            ("locate", _("Can run the `/locate` command")),
            ("lookup", _("Can run the `/lookup` command")),
        )
        verbose_name = _("Command Permission")
