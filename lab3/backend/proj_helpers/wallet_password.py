from passlib.handlers.pbkdf2 import pbkdf2_sha256


def encrypt(password) -> str:
    "Returns encrypted string for given password."
    return pbkdf2_sha256.encrypt(
        password,
        rounds=26000,
        salt_size=32,
    )


def check_pass(raw, enc_string) -> bool:
    "Checks the raw password against encrypted string."
    return pbkdf2_sha256.verify(raw, enc_string)