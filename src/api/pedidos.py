from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.infrastructure.database import get_db
from src.infrastructure.models import (
    UsuarioModel,
    UnidadeModel,
    ProdutoModel,
    PedidoModel,
    ItemPedidoModel,
)
from src.application.schemas import (
    PedidoCreate,
    PedidoResponse,
    ItemPedidoResponse,
    PedidoStatusUpdate,
)

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def criar_pedido(pedido_data: PedidoCreate, db: Session = Depends(get_db)):
    if not pedido_data.itens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O pedido deve conter pelo menos um item.",
        )

    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == pedido_data.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    unidade = db.query(UnidadeModel).filter(UnidadeModel.id == pedido_data.unidade_id).first()
    if not unidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada.",
        )

    valor_total = 0.0
    itens_preparados = []

    for item in pedido_data.itens:
        if item.quantidade <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quantidade inválida para o produto ID {item.produto_id}. Informe um valor maior que zero.",
            )

        produto = db.query(ProdutoModel).filter(ProdutoModel.id == item.produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto ID {item.produto_id} não encontrado.",
            )

        # Regra de negócio: se faltar ingrediente / prato indisponível, bloqueia o pedido
        if not produto.disponivel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O prato '{produto.nome}' está indisponível no momento por falta de ingredientes.",
            )

        preco_unitario = float(produto.preco)
        valor_total += preco_unitario * item.quantidade
        itens_preparados.append({
            "produto_id": produto.id,
            "quantidade": item.quantidade,
            "preco_unitario": preco_unitario,
        })

    try:
        novo_pedido = PedidoModel(
            usuario_id=pedido_data.usuario_id,
            unidade_id=pedido_data.unidade_id,
            status="ABERTO",
            valor_total=round(valor_total, 2),
        )
        db.add(novo_pedido)
        db.commit()
        db.refresh(novo_pedido)

        itens_criados = []
        for item_info in itens_preparados:
            novo_item = ItemPedidoModel(
                pedido_id=novo_pedido.id,
                produto_id=item_info["produto_id"],
                quantidade=item_info["quantidade"],
                preco_unitario=item_info["preco_unitario"],
            )
            db.add(novo_item)
            db.commit()
            db.refresh(novo_item)
            itens_criados.append(
                ItemPedidoResponse(
                    id=novo_item.id,
                    produto_id=novo_item.produto_id,
                    quantidade=novo_item.quantidade,
                    preco_unitario=novo_item.preco_unitario,
                )
            )

        return PedidoResponse(
            id=novo_pedido.id,
            usuario_id=novo_pedido.usuario_id,
            unidade_id=novo_pedido.unidade_id,
            canal=getattr(novo_pedido, "canal", None) or canal_normalizado,
            status=novo_pedido.status,
            valor_total=novo_pedido.valor_total,
            itens=itens_criados,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{type(e).__name__}: {e}",
        )


@router.get("/", response_model=List[PedidoResponse])
def listar_pedidos(db: Session = Depends(get_db)):
    pedidos = db.query(PedidoModel).all()
    resultado = []

    for pedido in pedidos:
        itens_db = db.query(ItemPedidoModel).filter(ItemPedidoModel.pedido_id == pedido.id).all()
        itens_resp = [
            ItemPedidoResponse(
                id=i.id,
                produto_id=i.produto_id,
                quantidade=i.quantidade,
                preco_unitario=i.preco_unitario,
            )
            for i in itens_db
        ]
        resultado.append(
            PedidoResponse(
                id=pedido.id,
                usuario_id=pedido.usuario_id,
                unidade_id=pedido.unidade_id,
                canal=getattr(pedido, "canal", None) or "APP",
                status=pedido.status,
                valor_total=pedido.valor_total,
                itens=itens_resp,
            )
        )

    return resultado


@router.patch("/{pedido_id}/status", response_model=PedidoResponse)
def atualizar_status_pedido(
    pedido_id: int,
    status_data: PedidoStatusUpdate,
    db: Session = Depends(get_db),
):
    status_validos = {"ABERTO", "EM_PREPARO", "FINALIZADO", "CANCELADO"}
    novo_status = (status_data.status or "").strip().upper()

    if novo_status not in status_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status '{status_data.status}' inválido. Use um destes: {', '.join(sorted(status_validos))}.",
        )

    pedido = db.query(PedidoModel).filter(PedidoModel.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )

    if pedido.status in {"FINALIZADO", "CANCELADO"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível alterar o status de um pedido já {pedido.status.lower()}.",
        )

    pedido.status = novo_status
    db.commit()
    db.refresh(pedido)

    itens_db = db.query(ItemPedidoModel).filter(ItemPedidoModel.pedido_id == pedido.id).all()
    itens_resp = [
        ItemPedidoResponse(
            id=i.id,
            produto_id=i.produto_id,
            quantidade=i.quantidade,
            preco_unitario=i.preco_unitario,
        )
        for i in itens_db
    ]

    return PedidoResponse(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        unidade_id=pedido.unidade_id,
        canal=getattr(pedido, "canal", None) or "APP",
        status=pedido.status,
        valor_total=pedido.valor_total,
        itens=itens_resp,
    )