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
    engine_raiz = create_engine(URL_RAIZ)
  
    try:
        with engine_raiz.connect() as conn:
            conn.execute(sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            print(f"Base de datos '{DB_NAME}' verificada/creada correctamente.")
    except Exception as e:
        print(f"Error al intentar crear la base de datos: {e}")
    finally:
        engine_raiz.dispose()

crear_bdd()

engine = create_engine(URL_BD)
sesion_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
modelo_base_tabla = declarative_base()