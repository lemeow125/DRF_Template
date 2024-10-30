import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall("[A-Z]", password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter (A-Z).")
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter (A-Z).")


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall("[a-z]", password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter (a-z).")
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 lowercase letter (a-z).")


class SpecialCharacterValidator(object):
    def validate(self, password, user=None):
        if not re.findall("[@#$%^&*()_+/\<>;:!?]", password):
            raise ValidationError(
                _(
                    "The password must contain at least 1 special character (@, #, $, etc.)."
                )
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 special character (@, #, $, etc.)."
        )


class NumberValidator(object):
    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("The password must contain at least one numerical digit (0-9).")
            )

    def get_help_text(self):
        return _("Your password must contain at least numerical digit (0-9).")
