import 'dotenv/config';
import cors from 'cors';
import express from 'express';
import helmet from 'helmet';
import morgan from 'morgan';

const app = express();
const port = Number(process.env.PORT || 3333);

app.use(helmet());
app.use(cors({ origin: process.env.FRONTEND_URL || 'http://localhost:5173' }));
app.use(express.json());
app.use(morgan('tiny'));

app.get('/api/health', (_request, response) => {
  response.json({ service: 'solar-gest-api', status: 'ok' });
});

app.get('/api/dashboard', (_request, response) => {
  response.json({
    clientes: 0,
    leads: 0,
    projetos: 0,
    atendimentosAbertos: 0,
    migratedFrom: 'django',
  });
});

app.use((_request, response) => {
  response.status(404).json({ error: 'Rota não encontrada' });
});

app.listen(port, () => {
  console.log(`Solar Gest API running on http://localhost:${port}`);
});
