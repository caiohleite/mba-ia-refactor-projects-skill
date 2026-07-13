# Checklist de Validação

Use este guia no final da Fase 3 e sempre que uma etapa de refatoração mudar inicialização, rotas, banco ou contratos HTTP.

## Preparação

- Identificar comando de instalação: `pip install -r requirements.txt`, `npm install`, `poetry install`, etc.
- Identificar comando de seed/migração quando existir.
- Identificar comando de inicialização: `python app.py`, `flask run`, `npm start`, `node src/app.js`.
- Identificar porta e base URL.
- Coletar endpoints a partir de decorators, `add_url_rule`, blueprints, `app.get/post`, routers ou arquivo `api.http`.

## Validação de Inicialização

Executar o comando de inicialização quando seguro. Se o processo ficar em primeiro plano, usar timeout ou iniciar em segundo plano de forma controlada. Validar:

- processo inicia sem exceção;
- porta esperada abre;
- logs não mostram rastreamento de pilha;
- banco inicializa ou conecta.

Se não for possível executar por dependência, rede, porta ocupada ou sandbox, documentar o motivo e o comando exato que deveria ser rodado.

## Testes de Fumaça de Endpoints

Testar pelo menos:

- saúde/raiz;
- listagem principal;
- criação simples quando houver payload seguro;
- busca por ID quando seed existir;
- fluxo de domínio crítico, como checkout, pedido ou task;
- endpoint de relatório se existir.

Preservar métodos, caminhos e formatos principais. Se o projeto possuir `api.http`, usá-lo como fonte de contratos.

## Regressão Arquitetural

Conferir:

- nenhum segredo fixado no código permanece em respostas ou logs;
- nenhuma consulta concatenada com entrada externa permanece nos fluxos alterados;
- routes/views não acessam banco diretamente, salvo exceção justificada;
- controllers não concentram loops de relatório ou regra extensa;
- models não retornam senha/hash/token em DTO público;
- tratador de erros central está registrado;
- imports antigos e arquivos mortos não quebram a inicialização.

## Checklist Obrigatório do README

### Fase 1 - Análise

- [ ] Linguagem detectada corretamente.
- [ ] Framework detectado corretamente.
- [ ] Domínio da aplicação descrito corretamente.
- [ ] Número de arquivos analisados condiz com a realidade.

### Fase 2 - Auditoria

- [ ] Relatório segue o modelo definido nos arquivos de referência.
- [ ] Cada achado tem arquivo e linhas exatos quando aplicável.
- [ ] Achados ordenados por severidade (`CRITICAL` -> `LOW`).
- [ ] Mínimo de 5 achados identificados quando houver evidência suficiente.
- [ ] Detecção de APIs obsoletas incluída quando aplicável.
- [ ] Skill pausou e pediu confirmação antes da Fase 3.

### Fase 3 - Refatoração

- [ ] Estrutura de diretórios segue padrão MVC.
- [ ] Configuração extraída para módulo de configuração, sem segredo fixado no código.
- [ ] Models ou repositories abstraem dados.
- [ ] Views/Routes ficam separadas para visualização ou roteamento.
- [ ] Controllers concentram o fluxo da aplicação.
- [ ] Tratamento de erros centralizado.
- [ ] Ponto de entrada claro.
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
