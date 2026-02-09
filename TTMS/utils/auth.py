from functools import wraps
from flask import session, redirect

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "role" not in session:
                return redirect("/")
            if role and session["role"] != role:
                return redirect("/")
            return f(*args, **kwargs)
        return wrapper
    return decorator