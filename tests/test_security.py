import pytest

from security import (
    decrypt_text,
    derive_vault_key,
    encrypt_text,
    generate_secure_password
)


TEST_SALT = b"1234567890abcdef"


@pytest.fixture(scope="module")
def vault_key():
    return derive_vault_key(
        "TemporaryMasterPassword!",
        TEST_SALT
    )


def test_key_derivation_is_repeatable():
    first_key = derive_vault_key(
        "TemporaryMasterPassword!",
        TEST_SALT
    )
    second_key = derive_vault_key(
        "TemporaryMasterPassword!",
        TEST_SALT
    )

    assert first_key == second_key


def test_different_salts_create_different_keys():
    first_key = derive_vault_key(
        "TemporaryMasterPassword!",
        b"1234567890abcdef"
    )
    second_key = derive_vault_key(
        "TemporaryMasterPassword!",
        b"fedcba0987654321"
    )

    assert first_key != second_key


def test_encryption_round_trip(vault_key):
    plaintext = "ExamplePassword123!"
    ciphertext = encrypt_text(vault_key, plaintext)

    assert ciphertext != plaintext
    assert decrypt_text(vault_key, ciphertext) == plaintext


def test_tampered_ciphertext_is_rejected(vault_key):
    ciphertext = encrypt_text(vault_key, "Private value")
    replacement = "A" if ciphertext[-1] != "A" else "B"
    tampered_ciphertext = ciphertext[:-1] + replacement

    with pytest.raises(ValueError):
        decrypt_text(vault_key, tampered_ciphertext)


def test_password_generator_requirements():
    password = generate_secure_password(24)

    assert len(password) == 24
    assert any(character.isupper() for character in password)
    assert any(character.islower() for character in password)
    assert any(character.isdigit() for character in password)
    assert any(not character.isalnum() for character in password)


def test_password_generator_rejects_short_length():
    with pytest.raises(ValueError):
        generate_secure_password(11)