# Para esta api el primer paso es crear un entorno virtual en la terminal
# Luego instalar flask y flaskmysql en el entorno virtual
# Despues importamos flask en el archivo
from flask import Flask,jsonify,request

# Importamos MySQLdb para realizar la conexión
from flask_mysqldb import MySQL

# Importamos archivo de configuración
from config_api import config

# Creamos la aplicación
app = Flask(__name__)

# Dirección general
conexion = MySQL(app)

#Establecer endpoint
@app.route('/producto', methods=["GET"])

def listar_productos():
    try:
        cursor=conexion.connection.cursor()
        sql="SELECT id_Producto, Nombre_Producto, Marca, Categoria, id_TipoProducto, precio FROM producto"
        cursor.execute(sql)
        datos=cursor.fetchall()
        productos=[]
        for fila in datos:
            producto={"id_Producto":fila[0], "Nombre_Producto":fila[1], "Marca":fila[2], "Categoria":fila[3], "id_TipoProducto":fila[4], "precio":fila[5]}
            productos.append(producto)
        return jsonify({"productos":productos,"mensaje":"Estos son todos los productos"})
    except Exception as te_equivocaste:
        return jsonify({"mensaje":f"El sistema ha fallado. El error es: {te_equivocaste}"})

@app.route('/producto/<id_Producto>', methods=["GET"])
def leer_producto(id_Producto):
    try:
        cursor=conexion.connection.cursor()
        sql="SELECT id_Producto, Nombre_Producto, Marca, Categoria, id_TipoProducto, precio FROM producto WHERE id_Producto = '{0}'".format(id_Producto)
        cursor.execute(sql)
        datos=cursor.fetchone()
        if datos!=None:
            producto={"id_Producto":datos[0], "Nombre_Producto":datos[1], "Marca":datos[2], "Categoria":datos[3], "id_TipoProducto":datos[4], "precio":datos[5]}
            return jsonify({"producto":producto, "mensaje":"Producto encontrado"})
        else:
            return jsonify({"mensaje":"Producto no encontrado"})
    except Exception as te_equivocaste:
        return jsonify({"mensaje":f"El sistema ha fallado. El error es: {te_equivocaste}"})
    
@app.route('/producto', methods=["POST"])
def registrar_producto():
    try:
        #print(request.json)
        cursor=conexion.connection.cursor()
        sql="""INSERT INTO producto (id_Producto, Nombre_Producto, Marca, Categoria, id_TipoProducto, precio) 
        VALUES ("{0}","{1}","{2}","{3}","{4}",{5})""".format(request.json["id_Producto"],
                                                            request.json["Nombre_Producto"],request.json["Marca"],request.json["Categoria"],request.json["id_TipoProducto"],request.json["precio"],)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({"mensaje":"Producto registrado"})
    except Exception as te_equivocaste:
        return jsonify({"mensaje":f"El sistema ha fallado. El error es: {te_equivocaste}"})
    
@app.route('/producto/<id_Producto>', methods=["DELETE"])
def eliminar_producto(id_Producto):
    try:
        cursor=conexion.connection.cursor()
        sql="DELETE FROM producto WHERE id_Producto = '{0}'".format(id_Producto)
        conexion.connection.commit()
        return jsonify({"mensaje":"Producto eliminado"})
    except Exception as te_equivocaste:
        return jsonify({"mensaje":f"El sistema ha fallado. El error es: {te_equivocaste}"})
    
@app.route('/producto/<id_Producto>', methods=["PUT"])
def actualizar_producto(id_Producto):
    try:
        cursor=conexion.connection.cursor()
        sql="""UPDATE producto SET Nombre_Producto = '{0}', Marca = '{1}', Categoria = '{2}', id_TipoProducto = '{3}', precio = {4} 
        WHERE id_Producto = '{5}' """.format(request.json["Nombre_Producto"],request.json["Marca"],request.json["Categoria"],request.json["id_TipoProducto"],request.json["precio"],id_Producto)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({"mensaje":"Producto actualizado"})
    except Exception as te_equivocaste:
        return jsonify({"mensaje":f"El sistema ha fallado. El error es: {te_equivocaste}"})
    
def pagina_no_encontrada(error):
    return "<h1> La página que buscas no existe </h1>",404

# El if name=main ejecuta la aplicación
if __name__ == "__main__":
    app.config.from_object(config["desarrollo"]) #Importe de la configuración desde config_api.py
    app.register_error_handler(404,pagina_no_encontrada)
    app.run()