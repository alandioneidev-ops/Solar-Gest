# Hospedagem da demonstracao

O projeto esta preparado para deploy no Render.

## Publicar

1. Acesse https://render.com e entre com GitHub.
2. Clique em **New > Blueprint**.
3. Selecione o repositorio `alandioneidev-ops/Solar-Gest`.
4. Confirme o arquivo `render.yaml`.
5. Aguarde o deploy do servico web e do PostgreSQL.

O Render vai executar automaticamente:

- instalacao de `requirements.txt`;
- migracoes do banco;
- coleta de arquivos estaticos;
- criacao do usuario demo;
- inicializacao do Gunicorn.

## Acesso demo

```text
Usuario: demo
Senha: SolarGestDemo123!
```

A senha pode ser alterada pela variavel `DEMO_PASSWORD` no Render.

O endereco final sera parecido com:

```text
https://solar-gest-demo.onrender.com/
```

O plano gratuito pode adormecer depois de um periodo sem acesso. Para uma apresentacao ao cliente, abra o link alguns minutos antes.
