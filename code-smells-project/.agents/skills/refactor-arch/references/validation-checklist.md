# Checklist de Validação

Use este guia no final da Fase 3 e sempre que uma etapa de refatoração mudar bootstrap, rotas, banco ou contratos HTTP.

## Preparação

- Identificar comando de instalação: `pip install -r requirements.txt`, `npm install`, `poetry install`, etc.
- Identificar comando de seed/migration quando existir.
- Identificar comando de boot: `python app.py`, `flask run`, `npm start`, `node src/app.js`.
- Identificar porta e base URL.
- Coletar endpoints a partir de decorators, `add_url_rule`, blueprints, `app.get/post`, routers ou arquivo `api.http`.

## Validação de Boot

Executar o comando de boot quando seguro. Se o processo ficar em primeiro plano, usar timeout ou iniciar em background de forma controlada. Validar:

- processo inicia sem exceção;
- porta esperada abre;
- logs não mostram stack trace;
- banco inicializa ou conecta.

Se não for possível executar por dependência, rede, porta ocupada ou sandbox, documentar o motivo e o comando exato que deveria ser rodado.

## Smoke Tests de Endpoints

Testar pelo menos:

- health/root;
- listagem principal;
- criação simples quando houver payload seguro;
- busca por ID quando seed existir;
- fluxo de domínio crítico, como checkout, pedido ou task;
- endpoint de relatório se existir.

Preservar métodos, paths e formatos principais. Se o projeto possuir `api.http`, usá-lo como fonte de contratos.

## Regressão Arquitetural

Conferir:

- nenhum segredo hardcoded permanece em respostas ou logs;
- nenhuma query concatenada com input externo permanece nos fluxos alterados;
- routes/views não acessam banco diretamente, salvo exceção justificada;
- controllers não concentram loops de relatório ou regra extensa;
- models não retornam senha/hash/token em DTO público;
- error handler central está registrado;
- imports antigos e arquivos mortos não quebram boot.

## Checklist Obrigatório do README

### Fase 1 - Análise

- [ ] Linguagem detectada corretamente.
- [ ] Framework detectado corretamente.
- [ ] Domínio da aplicação descrito corretamente.
- [ ] Número de arquivos analisados condiz com a realidade.

### Fase 2 - Auditoria

- [ ] Relatório segue o template definido nos arquivos de referência.
- [ ] Cada achado tem arquivo e linhas exatos quando aplicável.
- [ ] Achados ordenados por severidade (`CRITICAL` -> `LOW`).
- [ ] Mínimo de 5 achados identificados quando houver evidência suficiente.
- [ ] Detecção de APIs deprecated incluída quando aplicável.
- [ ] Skill pausou e pediu confirmação antes da Fase 3.

### Fase 3 - Refatoração

- [ ] Estrutura de diretórios segue padrão MVC.
- [ ] Configuração extraída para módulo de config, sem segredo hardcoded.
- [ ] Models ou repositories abstraem dados.
- [ ] Views/Routes ficam separadas para visualização ou roteamento.
- [ ] Controllers concentram o fluxo da aplicação.
- [ ] Error handling centralizado.
- [ ] Entry point claro.
- [ ] Aplicação inicia sem erros.
- [ ] Endpoints originais respondem corretamente.

## Atualização do Estado

Ao final da validação:

- atualizar `STATE.md` com comandos executados e resultados;
- marcar tarefas `COMPLETED`, `FAILED`, `SKIPPED` ou `BLOCKED`;
- definir `Status de Execução` como `COMPLETED`, `PARTIAL` ou `BLOCKED`;
- salvar `validation-report.md`.

## Relatório Final

Registrar:

- comandos executados;
- endpoints testados e status;
- testes automatizados executados;
- validações não executadas e motivo;
- achados tratados, parcialmente tratados ou remanescentes.
