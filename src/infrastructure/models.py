from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from src.infrastructure.database import Base

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(Enum("CLIENTE", "GERENTE", "COZINHA", "ADMIN", name="perfil_enum"),default="CLIENTE", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UnidadeModel(Base):
    __tablename__= "unidades"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(120), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    endereco = Column(String(200), nullable=True)
    ativa = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class ProdutoModel(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(String(255), nullable=True)
    preco = Column(Float, nullable=False)
    categoria = Column(String(60), nullable=False)
    disponivel = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PedidoModel(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    canal = Column(String(30), nullable=False, default="APP")
    valor_total = Column(Float, nullable=False, default=0.0)
    status = Column(String(30), default="ABERTO", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PromocaoModel(Base):
    __tablename__ = "promocoes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    desconto_percentual = Column(Float, nullable=False)
    ativa = Column(Boolean, default=True, nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)

class ItemPedidoModel(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)
    preco_unitario = Column(Float, nullable=False)

# Criação das outras tabelas (Unidades, Produtos, Pedidos, etc.) em seguida.