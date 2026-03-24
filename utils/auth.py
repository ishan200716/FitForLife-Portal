import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_admin_login(username: str, password: str, admins: list[dict]) -> bool:
    """
    Validate admin credentials against the Admin sheet.
    Supports plain-text passwords (for simplicity) OR sha256 hashes.
    """
    hashed = hash_password(password)
    for admin in admins:
        if str(admin.get("Username", "")).strip().lower() == username.strip().lower():
            stored = str(admin.get("Password", "")).strip()
            # Accept both plain text and hashed passwords
            if stored == password or stored == hashed:
                return True
    return False
