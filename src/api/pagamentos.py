import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.models import PedidoModel
from src.application.schemas import PagamentoMockCreate, PagamentoMockResponse

router = APIRouter(prefix="/pedidos", tags=["Pagamentos (Mock)"])

METODOS_PAGAMENTO = {"PIX", "CARTAO_CREDITO", "CARTAO_DEBITO", "DINHEIRO"}


@router.post("/{pedido_id}/pagamento", response_model=PagamentoMockResponse)
def simular_pagamento_pedido(
    pedido_id: int,
    pagamento_data: PagamentoMockCreate,
    db: Session = Depends(get_db),
):
    metodo_normalizado = (pagamento_data.metodo or "").strip().upper()
    if metodo_normalizado not in METODOS_PAGAMENTO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Método '{pagamento_data.metodo}' inválido. Use um destes: {', '.join(sorted(METODOS_PAGAMENTO))}.",
        )

    pedido = db.query(PedidoModel).filter(PedidoModel.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )

    if pedido.status == "CANCELADO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível simular pagamento para um pedido cancelado.",
        )

    if pedido.status == "ABERTO":
        pedido.status = "EM_PREPARO"
        db.commit()
        db.refresh(pedido)

    codigo_mock = f"MOCK-{uuid.uuid4().hex[:10].upper()}"

    return PagamentoMockResponse(
        pedido_id=pedido.id,
        valor_cobrado=pedido.valor_total,
        metodo=metodo_normalizado,
        status_pagamento="APROVADO",
        codigo_transacao=codigo_mock,
        status_pedido=pedido.status,
    )