
from flask import Flask, jsonify
from auth import auth
from decorators import role_required

app = Flask(__name__)
app.register_blueprint(auth)

@app.route("/gerente")
@role_required(["Gerente"])
def gerente():
    return jsonify({"mensaje": "Acceso gerente"})

@app.route("/caja")
@role_required(["Cajero", "Gerente"])
def caja():
    return jsonify({"mensaje": "Acceso caja"})

@app.route("/ventas")
@role_required(["Vendedor", "Gerente"])
def ventas():
    return jsonify({"mensaje": "Acceso ventas"})

if __name__ == "__main__":
    app.run(debug=True)
