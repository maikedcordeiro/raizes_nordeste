from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.models import PromocaoModel, ProdutoModel
from src.application.schemas import PromocaoCreate, PromocaoUpdate, PromocaoResponse

router = APIRouter(prefix="/promocoes", tags=["Promoções"])


@router.post("/", response_model=PromocaoResponse, status_code=status.HTTP_201_CREATED)
def criar_promocao(promocao: PromocaoCreate, db: Session = Depends(get_db)):
    if promocao.desconto_percentual <= 0 or promocao.desconto_percentual > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O desconto percentual deve ser maior que 0 e menor ou igual a 100.",
        )

    if promocao.produto_id is not None:
        produto = db.query(ProdutoModel).filter(ProdutoModel.id == promocao.produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto vinculado à promoção não encontrado.",
            )

    nova_promocao = PromocaoModel(
        titulo=promocao.titulo,
        descricao=promocao.descricao,
        desconto_percentual=promocao.desconto_percentual,
        ativa=promocao.ativa,
        produto_id=promocao.produto_id,
    )
    db.add(nova_promocao)
    db.commit()
    db.refresh(nova_promocao)
    return nova_promocao


@router.get("/", response_model=list[PromocaoResponse])
def listar_promocoes(apenas_ativas: bool = False, db: Session = Depends(get_db)):
    query = db.query(PromocaoModel)
    if apenas_ativas:
        query = query.filter(PromocaoModel.ativa.is_(True))
    return query.all()


@router.patch("/{promocao_id}", response_model=PromocaoResponse)
def atualizar_status_promocao(
    promocao_id: int,
    dados: PromocaoUpdate,
    db: Session = Depends(get_db),
):
    promocao = db.query(PromocaoModel).filter(PromocaoModel.id == promocao_id).first()
    if not promocao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoção não encontrada.",
        )

    promocao.ativa = dados.ativa
    db.commit()
    db.refresh(promocao)
    return promocao