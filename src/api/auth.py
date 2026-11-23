import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
import bcrypt
from dotenv import load_dotenv

from src.infrastructure.database import get_db
from src.infrastructure.models import UsuarioModel
from src.application.schemas import UsuarioLogin, TokenResponse

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-apenas-para-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter(prefix="/auth", tags=["Autenticação"])

def criar_token_acesso(dados: dict) -> str:
    to_encode = dados.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiracao})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=TokenResponse)
def login(credenciais: UsuarioLogin, db:Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.email ==credenciais.email).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )
    senha_valida = bcrypt.checkpw(
        credenciais.senha.encode("utf-8"),
        usuario.senha_hash.encode("utf-8")
    )

    if not senha_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    token = criar_token_acesso(
        dados={"sub": str(usuario.id), "email": usuario.email, "perfil": usuario.perfil}
    )

    return TokenResponse(access_token=token, token_type="bearer")