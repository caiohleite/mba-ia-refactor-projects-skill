# Entregável — Skill `refactor-arch`

Este documento apresenta o processo e as evidências de construção, execução e validação da skill `refactor-arch` nos três projetos legados do desafio. A implementação foi realizada para **OpenAI Codex**, com a skill instalada em `.agents/skills/refactor-arch/` e os agentes personalizados configurados em `.codex/agents/` dentro de cada projeto.

Os achados da seção **A) Análise Manual** descrevem o estado legado anterior à refatoração. As seções seguintes documentam a implementação da skill, as duas iterações de auditoria realizadas, o resultado da Fase 3 e o modo de reproduzir o fluxo. Os relatórios e artefatos de estado permanecem versionados nas pastas `reports/` dos respectivos projetos.

## Sumário

- [A) Análise Manual](#a-análise-manual)
- [B) Construção da Skill](#b-construção-da-skill)
- [C) Resultados](#c-resultados)
- [D) Como Executar](#d-como-executar)

## A) Análise Manual

A inspeção manual foi realizada sobre as versões legadas dos três projetos, antes da execução da skill. O objetivo foi identificar riscos representativos que servissem como baseline para o catálogo de antipadrões e para a posterior verificação da Fase 2. A classificação segue a escala do desafio: `CRITICAL` para falhas graves de segurança ou arquitetura; `HIGH` para violações severas de separação de responsabilidades; `MEDIUM` para problemas de validação, duplicação, organização ou performance; e `LOW` para legibilidade, nomenclatura e resíduos de implementação.

### A.1 `code-smells-project` — Python/Flask

| Severidade | Problema identificado | Relevância técnica |
|---|---|---|
| `CRITICAL` | Senhas expostas por endpoint desprotegido | A representação HTTP reutilizava dados de persistência sem um DTO seguro. Isso permitia obter credenciais sem autenticação e ampliava o impacto do armazenamento inseguro de senhas. |
| `CRITICAL` | SQL injection e execução de SQL arbitrário no endpoint `/admin/query` | Entrada externa era encaminhada à execução de SQL sem uma fronteira de consultas permitidas. Um atacante poderia ler, alterar ou excluir dados e contornar regras da aplicação. |
| `CRITICAL` | `SECRET_KEY` fixada no código | O segredo de assinatura fazia parte do código-fonte e ainda podia ser exposto por respostas de diagnóstico. Além de impedir rotação segura por ambiente, isso comprometia a confiança nas sessões. |
| `CRITICAL` | Rotas administrativas críticas sem autenticação ou autorização | Operações de reset do banco e consulta administrativa estavam publicamente acessíveis. Uma única requisição poderia causar indisponibilidade, perda de dados ou acesso irrestrito ao SQLite. |
| `HIGH` | Regras de negócio dentro dos controllers | Fluxos como criação de produto, validação de estoque e transições de pedido estavam acoplados ao ciclo HTTP. Isso reduzia coesão, impedia testes isolados e distribuía decisões de domínio entre controllers e persistência. |
| `MEDIUM` | Validação e criação de produto duplicadas em `criar_produto` e `atualizar_produto` | A repetição de categorias, limites e regras de entrada criava múltiplas fontes de verdade, aumentando o risco de comportamento divergente entre criação e atualização. |
| `MEDIUM` | Consultas duplicadas em `criar_pedido` e na montagem dos pedidos | O acesso a pedidos, itens e produtos repetia consultas e padrões de montagem em mais de um fluxo. A duplicação dificultava manutenção e também contribuía para o padrão N+1. |
| `LOW` | Valores de domínio e parâmetros operacionais fixados em controllers e bootstrap | Categorias, estados, porta, modo de debug e outros literais estavam espalhados. Alterações exigiam busca textual e podiam produzir configurações ou regras inconsistentes. |
| `LOW` | Importações mortas e logging por `print` | Resíduos de implementação aumentavam ruído e o logging não estruturado dificultava filtragem, redação de dados e controle por ambiente. |

**Síntese.** O projeto apresentava uma separação apenas nominal entre arquivos: HTTP, regras, SQL, serialização e administração continuavam fortemente acoplados. Os problemas prioritários para a skill eram criar fronteiras de segurança, separar casos de uso da persistência e preservar os contratos HTTP durante uma reorganização arquitetural ampla.

### A.2 `ecommerce-api-legacy` — Node.js/Express

| Severidade | Problema identificado | Relevância técnica |
|---|---|---|
| `CRITICAL` | Senhas, credenciais e segredos expostos em `utils.js` | Chaves operacionais e dados sensíveis estavam versionados junto ao código. Isso eliminava a separação por ambiente e exigia, além da remoção no código, rotação das credenciais reais potencialmente comprometidas. |
| `CRITICAL` | Endpoints administrativos e destrutivos sem proteção | Relatórios financeiros e exclusão de usuários podiam ser acionados sem autenticação/autorização adequada, expondo dados comerciais e operações destrutivas. |
| `HIGH` | `AppManager` como God Class | A classe concentrava inicialização do banco, schema, seed, rotas, validação, checkout, persistência, relatórios, serialização e erros. O alto acoplamento tornava mudanças e testes isolados arriscados. |
| `MEDIUM` | Consultas N+1 no relatório financeiro | O relatório disparava consultas adicionais para cada curso ou matrícula. O custo crescia com o volume de dados e deveria ser substituído por JOIN, agregação ou carregamento em lote. |
| `MEDIUM` | Exclusão de usuário sem validação de matrículas e pagamentos relacionados | A operação não estabelecia política de integridade referencial nem transação explícita. Isso podia deixar registros órfãos ou um estado parcial entre usuários, matrículas e pagamentos. |
| `LOW` | Nomes de variáveis pouco significativos, como `u`, `e` e `p` | Abreviações ocultavam conceitos de domínio em um fluxo sensível de checkout, aumentando o custo de revisão e a probabilidade de troca entre entidades ou valores. |
| `LOW` | Importações e estado residual sem uso | Dependências e variáveis remanescentes ampliavam a superfície cognitiva e sugeriam responsabilidades antigas ainda misturadas ao fluxo principal. |

**Síntese.** Este projeto exigia que a skill adaptasse as mesmas regras arquiteturais a JavaScript/CommonJS e ao modelo assíncrono do Node.js. Os principais alvos eram decompor o Objeto Deus, criar limites transacionais e de autorização e substituir consultas encadeadas por operações de persistência coesas.

### A.3 `task-manager-api` — Python/Flask com organização parcial

| Severidade | Problema identificado | Relevância técnica |
|---|---|---|
| `CRITICAL` | Senhas de demonstração expostas no código-fonte em `seed.py` | Mesmo em dados de carga, credenciais previsíveis podem chegar a ambientes compartilhados, ser reutilizadas e normalizar práticas inseguras de provisionamento. |
| `CRITICAL` | Segredo da aplicação fixado em `app.py` | Um segredo versionado não pode ser rotacionado de forma independente por ambiente e compromete tokens ou sessões assinadas quando o repositório é exposto. |
| `CRITICAL` | Endpoint de usuários expondo senha ou hash | A serialização dos models incluía material de autenticação. Hashes também são dados sensíveis e não devem integrar DTOs públicos. |
| `CRITICAL` | Endpoint de usuários sem proteção adequada | Operações de leitura ou alteração de usuários não aplicavam de forma consistente identidade e papel, permitindo enumeração de dados e escalonamento indevido de privilégios. |
| `HIGH` | Lógica de negócio nas classes e funções de rota | Blueprints acumulavam adaptação HTTP, validação, consultas, transações, autorização contextual e regras. A existência de pastas `models/`, `routes/` e `services/` não correspondia a uma separação efetiva. |
| `MEDIUM` | Endpoints de categorias misturados a `report_routes.py` | CRUD de categorias e geração de relatórios pertencem a capacidades distintas. Mantê-los no mesmo módulo diminuía coesão e dificultava evolução e testes por domínio. |
| `MEDIUM` | Contagem e consultas dentro de loop em `report_routes.py` | A agregação por usuário executava acesso adicional ao banco a cada iteração, caracterizando N+1 e degradando progressivamente o tempo de resposta dos relatórios. |
| `LOW` | Nomes pouco significativos, como `u`, `e` e `p` | Variáveis abreviadas dificultavam reconhecer usuário, entidade, payload ou resultado em handlers que já acumulavam múltiplas responsabilidades. |
| `LOW` | Importações mortas e responsabilidades residuais em helpers/services | Código desconectado do fluxo real criava a aparência de camadas sem que as rotas as utilizassem, aumentando a ambiguidade sobre a arquitetura vigente. |

**Síntese.** O risco central era confundir organização de diretórios com MVC efetivo. A skill precisava seguir o fluxo de dependências e detectar ORM, transações e regras dentro das rotas, preservando os componentes úteis e introduzindo somente as fronteiras ausentes.

### A.4 Cobertura mínima da análise

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total documentado |
|---|---:|---:|---:|---:|---:|
| `code-smells-project` | 4 | 1 | 2 | 2 | 9 |
| `ecommerce-api-legacy` | 2 | 1 | 2 | 2 | 7 |
| `task-manager-api` | 4 | 1 | 2 | 2 | 9 |

Os três projetos atendem à cobertura manual mínima exigida: ao menos cinco problemas por projeto, pelo menos um `CRITICAL` ou `HIGH`, dois `MEDIUM` e dois `LOW`. A auditoria automatizada não ficou limitada a esta baseline; como demonstrado na seção de resultados, a Fase 2 exigiu evidência concreta em arquivo e linha e ampliou os achados quando encontrou riscos adicionais.

## B) Construção da Skill

Esta seção descreve o processo de criação, as decisões de design, o catálogo de antipadrões, as estratégias de neutralidade tecnológica e os desafios de implementação da skill `refactor-arch`.

### B.1 Processo de construção

A skill foi construída para o OpenAI Codex com o objetivo de analisar, auditar e refatorar bases de código legadas de backend para uma arquitetura MVC. Como o enunciado do desafio usa Claude Code como referência, a implementação adaptou a convenção de diretórios para Codex, mantendo o mesmo conceito central: um [`SKILL.md`](code-smells-project/.agents/skills/refactor-arch/SKILL.md) como orquestrador e arquivos Markdown de referência para fornecer conhecimento especializado sob demanda.

O processo começou pela definição do fluxo principal em três fases obrigatórias:

1. **Análise:** detectar stack, framework, banco de dados, domínio, arquivos relevantes, arquitetura atual e pontos de entrada.
2. **Auditoria:** comparar a base de código com um catálogo de antipadrões, classificar severidade, gerar relatório estruturado e solicitar confirmação humana.
3. **Refatoração:** após confirmação explícita, planejar, quebrar em tarefas, implementar a migração para MVC e validar inicialização, endpoints e regressão arquitetural.

Essa separação reduz o risco operacional. A Fase 1 é exclusivamente investigativa; a Fase 2 consolida evidências e interrompe o fluxo antes de qualquer alteração no código; e a Fase 3 só executa mudanças após aprovação humana. A confirmação entre auditoria e refatoração funciona como barreira obrigatória porque a skill pode modificar estruturas, imports, rotas, configurações e arquivos de aplicação.

### B.2 Decisões de design

O `SKILL.md` foi mantido como ponto central de orquestração. Ele descreve entradas, fases, regras de segurança, controle de estado, critérios de retomada e responsabilidades de alto nível. Os detalhes extensos foram movidos para `references/`, seguindo o princípio de divulgação progressiva: o agente carrega apenas o conhecimento necessário à fase corrente.

Os arquivos de referência foram separados por responsabilidade:

- [`project-analysis.md`](code-smells-project/.agents/skills/refactor-arch/references/project-analysis.md): heurísticas para detectar linguagem, framework, banco de dados, domínio e arquitetura real;
- [`anti-pattern-catalog.md`](code-smells-project/.agents/skills/refactor-arch/references/anti-pattern-catalog.md): catálogo de antipadrões, sinais de detecção, severidades e recomendações;
- [`audit-report-template.md`](code-smells-project/.agents/skills/refactor-arch/references/audit-report-template.md): formato obrigatório do relatório de auditoria;
- [`mvc-guidelines.md`](code-smells-project/.agents/skills/refactor-arch/references/mvc-guidelines.md): arquitetura MVC alvo, responsabilidades por camada e variações por stack;
- [`refactoring-playbook.md`](code-smells-project/.agents/skills/refactor-arch/references/refactoring-playbook.md): padrões concretos de transformação com exemplos antes/depois;
- [`validation-checklist.md`](code-smells-project/.agents/skills/refactor-arch/references/validation-checklist.md): critérios para validar inicialização, endpoints, testes e regressão arquitetural;
- [`workflow-state.md`](code-smells-project/.agents/skills/refactor-arch/references/workflow-state.md): modelo de estado, checkpoints, retomada e controle de tarefas.

Também foram criados perfis especializados em `references/agents/` e agentes personalizados em `.codex/agents/`. Cada objetivo principal possui um agente dedicado: análise do projeto, auditoria de antipadrões, geração do relatório, planejamento MVC, escrita de tarefas, implementação e validação. Essa divisão reduz ambiguidade, evita concentrar responsabilidades incompatíveis no mesmo contexto e permite que cada etapa use instruções adequadas ao próprio nível de risco. A execução continua coordenada por uma única linha de decisão no agente principal, especialmente na barreira de confirmação entre as Fases 2 e 3.

Outra decisão importante foi tornar o controle de estado explícito. A skill cria e atualiza `reports-folder/.refactor-arch/STATE.md` para registrar fase atual, artefatos gerados, confirmação humana, achados por severidade, cobertura dos achados, tarefas de refatoração, validações e erros. Isso permite retomar a execução no ponto correto após uma interrupção, sem repetir tarefas concluídas nem avançar sem aprovação.

### B.3 Antipadrões incluídos no catálogo

O catálogo cobre arquitetura, segurança, manutenibilidade, performance e qualidade de código em backends legados. Foram incluídos 15 antipadrões, superando o mínimo de oito exigido pelo desafio:

| ID | Antipadrão | Motivo da inclusão |
|---|---|---|
| AP-01 | Injeção de SQL/consulta dinâmica insegura | Cobre falhas críticas causadas pela concatenação de entrada externa em consultas. |
| AP-02 | Segredos fixados no código | Detecta credenciais, tokens e chaves expostos em código, configuração ou respostas HTTP. |
| AP-03 | Endpoint administrativo sem proteção | Identifica rotas perigosas sem autenticação/autorização, como reset de banco ou consultas arbitrárias. |
| AP-04 | Classe, arquivo ou método Deus | Captura concentração excessiva de responsabilidades, comum em monólitos legados. |
| AP-05 | Regra de negócio pesada em rota/controller | Direciona a extração de regras para services/casos de uso e mantém routes/controllers finos. |
| AP-06 | Persistência misturada com domínio | Detecta SQL, transações e serialização misturados a regras de negócio. |
| AP-07 | Criptografia ou senha insegura | Cobre MD5/SHA1, senhas em texto puro, tokens falsos e ausência de salt. |
| AP-08 | Vazamento de dados sensíveis | Impede exposição de senha, hash, token, cartão, segredo, stack trace ou SQL em respostas e logs. |
| AP-09 | N+1 consultas/consulta em loop | Cobre gargalos de performance provocados por consultas repetidas dentro de loops. |
| AP-10 | Estado global mutável | Detecta caches, conexões e contadores globais sem ciclo de vida claro. |
| AP-11 | Validação espalhada e duplicada | Incentiva a extração de validators, schemas e constantes de domínio. |
| AP-12 | Tratamento de erros inconsistente | Cobre `except` genérico, vazamento de exceções e ausência de rollback. |
| AP-13 | APIs obsoletas ou legadas | Atende ao requisito de detectar APIs deprecated e recomendar equivalentes modernos. |
| AP-14 | Nomes obscuros e valores mágicos | Endereça legibilidade, nomenclatura deficiente e constantes implícitas. |
| AP-15 | Importações mortas e responsabilidades residuais | Apoia a limpeza final após a reorganização das camadas. |

A seleção foi guiada pela escala de severidade do desafio. Os itens `CRITICAL` e `HIGH` priorizam segurança e separação de responsabilidades; os itens `MEDIUM` tratam duplicação, validação, performance e APIs legadas; e os itens `LOW` cobrem legibilidade e limpeza incremental. O catálogo também evita achados artificiais: todo problema precisa ter evidência concreta em arquivo e linha ou, quando a evidência for distribuída, uma explicação estrutural verificável.

### B.4 Estratégias para manter a skill agnóstica de tecnologia

A skill opera sobre comportamento arquitetural, não sobre nomes fixos de arquivos ou frameworks. Em vez de assumir que um projeto segue MVC por possuir pastas como `models/`, `routes/` ou `services/`, ela exige leitura do fluxo real: imports, rotas, handlers, queries, serialização, configuração, inicialização e chamadas entre módulos.

As heurísticas cobrem Python/Flask, Node.js/Express e stacks similares. A detecção considera manifests (`requirements.txt`, `package.json`, `pyproject.toml`), imports, entry points, scripts de inicialização, ORMs, conexões diretas com banco, migrations, seeds, rotas e middlewares. Quando existe mais de uma stack ou evidência insuficiente, a skill deve declarar a ambiguidade em vez de extrapolar.

As diretrizes MVC foram escritas como contrato de responsabilidades, não como árvore rígida. A skill aceita variações como `routes/` no lugar de `views/`, CommonJS em projetos Node.js existentes, Blueprints em Flask e uso opcional de repositories quando o projeto ou o risco justificar. O objetivo é preservar a separação entre entrada HTTP, coordenação do caso de uso, regra de negócio, persistência, configuração e tratamento transversal.

O playbook também foi mantido genérico. Ele define dez transformações reutilizáveis — extrair configuração, parametrizar SQL, afinar routes/controllers, dividir objetos Deus, eliminar N+1, substituir criptografia fraca, criar DTOs seguros, centralizar erros, extrair validação e modernizar APIs obsoletas — com exemplos antes/depois. Esses exemplos orientam o raciocínio, mas nomes, módulos e idioms são adaptados à stack detectada.

### B.5 Desafios encontrados e soluções adotadas

O primeiro desafio foi adaptar o enunciado, baseado em Claude Code, para a estrutura do OpenAI Codex. A solução preservou a anatomia conceitual da skill (`SKILL.md` + referências Markdown) e adotou os diretórios compatíveis com Codex, incluindo perfis em `references/agents/` e agentes personalizados em `.codex/agents/`.

Outro desafio foi impedir alterações prematuras no código. Como a skill pode refatorar projetos inteiros, foi definida uma regra forte: antes da confirmação ao fim da Fase 2, somente relatórios e artefatos de estado podem ser criados ou atualizados. Essa restrição aparece no `SKILL.md`, nos perfis dos agentes e no controle de estado.

Também foi necessário garantir rastreabilidade entre auditoria e refatoração. A Fase 3 exige uma matriz de cobertura que vincula cada achado aprovado a uma decisão (`FIX`, `PARTIAL`, `DEFER`, `ACCEPT_RISK` ou `NOT_APPLICABLE`), às etapas do plano, às tarefas e às validações. Assim, a refatoração não se torna uma reescrita genérica: cada mudança precisa estar ligada a um problema identificado ou a uma necessidade arquitetural documentada.

A retomada após interrupções foi outro ponto sensível. A solução formalizou `STATE.md` como fonte de verdade, contendo fase atual, artefatos, permissão para modificar código, confirmação humana, tarefas, cobertura dos achados e log de validação. Antes de continuar, a skill lê esse estado e parte da primeira fase ou tarefa `PENDING` ou `FAILED`.

Por fim, era necessário manter as instruções completas sem sobrecarregar o `SKILL.md`. A separação do conhecimento em referências especializadas e perfis por objetivo mantém o orquestrador conciso, ao mesmo tempo que fornece instruções detalhadas para análise, auditoria, relatório, planejamento, implementação e validação quando cada fase precisa delas.

## C) Resultados

Esta seção consolida as evidências produzidas pela execução da skill `refactor-arch` nos três projetos-alvo. Para distinguir detecção de correção, os números apresentados são os dos relatórios de auditoria gerados na Fase 2: um achado corrigido na Fase 3 continua compondo o relatório que motivou a mudança. O estado pós-refatoração é demonstrado separadamente pelos relatórios de validação, testes automatizados e smoke tests HTTP.

Cada projeto passou por duas iterações das Fases 1 e 2. A primeira auditou a base legada e orientou a migração arquitetural. A segunda reavaliou a base já refatorada para identificar riscos residuais. Apenas o `code-smells-project` teve uma segunda execução da Fase 3, necessária para tratar problemas de segurança e integridade encontrados na reauditoria. Nos outros dois projetos, a segunda Fase 3 não foi executada porque os achados residuais foram mantidos como recomendações posteriores, sem invalidar a refatoração MVC já validada.

### C.1 Resumo executivo das auditorias

| Projeto | Iteração | CRITICAL | HIGH | MEDIUM | LOW | Total | Situação dos achados |
|---|---:|---:|---:|---:|---:|---:|---|
| `code-smells-project` | 1 | 5 | 4 | 3 | 2 | 14 | Corrigidos e validados na primeira Fase 3 |
| `code-smells-project` | 2 | 2 | 1 | 2 | 2 | 7 | Corrigidos e validados na segunda Fase 3 |
| `ecommerce-api-legacy` | 1 | 4 | 3 | 4 | 2 | 13 | Corrigidos e validados na primeira Fase 3 |
| `ecommerce-api-legacy` | 2 | 0 | 0 | 5 | 2 | 7 | Backlog incremental; nova Fase 3 não executada |
| `task-manager-api` | 1 | 4 | 3 | 4 | 2 | 13 | Corrigidos e validados na primeira Fase 3 |
| `task-manager-api` | 2 | 0 | 0 | 6 | 1 | 7 | Backlog de hardening/limpeza; nova Fase 3 não executada |
| **Total** | **1** | **13** | **10** | **11** | **6** | **40** | **Todos os achados iniciais corrigidos e validados** |
| **Total** | **2** | **2** | **1** | **13** | **5** | **21** | **7 corrigidos; 14 recomendações não críticas documentadas** |

As primeiras auditorias produziram 40 achados e atenderam, nos três projetos, ao mínimo de cinco findings e à exigência de pelo menos um `CRITICAL` ou `HIGH`. Após as primeiras refatorações, as reauditorias reduziram os achados graves de 23 para 3; esses três pertenciam ao `code-smells-project` e foram eliminados pela segunda Fase 3. O estado final, portanto, não possui `CRITICAL` ou `HIGH` conhecido em aberto. Permanecem 14 recomendações (`11 MEDIUM` e `3 LOW`) nos outros dois projetos, mantidas conscientemente como backlog por não exigirem nova reorganização MVC.

Neste documento, “corrigido” significa que o tratamento no código e as validações previstas no plano foram concluídos. Isso não substitui ações externas ou configuração de produção; essas responsabilidades estão explicitadas em **C.6 Limitações e riscos operacionais remanescentes**.

### C.2 `code-smells-project` — Python/Flask

#### C.2.1 Escopo e evolução das auditorias

A Fase 1 identificou corretamente uma API de e-commerce em Python 3, Flask 3.1.1 e SQLite. Na primeira iteração foram analisados os quatro arquivos-fonte legados, aproximadamente 780 linhas, e a arquitetura foi classificada como monólito procedural em camadas, com MVC apenas nominal. A segunda iteração inspecionou 35 arquivos Python — 30 considerados relevantes e aproximadamente 1.442 linhas, incluindo testes — e reconheceu corretamente a arquitetura MVC/em camadas criada na primeira refatoração.

| Iteração | Estado analisado | CRITICAL | HIGH | MEDIUM | LOW | Total | Fase 3 |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | Código legado da `main` | 5 | 4 | 3 | 2 | 14 | Executada e validada |
| 2 | Código após a primeira refatoração | 2 | 1 | 2 | 2 | 7 | Executada e validada |
| Resultado final | Após o hardening da segunda Fase 3 | 0 aberto | 0 aberto | 0 aberto | 0 aberto | 0 aberto | Todos os 7 achados tratados como `FIX` |

Na primeira auditoria, os achados `CRITICAL` cobriram SQL arbitrário/injeção, endpoints administrativos desprotegidos, senhas em texto puro, segredo e debug fixados no código e vazamento de senhas nas respostas. Os achados `HIGH` registraram arquivo Deus, mistura entre persistência e domínio, regras de negócio em controllers e conexão SQLite global. Em `MEDIUM`, foram identificados N+1, tratamento de erros inconsistente e validação duplicada; em `LOW`, valores mágicos e resíduos de implementação/logging.

Esses resultados confirmaram e ampliaram a análise manual: todos os temas nela mapeados — exposição de senha, SQL injection, segredo fixo, rotas administrativas abertas, regra de negócio em controller, duplicação de validação/consultas e valores de domínio fixados — apareceram na auditoria com evidência de arquivo e linhas. A skill ainda explicitou riscos correlatos que a inspeção manual não havia detalhado, principalmente senha persistida em texto puro, estado global de banco, N+1 e vazamento de exceções.

A primeira Fase 3 eliminou os 14 achados e criou a arquitetura MVC. A reauditoria foi importante porque não se limitou a reconhecer a nova estrutura: encontrou credenciais previsíveis no seed, ausência de autenticação/autorização geral, enumeração pública de dados pessoais e pedidos, falta de constraints, DDL/seed durante o boot, números mágicos na política de desconto e uma política de exclusão incoerente com o campo `ativo`. A segunda Fase 3 corrigiu os sete itens com seed explícito e configurável, migração transacional, constraints, soft delete, política de desconto nomeada, sessão assinada e guards de papel e ownership.

Nenhuma API obsoleta aplicável foi encontrada nas duas auditorias. Essa ausência foi registrada explicitamente, em vez de gerar um finding artificial.

Relatórios de evidência: [auditoria da iteração 1](code-smells-project/reports/iteracao-01/audit-code-smells-project.md), [validação da iteração 1](code-smells-project/reports/iteracao-01/.refactor-arch/validation-report.md), [auditoria da iteração 2](code-smells-project/reports/iteracao-02-executada/audit-code-smells-project.md) e [validação final](code-smells-project/reports/iteracao-02-executada/.refactor-arch/validation-report.md).

#### C.2.2 Estrutura antes e depois

Antes da refatoração, rotas, acesso a dados, regras de negócio e serialização estavam distribuídos em quatro módulos de grande abrangência. `models.py`, com 314 linhas, concentrava CRUD de múltiplos domínios, autenticação, pedidos, estoque, relatórios, serialização e SQL; `controllers.py` misturava adaptação HTTP, validação e efeitos de negócio; `database.py` mantinha conexão global, schema e seed; e `app.py` registrava rotas e executava operações administrativas com acesso direto ao banco.

```text
# Antes — branch main
code-smells-project/
├── app.py                 # bootstrap, rotas e operações administrativas
├── controllers.py         # HTTP, validações e regras de negócio
├── database.py            # conexão global, DDL e seed
├── models.py              # SQL, domínio, serialização e relatórios
├── requirements.txt
└── README.md
```

Depois, `app.py` tornou-se um ponto de entrada mínimo e o pacote `loja/` passou a separar composição, configuração e responsabilidades por camada e domínio. Blueprints recebem HTTP, controllers coordenam os casos de uso, services concentram regras e transações, repositories isolam SQL parametrizado, models representam dados e middlewares tratam identidade/autorização. A suíte de regressão foi adicionada em `tests/`.

```text
# Depois — estado final
code-smells-project/
├── app.py
├── loja/
│   ├── __init__.py                 # application factory e composição
│   ├── config.py                   # configuração externa
│   ├── database.py                 # conexão, schema e migração
│   ├── errors.py                   # erros centralizados e sanitizados
│   ├── models.py
│   ├── controllers/                # produto, usuário, pedido, relatório e sistema
│   ├── middlewares/
│   │   └── auth.py                 # sessão, papéis e ownership
│   ├── repositories/               # SQL isolado por domínio
│   ├── services/                   # regras, transações e validação
│   └── views/                      # Blueprints e respostas HTTP
├── tests/
│   └── test_api.py
├── requirements.txt
└── README.md
```

A mudança preservou os 19 métodos/caminhos HTTP originais. Alterações observáveis foram deliberadamente restritas a correções de segurança: respostas deixaram de expor senha/hash e detalhes internos, SQL livre passou a ser recusado, operações e dados sensíveis receberam autenticação/autorização e erros internos passaram a ser sanitizados.

#### C.2.3 Checklist de validação

##### Fase 1 — Análise

- [x] Linguagem detectada corretamente: Python 3.
- [x] Framework detectado corretamente: Flask 3.1.1, com Flask-Cors e SQLite.
- [x] Domínio descrito corretamente: API de e-commerce/loja.
- [x] Número de arquivos condizente com cada estado: 4 fontes na base legada; 35 arquivos Python inspecionados, 30 relevantes, na reauditoria.

##### Fase 2 — Auditoria

- [x] Os dois relatórios seguem o template definido pela skill.
- [x] Todos os findings apresentam arquivo, linhas, evidência, impacto e recomendação.
- [x] Findings ordenados de `CRITICAL` para `LOW`.
- [x] Mínimo de cinco findings atendido nas duas iterações: 14 e 7.
- [x] APIs deprecated verificadas; nenhuma ocorrência aplicável foi encontrada.
- [x] Pausa e confirmação humana registradas antes de cada execução da Fase 3.

##### Fase 3 — Refatoração

- [x] Estrutura organizada em MVC e camadas por domínio.
- [x] Configuração extraída para `loja/config.py`, sem segredo ou credencial de execução fixados.
- [x] Models/DTOs representam dados sem expor campos sensíveis.
- [x] Views/routes separadas em Blueprints finos.
- [x] Controllers coordenam services e respostas sem acessar o banco.
- [x] Regras e transações concentradas em services; SQL isolado e parametrizado em repositories.
- [x] Autenticação, papel e ownership centralizados em middleware reutilizável.
- [x] Error handling centralizado e respostas de erro sanitizadas.
- [x] Entry point reduzido e application factory sem DDL/seed automático no boot padrão.
- [x] Aplicação iniciada sem erros em servidor Flask temporário.
- [x] Todos os 19 contratos de endpoint preservados e validados.
- [x] Suíte final aprovada: 11 testes, sem falhas.
- [x] Todos os 21 achados auditados ao longo das duas iterações possuem correção validada; nenhum `CRITICAL` ou `HIGH` permanece aberto.

#### C.2.4 Evidências de execução após a refatoração

O relatório final registra inicialização bem-sucedida na porta alternativa `5001` — a porta `5000` estava ocupada — usando SQLite temporário em `/tmp`. O servidor foi encerrado ao final do smoke test. A suíte foi executada novamente durante a elaboração desta documentação, com o mesmo resultado:

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v
...
Ran 11 tests in 3.124s

OK
```

O smoke HTTP real confirmou tanto os fluxos públicos e autenticados quanto o comportamento fail-closed:

```text
GET  /                         -> 200
GET  /health                   -> 200
GET  /produtos                 -> 200
GET  /usuarios (anônimo)       -> 401
POST /login (admin)            -> 200
GET  /usuarios (admin)         -> 200
POST /produtos (admin)         -> 201
POST /pedidos (admin)          -> 201
GET  /relatorios/vendas        -> 200
POST /admin/query              -> 403
```

Além dos códigos HTTP esperados, o health check não revelou segredo, debug ou caminho do banco; login e listagem não retornaram senha/hash; e o endpoint legado de SQL arbitrário permaneceu bloqueado.

#### C.2.5 Avaliação do resultado

O `code-smells-project` foi o caso mais agressivo de transformação: partiu de quatro arquivos fortemente acoplados e sem testes para uma arquitetura modular, testável e protegida. A segunda iteração demonstrou uma propriedade importante da skill: ela não tratou a presença de pastas MVC como prova suficiente de qualidade. Ao reinspecionar o fluxo real, reconheceu que a separação arquitetural já estava adequada, evitou uma reestruturação redundante e direcionou a segunda Fase 3 somente ao hardening de segurança, integridade e ciclo de vida dos dados.

### C.3 `ecommerce-api-legacy` — Node.js/Express

#### C.3.1 Escopo e evolução das auditorias

A Fase 1 identificou corretamente uma API JavaScript/CommonJS sobre Node.js, Express 4.22.1 e SQLite 5.1.7. Embora o nome do diretório sugira e-commerce genérico, a skill inferiu corretamente o domínio real: um LMS com checkout de cursos, usuários, matrículas, pagamentos e relatório financeiro. Na primeira iteração foram analisados três arquivos-fonte, aproximadamente 180 linhas, e a arquitetura foi classificada como monólito com Objeto Deus. Na segunda, foram analisados 28 arquivos JavaScript relevantes — 27 da aplicação e uma suíte de testes, aproximadamente 935 linhas — e a estrutura foi corretamente reclassificada como MVC/em camadas.

| Iteração | Estado analisado | CRITICAL | HIGH | MEDIUM | LOW | Total | Fase 3 |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | Código legado da `main` | 4 | 3 | 4 | 2 | 13 | Executada e validada |
| 2 | Código após a refatoração | 0 | 0 | 5 | 2 | 7 | Não executada, conforme recomendação técnica |
| Estado validado | Refatoração da iteração 1 | 0 aberto entre os 13 originais | 0 aberto entre os 13 originais | 0 aberto entre os 13 originais | 0 aberto entre os 13 originais | 13 tratados | Todos os achados originais tratados como `FIX` |

Os quatro achados `CRITICAL` da primeira auditoria foram segredos fixados no código, endpoints administrativos/destrutivos sem proteção, armazenamento inseguro de senha e log de cartão/chave de pagamento. Os três `HIGH` cobriram o Objeto Deus `AppManager`, a regra pesada de checkout dentro da rota e a falta de fronteira transacional/integridade referencial. Em `MEDIUM`, a skill detectou N+1, cache global mutável, validação incompleta e erros inconsistentes; em `LOW`, nomes/valores obscuros e estado residual sem uso.

A auditoria confirmou todos os temas da análise manual: credenciais expostas, endpoints críticos abertos, God Class, N+1, exclusão sem proteção da integridade e nomes pouco expressivos. Ela aprofundou esses achados ao demonstrar o risco de PAN e chave de gateway em log, hashing reversível por Base64, checkout não atômico, estado global e falhas silenciosas em callbacks.

A Fase 3 tratou os 13 itens: removeu segredos e logs sensíveis; introduziu configuração por ambiente, autenticação administrativa fail-closed, `scrypt` com salt, transação e rollback, foreign keys/cascata, JOIN único para relatório, validação, erros centralizados e dependências injetadas. O contrato externo dos três endpoints foi preservado. A remoção impede que os valores continuem no código atual, mas credenciais reais anteriormente expostas ainda precisam ser rotacionadas nos respectivos sistemas externos.

Na segunda auditoria, a skill reconheceu que não restavam problemas estruturais ou achados `CRITICAL`/`HIGH` e recomendou não executar uma nova refatoração MVC. Os sete itens residuais foram classificados corretamente como melhorias incrementais: driver `node-sqlite3` descontinuado, ausência de idempotência no checkout, política de senha permissiva, ciclo de vida incompleto no bind do servidor, sucesso indevido ao excluir usuário inexistente, valor mágico no gateway simulado e resposta HTML para rotas desconhecidas. Esses itens permanecem documentados e fora do escopo da Fase 3 já concluída; não invalidam o funcionamento nem a separação MVC comprovados, mas constituem backlog técnico explícito.

A detecção de APIs deprecated adaptou-se à evidência de cada iteração. Na primeira, não havia uso direto de API obsoleta no código; dependências transitivas deprecated foram apenas sinalizadas para atualização futura. Na segunda, o driver `sqlite3` foi identificado como descontinuado e recebeu finding `MEDIUM` com recomendação de substituição no adapter de persistência, sem promover indevidamente a questão a falha arquitetural crítica.

Relatórios de evidência: [auditoria da iteração 1](ecommerce-api-legacy/reports/iteracao-01/audit-ecommerce-api-legacy.md), [validação da iteração 1](ecommerce-api-legacy/reports/iteracao-01/.refactor-arch/validation-report.md) e [auditoria da iteração 2](ecommerce-api-legacy/reports/iteracao-02-nao_executada/audit-ecommerce-api-legacy.md).

#### C.3.2 Estrutura antes e depois

Antes da refatoração, `src/AppManager.js` concentrava abertura e inicialização do banco, schema, seeds, registro de rotas, validação HTTP, checkout, SQL, relatório, serialização e erros. `src/utils.js` reunia configuração sensível, cache global, logging e hashing inseguro. Não havia testes, controllers, services, repositories, middlewares ou fronteira transacional.

```text
# Antes — branch main
ecommerce-api-legacy/
├── src/
│   ├── app.js              # Express e instanciação do AppManager
│   ├── AppManager.js       # HTTP, domínio, banco, relatório e administração
│   └── utils.js            # segredos, cache, log e criptografia fraca
├── api.http
├── package.json
└── README.md
```

Depois, `src/app.js` passou a construir apenas o Express e seus middlewares, enquanto `src/server.js` se tornou a composition root. O caso de uso de checkout, o relatório e a administração de usuários foram separados verticalmente, com routes/controllers na borda, services no domínio e repositories/db na persistência. A estratégia é idiomática para Express e preserva CommonJS, evitando uma migração tecnológica desnecessária.

```text
# Depois — estado validado
ecommerce-api-legacy/
├── src/
│   ├── app.js
│   ├── server.js                         # composition root e startup
│   ├── config/
│   │   └── index.js                      # ambiente, sem segredo default
│   ├── controllers/                      # checkout, relatório e usuário
│   ├── db/                               # conexão, schema/seed e adapter Promise
│   ├── errors/
│   │   └── AppError.js
│   ├── middlewares/                      # adminAuth e errorHandler
│   ├── repositories/                     # SQL, JOIN, transação e integridade
│   ├── routes/                           # três contratos HTTP
│   ├── services/                         # checkout, relatório, senha e usuário
│   └── validators/
│       └── checkoutValidator.js
├── test/
│   └── run.js
├── api.http
├── package.json
└── README.md
```

A refatoração removeu `AppManager.js` e `utils.js` após confirmar que não havia consumidores residuais. SQL passou a existir somente em `db/` e `repositories/`; services ficaram independentes de Express; e autenticação, erros e redação de dados sensíveis passaram a ser preocupações transversais explícitas.

#### C.3.3 Checklist de validação

##### Fase 1 — Análise

- [x] Linguagem detectada corretamente: JavaScript/CommonJS sobre Node.js.
- [x] Framework detectado corretamente: Express 4, com SQLite.
- [x] Domínio descrito corretamente: LMS com checkout, matrículas, pagamentos e relatório financeiro.
- [x] Número de arquivos condizente com cada estado: 3 fontes na base legada; 28 arquivos JavaScript relevantes na reauditoria.

##### Fase 2 — Auditoria

- [x] Os dois relatórios seguem o template da skill.
- [x] Cada finding contém arquivo, linhas, evidência, impacto e recomendação.
- [x] Findings ordenados por severidade.
- [x] Mínimo de cinco findings atendido nas duas iterações: 13 e 7.
- [x] APIs deprecated verificadas; `node-sqlite3` foi identificado na segunda iteração.
- [x] A primeira Fase 2 pausou e recebeu confirmação humana antes das mudanças.
- [x] A segunda Fase 2 pausou sem editar código; a nova Fase 3 não foi executada, em conformidade com a recomendação de preservar o MVC já adequado.

##### Fase 3 — Refatoração da iteração 1

- [x] Estrutura organizada em MVC/camadas adequada ao Express.
- [x] Configuração extraída para módulo próprio e alimentada pelo ambiente.
- [x] Models/persistência abstraídos por `db/` e repositories.
- [x] Views/routes declarativas e separadas por recurso.
- [x] Controllers finos concentram a adaptação HTTP.
- [x] Services concentram regras e orquestração, sem dependência de Express.
- [x] Error handling centralizado em middleware.
- [x] Entry point e composition root explícitos em `app.js` e `server.js`.
- [x] Senhas protegidas por `scrypt`, salt aleatório e comparação timing-safe.
- [x] Transações, rollback, foreign keys e cascata validados em SQLite real.
- [x] Aplicação iniciou sem erros com `npm start`.
- [x] Os três endpoints originais responderam corretamente.
- [x] Regressão funcional, de segurança e arquitetural aprovada.
- [x] Todos os 13 achados originais tratados como `FIX`.

#### C.3.4 Evidências de execução após a refatoração

A validação foi realizada com Node.js 14.16.1. Devido à interoperabilidade WSL/Windows do ambiente, o script do npm precisou ser chamado pelo `npm-cli.js` nativo; essa adaptação foi operacional e não exigiu alteração na aplicação. Os logs registrados mostram:

```text
$ npm test
PASS: regressão funcional, segurança e arquitetura MVC

$ npm start
LMS API rodando na porta 3000.
# processo encerrado pelo timeout controlado após 8 s
```

O smoke test iniciou o servidor em porta efêmera e comprovou os três contratos originais, incluindo erros e proteção administrativa:

```text
POST   /api/checkout                   payload vazio         -> 400
POST   /api/checkout                   cartão recusado       -> 400, sem escrita parcial
POST   /api/checkout                   curso inexistente     -> 404
POST   /api/checkout                   sucesso               -> 200
GET    /api/admin/financial-report     sem chave             -> 401
GET    /api/admin/financial-report     chave válida          -> 200
DELETE /api/users/2                    sem chave             -> 401
DELETE /api/users/2                    chave válida          -> 200
GET    /api/admin/financial-report     sem chave configurada -> 503
```

O relatório financeiro retornou as receitas esperadas `[997, 497]`; após a exclusão autorizada, o curso afetado retornou receita `0` e lista vazia de alunos, comprovando a cascata. A inicialização confirmou `PRAGMA foreign_keys = 1`, o seed armazenou senha no formato `scrypt$...`, o fluxo recusado não deixou efeitos parciais e as buscas estáticas não encontraram segredos, cache global, criptografia fraca ou SQL fora da persistência.

#### C.3.5 Avaliação do resultado

Este projeto comprovou a adaptação da skill a uma stack diferente sem transportar padrões específicos de Flask. Em Node.js/Express, ela preservou CommonJS, utilizou middlewares, composition root, injeção explícita e adaptadores baseados em Promises para SQLite. Também tratou corretamente o modelo assíncrono baseado em callbacks, convertendo-o em limites testáveis e transacionais. Na reauditoria, a skill evitou uma segunda reestruturação artificial: reconheceu MVC real pelas responsabilidades e pelo fluxo de dependências, manteve zero achados `CRITICAL`/`HIGH` e separou modernização de dependência e melhorias comportamentais do objetivo arquitetural já atingido.

### C.4 `task-manager-api` — Python/Flask com organização parcial

#### C.4.1 Escopo e evolução das auditorias

A Fase 1 identificou corretamente Python 3, Flask 3.0.0, Flask-SQLAlchemy 3.1.1/SQLAlchemy 2.0.51 e SQLite, além do domínio de gerenciamento de tarefas, usuários, categorias e relatórios. Diferentemente do primeiro projeto Flask, esta base já possuía pastas `models/`, `routes/`, `services/` e `utils/`. A skill não confundiu organização nominal com separação real: nos 15 arquivos-fonte iniciais, aproximadamente 1.158 linhas, constatou que os Blueprints ainda acumulavam View/Route, Controller, Service e Repository. Na segunda iteração, 44 arquivos Python e aproximadamente 1.941 linhas foram inspecionados, e a arquitetura foi reconhecida como MVC/em camadas efetivo.

| Iteração | Estado analisado | CRITICAL | HIGH | MEDIUM | LOW | Total | Fase 3 |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | Código parcialmente organizado da `main` | 4 | 3 | 4 | 2 | 13 | Executada e validada |
| 2 | Código após a refatoração | 0 | 0 | 6 | 1 | 7 | Não executada, conforme recomendação técnica |
| Estado validado | Refatoração da iteração 1 | 0 aberto entre os 13 originais | 0 aberto entre os 13 originais | 0 aberto entre os 13 originais | 0 aberto entre os 13 originais | 13 tratados | Todos os achados originais tratados como `FIX` |

Na primeira auditoria, os quatro achados `CRITICAL` foram segredos fixados, endpoints privilegiados sem proteção/escalonamento de papel, MD5 com token previsível e exposição do hash de senha. Os três `HIGH` registraram rotas como objetos Deus, regras/relatórios pesados nos handlers e persistência/transações controladas pelas rotas. Em `MEDIUM`, foram encontrados N+1, validação/serialização duplicada, erros inconsistentes e `Query.get()` legado; em `LOW`, nomes/valores mágicos e responsabilidades residuais.

Os resultados cobriram integralmente a análise manual. Senhas de demonstração, segredo fixo, exposição de senha e usuários, lógica nas rotas, mistura de categorias com relatórios, contagem dentro de loop e nomes abreviados foram mapeados com localização precisa. A auditoria refinou a gravidade ao relacionar esses sinais a escalonamento de privilégio, token falso, DTO inseguro, rotas Deus, N+1, transações na borda e dívida de compatibilidade com SQLAlchemy 2.x.

A primeira Fase 3 corrigiu os 13 itens. A configuração passou a vir do ambiente; novas senhas usam hash forte; o token passou a ser assinado e temporizado; DTOs deixaram de expor hash; autenticação, papéis e erros foram centralizados; routes/controllers ficaram sem ORM; services e repositories assumiram regras e persistência; schemas centralizaram validação/serialização; eager loading e agregações removeram N+1; e as chamadas HTTP principais deixaram a API `Query.get()` legada.

A segunda auditoria não encontrou violações graves de MVC, segredos fixos, endpoints administrativos abertos, senha em DTO, N+1 ou regras pesadas na borda. Os sete achados residuais foram mantidos como hardening/limpeza pontual: leitura anônima de tarefas cuja intenção de negócio não está documentada, chave de assinatura efêmera sem variável de ambiente, ponte temporária para MD5, senha mínima de quatro caracteres, `create_all()` dentro da factory, API `Query` legada apenas no seed e código/documentação residuais. Como todos são `MEDIUM` ou `LOW`, alguns dependem de decisão de produto ou inventário de bases externas e nenhum exige reorganização MVC, a segunda Fase 3 não foi executada.

A verificação de APIs deprecated foi particularmente útil neste projeto. A primeira auditoria encontrou `Model.query.get()` no fluxo HTTP e recomendou `db.session.get()`, correção aplicada na Fase 3. A reauditoria confirmou a ausência dessa API no fluxo principal, mas encontrou `Model.query.delete()` e `Model.query.count()` no script de seed, mantendo a modernização restante corretamente limitada ao ambiente de desenvolvimento.

Relatórios de evidência: [auditoria da iteração 1](task-manager-api/reports/iteracao-01/audit-project-3.md), [validação da iteração 1](task-manager-api/reports/iteracao-01/.refactor-arch/validation-report.md) e [auditoria da iteração 2](task-manager-api/reports/iteracao-02-nao_executada/audit-project-3.md).

#### C.4.2 Estrutura antes e depois

Antes, a estrutura sugeria camadas, porém os três arquivos de routes, com 211 a 299 linhas, realizavam HTTP, validação, consultas, transações, regras, relatórios e serialização. `report_routes.py` também continha CRUD de categorias. O único service estava desconectado do fluxo, e helpers duplicavam regras sem serem consumidos.

```text
# Antes — branch main
task-manager-api/
├── app.py
├── database.py
├── models/
│   ├── category.py
│   ├── task.py
│   └── user.py
├── routes/
│   ├── report_routes.py       # relatórios e categorias
│   ├── task_routes.py         # HTTP, ORM e regras
│   └── user_routes.py         # HTTP, ORM e autenticação
├── services/
│   └── notification_service.py
├── utils/
│   └── helpers.py
├── seed.py
├── requirements.txt
└── README.md
```

Depois, os Blueprints passaram a apenas registrar rotas e decorators; controllers adaptam HTTP; services executam casos de uso e autorização contextual; repositories concentram SQLAlchemy, eager loading, agregações e transações; schemas definem validação e DTOs seguros; e middlewares centralizam autenticação, autorização e erros. O CRUD de categorias ganhou rota, controller, service e repository próprios.

```text
# Depois — estado validado
task-manager-api/
├── app.py                              # application factory/composição
├── config.py                           # configuração por ambiente
├── database.py
├── exceptions.py
├── controllers/                        # tarefa, usuário, categoria e relatório
├── middlewares/                        # auth e error handler
├── models/                             # entidades ORM enxutas
├── repositories/                       # persistência e consultas agregadas
├── routes/                             # Blueprints finos por recurso
│   ├── category_routes.py
│   ├── report_routes.py
│   ├── task_routes.py
│   └── user_routes.py
├── schemas/                            # constantes, validators e serializers
├── services/                           # auth, casos de uso e notificação residual
├── tests/
│   └── test_api.py
├── utils/
│   ├── helpers.py                      # helpers residuais apontados na reauditoria
│   └── time.py
├── seed.py
├── requirements.txt
└── README.md
```

Os 22 métodos/caminhos originais foram preservados. As mudanças observáveis — remoção de `password` das respostas, substituição do token falso e exigência de Bearer token/papel ou identidade em operações sensíveis — foram aprovadas e documentadas como correções de segurança.

#### C.4.3 Checklist de validação

##### Fase 1 — Análise

- [x] Linguagem detectada corretamente: Python 3.
- [x] Framework detectado corretamente: Flask 3.0.0 e Flask-SQLAlchemy 3.1.1/SQLAlchemy 2.0.51.
- [x] Domínio descrito corretamente: tarefas, usuários, categorias e relatórios de produtividade.
- [x] Número de arquivos condizente com cada estado: 15 fontes na base inicial; 44 arquivos Python na reauditoria.

##### Fase 2 — Auditoria

- [x] Os dois relatórios seguem o template da skill.
- [x] Cada finding contém arquivo, linhas, evidência, impacto e recomendação.
- [x] Findings ordenados por severidade.
- [x] Mínimo de cinco findings atendido nas duas iterações: 13 e 7.
- [x] APIs deprecated verificadas e localizadas no fluxo principal e, depois, apenas no seed.
- [x] A primeira Fase 2 pausou e recebeu confirmação humana antes das mudanças.
- [x] A segunda Fase 2 permaneceu somente leitura; a nova Fase 3 não foi executada, conforme recomendação de preservar o MVC adequado.

##### Fase 3 — Refatoração da iteração 1

- [x] Estrutura MVC/em camadas implementada por responsabilidades reais.
- [x] Configuração extraída para `config.py`, sem segredo fixado.
- [x] Models ORM mantidos enxutos e repositories responsáveis pela persistência.
- [x] Views/routes finas, separadas por domínio e sem ORM.
- [x] Controllers responsáveis por entrada/saída HTTP e escolha de DTOs.
- [x] Services independentes de Flask concentram regras, autorização contextual e transações.
- [x] Schemas centralizam constantes, validação e serialização segura.
- [x] Autenticação, autorização e error handling centralizados em middlewares.
- [x] Entry point claro com application factory.
- [x] Aplicação iniciou sem erros na porta de validação `5051`.
- [x] Os 22 contratos HTTP foram registrados e exercitados.
- [x] Suíte aprovada: 4 testes, sem falhas.
- [x] Todos os 13 achados originais tratados como `FIX`.

#### C.4.4 Evidências de execução após a refatoração

O boot real foi confirmado na porta `5051`: o processo permaneceu ativo até o timeout controlado de três segundos, sem exceção de inicialização. O seed também foi validado contra SQLite in-memory, criando três usuários, quatro categorias e dez tarefas. A suíte foi executada novamente durante a elaboração desta documentação, isolada em memória:

```text
$ DATABASE_URL=sqlite:///:memory: venv/bin/python -m unittest discover -s tests -v
test_all_original_endpoint_contracts ... ok
test_authentication_authorization_and_safe_dtos ... ok
test_url_map_and_architectural_boundaries ... ok
test_validation_errors_and_legacy_password_migration ... ok

Ran 4 tests in 3.406s

OK
```

Os testes e smoke checks registraram os seguintes comportamentos:

```text
GET  / e GET /health                         -> 200
GET  /tasks, /tasks/<id>, /tasks/search      -> 200
POST/PUT/DELETE /tasks sem token             -> 401
POST /login com credencial válida            -> 200 + token assinado
GET/POST/PUT/DELETE /users                    -> identidade/papel validados
GET  /reports/summary e /reports/user/<id>    -> identidade/papel validados
GET  /categories                             -> 200
POST/PUT/DELETE /categories sem admin         -> 401/403
payload ou recurso inválido                   -> 400/404 em JSON padronizado
```

Além da regressão funcional, as varreduras confirmaram 44 arquivos Python sintaticamente válidos, dependências íntegras, nenhum ORM em routes/controllers, nenhum Flask em services, nenhum segredo conhecido/token falso/`Query.get()`/`datetime.utcnow()`/`except:` nu e nenhuma chave `password` nos serializers e adaptadores HTTP.

#### C.4.5 Avaliação do resultado

O `task-manager-api` comprovou a capacidade da skill de analisar comportamento, não apenas nomes de diretório. A base inicial parecia organizada, mas a leitura do fluxo mostrou que as rotas ainda concentravam quatro responsabilidades e que services/helpers existentes eram, em parte, decorativos. A refatoração foi, por isso, seletiva: preservou os models e Blueprints úteis, criou as fronteiras ausentes e separou categorias de relatórios. Na reauditoria, a skill reconheceu a melhora material e restringiu os achados a decisões de segurança, ciclo de vida, modernização do seed e limpeza, sem classificar artificialmente nenhum item como `CRITICAL` ou `HIGH`.

### C.5 Comparação entre stacks e comportamento da skill

#### Detecção orientada a evidências

A skill permaneceu agnóstica porque partiu de manifestos, importações, pontos de entrada, registros de rotas, chamadas ao banco e fluxo de dependências, e não de nomes predefinidos. Isso permitiu detectar corretamente dois projetos Flask com arquiteturas iniciais muito diferentes e um projeto Express/CommonJS. Também permitiu inferir o domínio LMS do `ecommerce-api-legacy`, apesar do nome genérico do diretório.

#### Adaptação do MVC à tecnologia

No Flask monolítico, a solução usou application factory, Blueprints, controllers, services, repositories e conexão por contexto. No Express, adotou routes, controllers, services, repositories, middlewares, composition root e adaptadores baseados em Promises, respeitando o modelo assíncrono do Node.js. No Task Manager, preservou models e Blueprints úteis e introduziu apenas as fronteiras ausentes. A skill aplicou MVC como contrato de responsabilidades, sem impor a mesma árvore ou o mesmo padrão de implementação a todas as stacks.

#### Sensibilidade ao estado arquitetural

A segunda iteração comprovou que a skill não considera a simples presença de pastas como evidência de qualidade, nem fabrica severidade para atingir uma distribuição esperada. Ela encontrou riscos graves residuais no primeiro projeto, recomendando e executando hardening; nos outros dois, confirmou MVC real, registrou somente itens `MEDIUM`/`LOW` e recomendou evitar nova reestruturação. Esse comportamento reduziu mudanças desnecessárias e preservou contratos já validados.

#### Segurança e controle humano

Nas três primeiras execuções, a Fase 2 interrompeu o fluxo antes de editar código e a Fase 3 só ocorreu após confirmação humana. Mudanças de contrato motivadas por segurança — proteção de operações, retirada de senha/hash, bloqueio de SQL livre e substituição de token falso — foram explicitadas nos planos e verificadas por códigos `401`, `403` e respostas sanitizadas. Na segunda iteração dos projetos sem nova refatoração, o estado permaneceu em `WAITING_CONFIRMATION`, com modificação de código desabilitada.

#### Estratégias de validação

A validação também se adaptou à stack. Os projetos Flask usaram `unittest`, cliente de teste, SQLite temporário/in-memory, inspeção do URL map e boot real controlado. O projeto Node.js usou um runner de contrato, SQLite real em memória, servidor em porta efêmera, verificações de rollback e `npm start`. Restrições ambientais de socket e interoperabilidade WSL/Windows foram registradas e contornadas de forma controlada durante as execuções originais, sem serem confundidas com falhas da aplicação.

### C.6 Limitações e riscos operacionais remanescentes

Os itens abaixo não contradizem o `PASS` das refatorações: são condições de operação, migração ou evolução que não podem ser eliminadas apenas pela reorganização arquitetural executada.

| Projeto | Responsabilidades e limitações remanescentes |
|---|---|
| `code-smells-project` | Produção deve definir `SECRET_KEY` estável, cookies seguros, HTTPS e allowlist de CORS, além de usar servidor WSGI. Bases legadas com e-mails duplicados ou relações inválidas exigem correção manual antes da migração; o processo falha sem descartar dados silenciosamente. Não há endpoint de reativação após soft delete. |
| `ecommerce-api-legacy` | Credenciais reais expostas no legado devem ser rotacionadas externamente. A API key administrativa atende ao escopo atual, mas uma evolução multiusuário requer identidade, papéis e auditoria por ator. O SQLite permanece em memória por compatibilidade com o contrato original; persistência durável e migrations ficaram fora do escopo. |
| `task-manager-api` | Produção deve configurar `SECRET_KEY` persistente. Hashes MD5 legados só migram após login válido e devem ser inventariados/removidos; o SMTP não foi exercitado por depender de serviço externo. As datas permanecem sem timezone no schema legado, embora sejam geradas a partir de UTC explícito. |

Essas limitações provêm dos [resultados finais do `code-smells-project`](code-smells-project/reports/iteracao-02-executada/.refactor-arch/validation-report.md), da [validação do `ecommerce-api-legacy`](ecommerce-api-legacy/reports/iteracao-01/.refactor-arch/validation-report.md) e da [validação do `task-manager-api`](task-manager-api/reports/iteracao-01/.refactor-arch/validation-report.md). Elas complementam e contextualizam os 14 findings `MEDIUM`/`LOW` mantidos no backlog das reauditorias.

### C.7 Conclusão dos resultados

A execução da `refactor-arch` atingiu os critérios de aceite nos três projetos:

- [x] Stack, framework, domínio e arquitetura detectados corretamente em 3/3 projetos.
- [x] Pelo menos cinco findings identificados em 3/3 auditorias iniciais.
- [x] Pelo menos um finding `CRITICAL` ou `HIGH` identificado em 3/3 auditorias iniciais.
- [x] Estrutura MVC criada ou fortalecida de acordo com a stack em 3/3 projetos.
- [x] Aplicações iniciadas sem erros após a refatoração em 3/3 projetos.
- [x] Contratos originais preservados e exercitados: 19, 3 e 22, respectivamente.
- [x] Testes/regressão aprovados e evidências de execução registradas em 3/3 projetos.
- [x] Todos os 40 achados das auditorias iniciais receberam decisão `FIX` e validação local; ações externas e condições de produção permanecem explicitamente registradas.
- [x] Nenhum achado `CRITICAL` ou `HIGH` conhecido permanece aberto após a segunda iteração.

O resultado demonstra que a skill é reutilizável entre stacks e entre diferentes níveis de maturidade arquitetural. Ela transformou um monólito Flask, decompôs um Objeto Deus assíncrono em Express e corrigiu uma separação apenas nominal em outro Flask, preservando comportamento e adicionando validação automatizada. As reauditorias fecharam o ciclo ao comprovar a melhoria estrutural, identificar riscos residuais sem inflar severidades e produzir um backlog rastreável para evoluções que não justificavam nova Fase 3.

## D) Como Executar

Esta seção descreve os pré-requisitos, a forma de invocação da skill `refactor-arch` no OpenAI Codex, os comandos específicos de cada projeto e as verificações necessárias para confirmar a refatoração. Em uma execução nova, os exemplos gravam o relatório diretamente em `reports/audit-project-N.md`; as evidências desta entrega foram arquivadas em subdiretórios de iteração, conforme os links da seção C.

### D.1 Pré-requisitos

- OpenAI Codex CLI instalado, autenticado e configurado;
- execução iniciada a partir da raiz de cada projeto, e não da raiz do repositório pai;
- skill disponível no projeto em `.agents/skills/refactor-arch/`;
- agentes personalizados disponíveis no projeto em `.codex/agents/refactor-*.toml`;
- dependências da aplicação instaláveis conforme o `README.md` de cada projeto;
- árvore de trabalho revisada antes da execução, pois a Fase 3 altera o código-fonte após confirmação.

Os três projetos já possuem a skill e os agentes nos caminhos esperados:

| Projeto | Skill | Agentes |
|---|---|---|
| `code-smells-project` | [`code-smells-project/.agents/skills/refactor-arch/`](code-smells-project/.agents/skills/refactor-arch/SKILL.md) | [`code-smells-project/.codex/agents/`](code-smells-project/.codex/agents/refactor-project-analyzer.toml) |
| `ecommerce-api-legacy` | [`ecommerce-api-legacy/.agents/skills/refactor-arch/`](ecommerce-api-legacy/.agents/skills/refactor-arch/SKILL.md) | [`ecommerce-api-legacy/.codex/agents/`](ecommerce-api-legacy/.codex/agents/refactor-project-analyzer.toml) |
| `task-manager-api` | [`task-manager-api/.agents/skills/refactor-arch/`](task-manager-api/.agents/skills/refactor-arch/SKILL.md) | [`task-manager-api/.codex/agents/`](task-manager-api/.codex/agents/refactor-project-analyzer.toml) |

### D.2 Forma de invocação no Codex

No Codex CLI, a skill deve ser chamada pelo nome `$refactor-arch`. A mensagem abaixo deve ser enviada dentro da interface do Codex, já posicionada na raiz do projeto-alvo:

```text
Use $refactor-arch neste projeto.
Parâmetros:
- project-folder: .
- reports-folder: reports
- report-name: [NOME_DO_RELATORIO]
Execute as Fases 1 e 2. Ao concluir a Fase 2, pause e solicite confirmação antes da Fase 3.
```

Ao final da Fase 2, revise o relatório de auditoria gerado. Se estiver correto e a refatoração deva ser aplicada, responda no Codex:

```text
s
```

Se a resposta não for afirmativa, a skill encerra o fluxo sem alterar o código-fonte.

### D.3 Projeto 1 — `code-smells-project`

Entre na raiz do projeto:

```bash
cd code-smells-project
```

No Codex CLI, envie:

```text
Use $refactor-arch neste projeto.
Parâmetros:
- project-folder: .
- reports-folder: reports
- report-name: audit-project-1.md
Execute as Fases 1 e 2. Ao concluir a Fase 2, pause e solicite confirmação antes da Fase 3.
```

Após revisar `reports/audit-project-1.md`, responda `s` para executar a Fase 3.

Valide a execução da skill verificando:

- `reports/audit-project-1.md`;
- `reports/.refactor-arch/STATE.md`;
- `reports/.refactor-arch/phase-1-analysis.md`;
- `reports/.refactor-arch/refactor-plan.md`;
- `reports/.refactor-arch/refactor-tasks.md`;
- `reports/.refactor-arch/validation-report.md`.

Para validar a aplicação refatorada, siga o [`README.md` do projeto](code-smells-project/README.md). Em resumo:

```bash
python3 -m pip install -r requirements.txt
flask --app app init-db
python3 app.py
curl http://localhost:5000/health
python3 -m unittest discover -v
```

`python3 app.py` mantém o servidor em primeiro plano. Execute o `curl` em outro terminal ou interrompa o servidor antes de rodar a suíte de testes. No Windows, use `python` no lugar de `python3` se esse for o executável disponível.

### D.4 Projeto 2 — `ecommerce-api-legacy`

Entre na raiz do projeto:

```bash
cd ecommerce-api-legacy
```

No Codex CLI, envie:

```text
Use $refactor-arch neste projeto.
Parâmetros:
- project-folder: .
- reports-folder: reports
- report-name: audit-project-2.md
Execute as Fases 1 e 2. Ao concluir a Fase 2, pause e solicite confirmação antes da Fase 3.
```

Após revisar `reports/audit-project-2.md`, responda `s` para executar a Fase 3.

Valide a execução da skill verificando:

- `reports/audit-project-2.md`;
- `reports/.refactor-arch/STATE.md`;
- `reports/.refactor-arch/phase-1-analysis.md`;
- `reports/.refactor-arch/refactor-plan.md`;
- `reports/.refactor-arch/refactor-tasks.md`;
- `reports/.refactor-arch/validation-report.md`.

Para validar a aplicação refatorada, siga o [`README.md` do projeto](ecommerce-api-legacy/README.md). Em resumo:

```bash
npm ci
npm test
npm start
```

`npm start` mantém o servidor em primeiro plano. Com o servidor ativo, valide os endpoints em outro terminal usando o arquivo [`api.http`](ecommerce-api-legacy/api.http) ou as requisições `curl` descritas no README da aplicação, especialmente:

- `POST /api/checkout`;
- `GET /api/admin/financial-report` com `ADMIN_API_KEY`;
- `DELETE /api/users/:id` com `ADMIN_API_KEY`.

### D.5 Projeto 3 — `task-manager-api`

Entre na raiz do projeto:

```bash
cd task-manager-api
```

No Codex CLI, envie:

```text
Use $refactor-arch neste projeto.
Parâmetros:
- project-folder: .
- reports-folder: reports
- report-name: audit-project-3.md
Execute as Fases 1 e 2. Ao concluir a Fase 2, pause e solicite confirmação antes da Fase 3.
```

Após revisar `reports/audit-project-3.md`, responda `s` para executar a Fase 3.

Valide a execução da skill verificando:

- `reports/audit-project-3.md`;
- `reports/.refactor-arch/STATE.md`;
- `reports/.refactor-arch/phase-1-analysis.md`;
- `reports/.refactor-arch/refactor-plan.md`;
- `reports/.refactor-arch/refactor-tasks.md`;
- `reports/.refactor-arch/validation-report.md`.

Para validar a aplicação refatorada, siga o [`README.md` do projeto](task-manager-api/README.md). Em resumo:

```bash
python3 -m pip install -r requirements.txt
python3 seed.py
python3 app.py
curl http://localhost:5000/health
python3 -m unittest discover -v
```

`python3 app.py` mantém o servidor em primeiro plano. Execute o `curl` em outro terminal ou interrompa o servidor antes de rodar a suíte. O seed é opcional para a API iniciar, mas ajuda a validar fluxos autenticados e endpoints com dados de demonstração.

### D.6 Checklist de validação da skill

Após executar a skill em cada projeto, confirme:

- [ ] A Fase 1 detectou linguagem, framework, domínio e arquitetura atual corretamente.
- [ ] A Fase 2 gerou o relatório no nome esperado (`audit-project-1.md`, `audit-project-2.md` ou `audit-project-3.md`).
- [ ] O relatório contém pelo menos cinco achados quando houver evidência suficiente.
- [ ] Os achados estão classificados por severidade (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) e incluem arquivo/linha quando aplicável.
- [ ] A skill pausou ao final da Fase 2 e só iniciou a Fase 3 após resposta afirmativa.
- [ ] A Fase 3 gerou `refactor-plan.md`, `refactor-tasks.md` e `validation-report.md`.
- [ ] `STATE.md` registra a fase final, tarefas executadas, validações e eventuais limitações.
- [ ] A aplicação inicia sem erros depois da refatoração.
- [ ] Os endpoints originais principais continuam respondendo.
- [ ] Os testes automatizados do projeto passam, ou qualquer impedimento está documentado em `validation-report.md`.

Este checklist é operacional para uma nova execução; os checklists preenchidos e as evidências da execução entregue estão na seção C.

### D.7 Retomada após interrupção

Se a execução for interrompida, reabra o Codex CLI na raiz do mesmo projeto e envie:

```text
Use $refactor-arch para retomar a execução deste projeto a partir de reports/.refactor-arch/STATE.md.
Não reinicie tarefas concluídas; continue da primeira fase ou tarefa PENDING ou FAILED.
```

A skill lê `reports/.refactor-arch/STATE.md` antes de agir, preserva tarefas concluídas e respeita o campo `Modificações no código-fonte permitidas`.

### D.8 Observações importantes

- Execute a skill separadamente em cada projeto.
- Não execute a skill a partir da raiz do repositório pai quando o objetivo for refatorar apenas um projeto.
- Antes de confirmar a Fase 3, revise o relatório de auditoria e os riscos identificados.
- Em projetos já refatorados, uma nova execução audita o estado atual; para reproduzir a refatoração desde o início, use uma cópia limpa do projeto legado.
- As instruções completas de instalação, variáveis de ambiente, endpoints e testes pertencem ao `README.md` de cada projeto. Esta seção registra o fluxo de execução da skill e os pontos de validação relacionados a ela.
