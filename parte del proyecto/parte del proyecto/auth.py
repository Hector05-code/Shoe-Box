
from flask import Blueprint, request, jsonify
from database import get_connection

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    usuario = data.get("usuario")
    contraseña = data.get("contraseña")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id_Empleado, Nombre, Funcion FROM empleado WHERE Usuario=%s AND Contraseña=%s",
        (usuario, contraseña)
    )

    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    return jsonify({
        "mensaje": "Login exitoso",
        "id": user["id_Empleado"],
        "nombre": user["Nombre"],
        "rol": user["Funcion"]
    })
