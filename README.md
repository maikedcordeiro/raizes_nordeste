# Raízes do Nordeste — Back-end API

API back-end em **Python** e **FastAPI** com **SQLAlchemy** e **MySQL** para gestão de usuários, unidades, produtos, pedidos e simulação de pagamento.

## Stack
- Python 3.13
- FastAPI
- SQLAlchemy, PyMySQL e MySQL
- Pydantic
- Swagger UI (`/docs`)

## Estrutura do Projeto
- `main.py` — Inicialização da API e registro das rotas.
- `test_connection.py` — Teste de conexão com o MySQL.
- `src/api/` — Endpoints (autenticação, usuários, unidades, produtos, pedidos e pagamentos).
- `src/application/` — Schemas Pydantic e regras de aplicação.
- `src/infrastructure/` — Conexão com o banco e modelos ORM.
- `.env.example` — Modelo das variáveis de ambiente.

## Configuração do Ambiente
1. Crie e ative o ambiente virtual:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   
2. Instale as dependências:
    ```bash
   pip install -r requirements.txt
   
3. Copie .env.example para .env e preencha suas credenciais(`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `SECRET_KEY`).

## Executando a Aplicação
1. Com o MySQL ativo e o `.env` configurado, inicie o servidor:
    ```bash
    uvicorn main:app --reload

2. Acesse a documentação interativa em: http://127.0.0.1:8000/docs
## Endpoints e Regras Principais
- Usuários e Autenticação: cadastro e login.
- Unidades: cadastro e listagem.
- Produtos: cadastro, listagem e atualização, com controle de disponibilidade (disponivel).
- Pedidos: criação com validação de usuário, unidade, canal (APP, TOTEM, INTERNET, BALCAO, WHATSAPP) e itens, além de consulta e atualização de status (ABERTO, EM_PREPARO, FINALIZADO, CANCELADO).
- Pagamento (Mock): POST /pedidos/{pedido_id}/pagamento — simula pagamento (PIX, CARTAO_CREDITO, CARTAO_DEBITO, DINHEIRO), gera código de transação (MOCK-...) e avança o status do pedido.