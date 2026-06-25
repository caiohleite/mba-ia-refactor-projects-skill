# Checklist De Validacao

Use este guia no final da Fase 3 e sempre que uma etapa de refatoracao mudar bootstrap, rotas, banco ou contratos HTTP.

## Preparacao

- Identificar comando de instalacao: `pip install -r requirements.txt`, `npm install`, `poetry install`, etc.
- Identificar comando de seed/migration quando existir.
- Identificar comando de boot: `python app.py`, `flask run`, `npm start`, `node src/app.js`.
- Identificar porta e base URL.
- Coletar endpoints a partir de decorators, `add_url_rule`, blueprints, `app.get/post`, routers ou arquivo `api.http`.

## Validacao De Boot

Executar o comando de boot quando seguro. Se o processo ficar em primeiro plano, usar timeout ou iniciar em background de forma controlada. Validar:

- processo inicia sem excecao;
- porta esperada abre;
- logs nao mostram stack trace;
- banco inicializa ou conecta.

Se nao for possivel executar por dependencia, rede, porta ocupada ou sandbox, documentar o motivo e o comando exato que deveria ser rodado.

## Smoke Tests De Endpoints

Testar pelo menos:

- health/root;
- listagem principal;
- criacao simples quando houver payload seguro;
- busca por ID quando seed existir;
- fluxo de dominio critico, como checkout, pedido ou task;
- endpoint de relatorio se existir.

Preservar metodos, paths e formatos principais. Se o projeto possuir `api.http`, usa-lo como fonte de contratos.

## Regressao Arquitetural

Conferir:

- nenhum segredo hardcoded permanece em respostas ou logs;
- nenhuma query concatenada com input externo permanece nos fluxos alterados;
- routes/views nao acessam banco diretamente, salvo excecao justificada;
- controllers nao concentram loops de relatorio ou regra extensa;
- models nao retornam senha/hash/token em DTO publico;
- error handler central esta registrado;
- imports antigos e arquivos mortos nao quebram boot.

## Relatorio Final

Registrar:

- comandos executados;
- endpoints testados e status;
- testes automatizados executados;
- validacoes nao executadas e motivo;
- findings tratados, parcialmente tratados ou remanescentes.
