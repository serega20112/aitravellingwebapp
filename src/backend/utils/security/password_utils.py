import bcrypt


def is_bcrypt_hash(s: str) -> bool:
    """Проверяет, является ли строка валидным bcrypt-хэшем.

    Args:
        s: Строка для проверки

    Returns:
        bool: True если строка является bcrypt-хэшем, иначе False.
    """
    return s.startswith(("$2a$", "$2b$", "$2y$"))


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt и возвращает строку хэша.

    Args:
        password: Обычный текстовый пароль

    Returns:
        str: Хеш пароля
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(a: str, b: str) -> bool:
    """Проверяет соответствие пароля и хэша (порядок аргументов может быть любой).

    Args:
        a: Пароль или хеш
        b: Пароль или хеш

    Returns:
        bool: True если пароль соответствует хэшу, иначе False.
    """
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
