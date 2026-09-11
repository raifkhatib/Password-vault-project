import base64
import secrets
import string

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


KDF_ITERATIONS = 600_000


def derive_vault_key(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS
    )

    raw_key = kdf.derive(master_password.encode("utf-8"))
    return base64.urlsafe_b64encode(raw_key)


def encrypt_text(vault_key, text):
    value = text or ""
    encrypted = Fernet(vault_key).encrypt(value.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_text(vault_key, encrypted_text):
    if not encrypted_text:
        return ""

    try:
        decrypted = Fernet(vault_key).decrypt(
            encrypted_text.encode("utf-8")
        )
        return decrypted.decode("utf-8")
    except InvalidToken as error:
        raise ValueError("The encrypted value could not be decrypted.") from error


def generate_secure_password(length=20):
    if length < 12:
        raise ValueError("Password length must be at least 12.")

    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+"

    password_characters = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]

    all_characters = uppercase + lowercase + digits + symbols

    for _ in range(length - 4):
        password_characters.append(secrets.choice(all_characters))

    for position in range(len(password_characters) - 1, 0, -1):
        random_position = secrets.randbelow(position + 1)
        password_characters[position], password_characters[random_position] = (
            password_characters[random_position],
            password_characters[position]
        )

    return "".join(password_characters)