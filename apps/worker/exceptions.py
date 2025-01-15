from django.core.exceptions import ValidationError

class CustomUserFuncionarioError(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidUsernameError(CustomUserFuncionarioError):
    """Exception raised for errors in the username validation."""

    def __init__(self, username, message="Username must be at least 5 characters long and contain only alphanumeric characters."):
        self.username = username
        self.message = message
        super().__init__(self.message)

def validate_username(username):
    if len(username) < 5 or not username.isalnum():
        raise InvalidUsernameError(username)

def validate_custom_user_funcionario(instance):
    try:
        validate_username(instance.username)
    except InvalidUsernameError as e:
        raise ValidationError(f"Invalid username: {e.username}. {e.message}")

# Usage example:
# try:
#     validate_custom_user_funcionario(custom_user_instance)
# except ValidationError as e:
#     print(e)