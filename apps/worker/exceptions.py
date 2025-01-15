from django.core.exceptions import ValidationError

class InvalidUsernameError(Exception):
    """Exception raised for errors in the username validation."""

    def __init__(self, username, message="O nome de usuário deve ter pelo menos 5 caracteres e conter apenas caracteres alfanuméricos."):
        self.username = username
        self.message = message
        super().__init__(self.message)


def validate_username(username):
    if len(username) < 5 or not username.isalnum():
        raise InvalidUsernameError(username)

def validate_email(email):
    from .models import CustomUser_Funcionario
    if CustomUser_Funcionario.objects.filter(email=email).exists():
        raise EmailAlreadyExistsError(email)

def validate_custom_user_funcionario(instance):
    try:
        validate_username(instance.username)
        validate_email(instance.email)
    except (InvalidUsernameError, EmailAlreadyExistsError) as e:
        raise ValidationError(f"{e.message}")