from src.infrastructure.database import engine, Base
from src.infrastructure.models import UsuarioModel

try:
    #Tenta conectar e criar as tabelas no MySQL automaticamente
    Base.metadata.create_all(bind=engine)
    print("SUCESSO: Conexão com o MySQL estabelecida e tabelas criadas!")
except Exception as e:
    print(f"ERRO DE CONEXÃO: {e}")