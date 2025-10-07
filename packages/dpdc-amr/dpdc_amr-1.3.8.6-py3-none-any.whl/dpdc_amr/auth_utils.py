# auth_utils.py
USERS = {
    "mbill":"mbill@321!",
    "admin": "token123",
    "user1": "token456"
}

def verify_user_token(username, token):
    if username not in USERS:
        return False, "User not found"
    if USERS[username] != token:
        return False, "Token invalid"
    return True, "Authenticated"
