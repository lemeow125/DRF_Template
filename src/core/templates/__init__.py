from djoser import email


class ActivationEmail(email.ActivationEmail):
    template_name = "email_activation.html"


class PasswordResetEmail(email.PasswordResetEmail):
    template_name = "password_change.html"
