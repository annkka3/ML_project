from dataclasses import dataclass
from utils.hasher import PasswordHasher
from utils.validator import UserValidator

@dataclass
class User:
    id: str
    email: str
    _password_hash: str

    @classmethod
    def create(cls, id: str, email: str, password: str) -> 'User':
        UserValidator.validate_email(email)
        UserValidator.validate_password(password)
        return cls(id=id, email=email, _password_hash=PasswordHasher.hash(password))

    def check_password(self, password: str) -> bool:
        return PasswordHasher.check(password, self._password_hash)
