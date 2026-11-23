from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.infrastructure.database import get_db
from src.infrastructure.models import ProdutoModel
from src.application.schemas import (
    ProdutoCreate,
    ProdutoResponse,
    ProdutoUpdate,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto_data: ProdutoCreate, db: Session = Depends(get_db)):
    if produto_data.preco <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O preço do produto deve ser maior que zero.",
        )

    novo_produto = ProdutoModel(
        nome=produto_data.nome,
        descricao=produto_data.descricao,
        preco=produto_data.preco,
        categoria=produto_data.categoria,
        disponivel=produto_data.disponivel if produto_data.disponivel is not None else True,
    )

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)

    return novo_produto


@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(ProdutoModel).all()


@router.patch("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    produto_data: ProdutoUpdate,
    db: Session = Depends(get_db),
):
    produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    dados_atualizacao = produto_data.model_dump(exclude_unset=True)

    if "preco" in dados_atualizacao and dados_atualizacao["preco"] is not None:
        if dados_atualizacao["preco"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O preço do produto deve ser maior que zero.",
            )

    for campo, valor in dados_atualizacao.items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)

    return produto