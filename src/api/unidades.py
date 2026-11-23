from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.models import UnidadeModel
from src.application.schemas import UnidadeCreate, UnidadeResponse

router = APIRouter(prefix="/unidades", tags=["Unidades"])
@router.post("/", response_model=UnidadeResponse, status_code=status.HTTP_201_CREATED)
def criar_unidade(unidade: UnidadeCreate, db: Session = Depends(get_db)):
    nova_unidade = UnidadeModel(
        nome=unidade.nome,
        cidade=unidade.cidade,
        estado=unidade.estado,
        endereco=unidade.endereco,
        ativa=unidade.ativa
    )

    db.add(nova_unidade)
    db.commit()
    db.refresh(nova_unidade)

    return nova_unidade

@router.get("/", response_model=List[UnidadeResponse])
def listar_unidades(db: Session = Depends(get_db)):
    unidades = db.query(UnidadeModel).all()
    return unidades
