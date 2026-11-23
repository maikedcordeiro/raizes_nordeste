from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt

from src.infrastructure.database import get_db
from src.infrastructure.models import UsuarioModel
from src.application.schemas import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Verifica se o e-mail já está cadastrado no banco
    usuario_existente = db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado no sistema."
        )

    # 2. Criptografa a senha antes de salvar
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(usuario.senha.encode('utf-8'), salt).decode('utf-8')

    # 3.Cria o objeto do modelo do banco
    novo_usuario = UsuarioModel(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash,
        perfil=usuario.perfil
    )

    # 4. Salva no MySQL
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario