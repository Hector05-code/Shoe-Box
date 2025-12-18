# Los atributos de configuración como el modo de depuración están aquí, HAY QUE AÑADIR más detalles
# a medida que continue el desarrollo

# Creación de una clase
class ConfiguracionDeDesarrollo():
    DEBUG = True
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "31087719"
    MYSQL_DB = "BdDShoeBox"

# Creando un diccionario para...
config = {
    "desarrollo":ConfiguracionDeDesarrollo
}