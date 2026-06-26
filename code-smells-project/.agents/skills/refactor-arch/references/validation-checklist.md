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

## Checklist Obrigatorio Do README

### Fase 1 - Analise

- [ ] Linguagem detectada corretamente.
- [ ] Framework detectado corretamente.
- [ ] Dominio da aplicacao descrito corretamente.
- [ ] Numero de arquivos analisados condiz com a realidade.

### Fase 2 - Auditoria

- [ ] Relatorio segue o template definido nos arquivos de referencia.
- [ ] Cada finding tem arquivo e linhas exatos quando aplicavel.
- [ ] Findings ordenados por severidade (`CRITICAL` -> `LOW`).
- [ ] Minimo de 5 findings identificados quando houver evidencia suficiente.
- [ ] Deteccao de APIs deprecated incluida quando aplicavel.
- [ ] Skill pausou e pediu confirmacao antes da Fase 3.

### Fase 3 - Refatoracao

- [ ] Estrutura de diretorios segue padrao MVC.
- [ ] Configuracao extraida para modulo de config, sem segredo hardcoded.
- [ ] Models ou repositories abstraem dados.
- [ ] Views/Routes ficam separadas para visualizacao ou roteamento.
- [ ] Controllers concentram o fluxo da aplicacao.
- [ ] Error handling centralizado.
- [ ] Entry point claro.
- [ ] Aplicacao inicia sem erros.
- [ ] Endpoints originais respondem corretamente.

## Atualizacao Do Estado

Ao final da validacao:

- atualizar `STATE.md` com comandos executados e resultados;
- marcar tarefas `COMPLETED`, `FAILED`, `SKIPPED` ou `BLOCKED`;
- definir `Execution Status` como `COMPLETED`, `PARTIAL` ou `BLOCKED`;
- salvar `validation-report.md`.

## Relatorio Final

Registrar:

- comandos executados;
- endpoints testados e status;
- testes automatizados executados;
- validacoes nao executadas e motivo;
- findings tratados, parcialmente tratados ou remanescentes.
