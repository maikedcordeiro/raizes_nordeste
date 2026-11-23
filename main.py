from fastapi import FastAPI
from src.api.usuarios import router as usuarios_router
from src.api.auth import router as auth_router
from src.api.unidades import router as unidades_router
from src.api.produtos import router as produtos_router
from src.api.pedidos import router as pedidos_router
from src.api.pagamentos import router as pagamentos_router


app = FastAPI(
    title="Raízes do Nordeste API",
    version="1.0.0",
    description="API do sistema para a Trilha Back-End"
)

#Registra as rotas da aplicação
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(unidades_router)
app.include_router(produtos_router)
app.include_router(pedidos_router)
app.include_router(pagamentos_router)

@app.get("/")
def raiz():
    return{"mensagem": "Bem-vindo(a) à API Raízes do Nordeste! Servidor rodando com sucesso"}