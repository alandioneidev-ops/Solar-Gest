# Migração React + Node

A migração começou sem remover o Django atual. A nova arquitetura está organizada assim:

- `frontend/`: React + Vite
- `backend/`: Node.js + Express
- Django: permanece ativo durante a transição

## Executar o backend

```bash
cd backend
npm install
npm run dev
```

API: `http://localhost:3333`

Health check: `http://localhost:3333/api/health`

## Executar o frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

O frontend usa `VITE_API_URL` para localizar a API. Por padrão, usa `http://localhost:3333/api`.

## Próximas etapas

1. Migrar autenticação Django para JWT no backend Node.
2. Conectar Node ao PostgreSQL existente.
3. Migrar clientes, leads, CRM, projetos e financeiro para endpoints reais.
4. Transferir progressivamente cada tela Django para React.
5. Desativar o Django somente após a validação dos módulos migrados.
