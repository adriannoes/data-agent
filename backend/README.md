# Backend - AI DataLab

Backend Python com FastAPI e LangGraph para processamento de mensagens e análise de dados.

## Configuração

1. Instale as dependências:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY
```

3. Adicione arquivos CSV na pasta `data/` para análise.

## Execução

```bash
# A partir da pasta backend/
python main.py

# Ou usando uvicorn diretamente
uvicorn main:app --reload --port 8000
```

O servidor estará disponível em `http://localhost:8000`

## Estrutura

- `main.py` - FastAPI app com endpoints
- `agent/` - Módulo LangGraph com grafo e nós
- `tools/` - Ferramentas Python para análise de dados
- `data/` - Arquivos CSV para análise

## Endpoints

- `POST /api/chat` - Processa mensagens do chat
- `GET /api/stream/{session_id}` - SSE para atualização do preview
- `GET /api/health` - Health check

