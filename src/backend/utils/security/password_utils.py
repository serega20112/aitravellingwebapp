import bcrypt


def is_bcrypt_hash(s: str) -> bool:
    return s.startswith(("$2a$", "$2b$", "$2y$"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(a: str, b: str) -> bool:
    if is_bcrypt_hash(a):
        hashed, password = a, b
    elif is_bcrypt_hash(b):
        hashed, password = b, a
    else:
        return False
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False
