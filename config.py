import os


class Config:
    ADMIN_EMAILS = set()

    _admin_env = os.environ.get('ADMIN_EMAILS', '')
    if _admin_env:
        ADMIN_EMAILS = {email.strip().lower() for email in _admin_env.split(',') if email.strip()}
