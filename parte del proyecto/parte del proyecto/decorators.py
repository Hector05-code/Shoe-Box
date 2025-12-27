
from functools import wraps
from flask import request, jsonify

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            rol = request.headers.get("Rol")
            if rol not in roles:
                return jsonify({"error": "Acceso no autorizado"}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator
