from dns.resolver import NoMetaqueries
from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import List, Optional

# Schema para receber os dados quando um usuário for se cadastrar
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: Optional[str] = "CLIENTE" #Se não mandar, o padrão é CLIENTE

# Schema para definir o que será retornado para o cliente (sem expor a senha!)
class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str

    class Config:
        from_attributes = True #Permite ler dados diretamente do modelo do SQLAlchemy

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str= "bearer"

class UnidadeCreate(BaseModel):
    nome: str
    cidade: str
    estado: str
    endereco: Optional[str] = None
    ativa: Optional[bool] = True

class UnidadeResponse(BaseModel):
    id: int
    nome: str
    cidade: str
    estado: str
    endereco: Optional[str] = None
    ativa: bool

    class Config:
        from_attributes = True

class ProdutoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    categoria: str
    disponivel: Optional[bool] = True

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    preco: float
    categoria: str
    disponivel: bool

    class Config:
        from_attributes =True

class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int = 1

class PedidoCreate(BaseModel):
    usuario_id:int
    unidade_id: int
    canal: str = "APP"
    itens: List[ItemPedidoCreate]

class ItemPedidoResponse(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: float

    class Config:
        from_attributes = True

class PedidoResponse(BaseModel):
    id: int
    usuario_id: int
    unidade_id: int
    canal: str
    status: str
    valor_total:float
    itens: List[ItemPedidoResponse]

    class Config:
        from_attributes = True

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[float] = None
    categoria: Optional[str] = None
    disponivel: Optional[bool] = None

class PedidoStatusUpdate(BaseModel):
    status: str

class PagamentoMockCreate(BaseModel):
    metodo: str = "PIX"

class PagamentoMockResponse(BaseModel):
    pedido_id: int
    valor_cobrado: float
    metodo: str
    status_pagamento: str
    codigo_transacao: str
    status_pedido: str

class PromocaoCreate(BaseModel):
    titulo: str
    descricao: str | None = None
    desconto_percentual: float
    ativa: bool = True
    produto_id: int | None = None


class PromocaoUpdate(BaseModel):
    ativa: bool


class PromocaoResponse(BaseModel):
    id: int
    titulo: str
    descricao: str | None
    desconto_percentual: float
    ativa: bool
    produto_id: int | None

    class Config:
        from_attributes = True