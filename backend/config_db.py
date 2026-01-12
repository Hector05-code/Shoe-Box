from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlalchemy

DB_USER = "root"
DB_PASS = "31087719" 
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "bddshoebox"

URL_RAIZ = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
URL_BD = f"{URL_RAIZ}/{DB_NAME}"

def crear_bdd():
    # Creamos un motor temporal que solo conecta al servidor (sin buscar la BD específica)
    engine_raiz = create_engine(URL_RAIZ)
    
    try:
        with engine_raiz.connect() as conn:
            # Ejecutamos comando SQL directo para crearla
            conn.execute(sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            print(f"Base de datos '{DB_NAME}' verificada/creada correctamente.")
    except Exception as e:
        print(f"Error al intentar crear la base de datos: {e}")
    finally:
        engine_raiz.dispose()

# 1. Ejecutamos la función ANTES de crear el engine definitivo
crear_bdd()

# 2. Ahora sí, nos conectamos a la BD que acabamos de asegurar
engine = create_engine(URL_BD)
sesion_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
modelo_base_tabla = declarative_base()


# #Aqui esta la conexión a la base de datos
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# url_bdd_shoebox = "mysql+mysqlconnector://root:31087719@localhost/bddshoebox"
# engine = create_engine(url_bdd_shoebox, echo=True)

# sesion_local = sessionmaker(autoflush=False,autocommit=False,bind=engine)

# modelo_base_tabla = declarative_base()