#Aqui esta la conexión a la base de datos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

url_bdd_shoebox = "mysql+mysqlconnector://root:31087719@localhost/Dump251217"
engine = create_engine(url_bdd_shoebox, echo=True)

sesion_local = sessionmaker(autoflush=False,autocommit=False,bind=engine)

modelo_base_tabla = declarative_base