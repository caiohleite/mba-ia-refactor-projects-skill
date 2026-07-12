# Construção da Skill

Este documento descreve somente a construção da skill `refactor-arch`, conforme solicitado na seção **B) Construção da Skill** do `README.md`. O foco está no processo de criação, nas decisões de design, no catálogo de antipadrões, nas estratégias adotadas para manter a skill agnóstica de tecnologia e nos desafios encontrados durante a implementação.

## Processo de construção

A skill foi construída para o OpenAI Codex com o objetivo de analisar, auditar e refatorar bases de código legadas de backend para uma arquitetura MVC. Como o enunciado do desafio usa Claude Code como referência, a implementação adaptou a convenção de diretórios para Codex, mantendo o mesmo conceito central: um `SKILL.md` como orquestrador e arquivos Markdown de referência para fornecer conhecimento especializado sob demanda.

O processo começou pela definição do fluxo principal da skill em três fases obrigatórias:

1. **Análise**: detectar stack, framework, banco de dados, domínio, arquivos relevantes, arquitetura atual e pontos de entrada.
2. **Auditoria**: comparar a base de código com um catálogo de antipadrões, classificar severidade, gerar relatório estruturado e solicitar confirmação humana.
3. **Refatoração**: após confirmação explícita, planejar, quebrar em tarefas, implementar a migração para MVC e validar inicialização, endpoints e regressão arquitetural.

Essa separação foi adotada para reduzir risco operacional. A Fase 1 é exclusivamente investigativa, a Fase 2 consolida evidências e interrompe o fluxo antes de qualquer alteração de código, e a Fase 3 só executa mudanças após aprovação humana. A confirmação entre auditoria e refatoração foi tratada como uma barreira obrigatória, porque a skill pode modificar estruturas, imports, rotas, configuração e arquivos de aplicação.

## Decisões de design

O `SKILL.md` foi mantido como o ponto central de orquestração. Ele descreve entradas, fases, regras de segurança, controle de estado, critérios de retomada e responsabilidades de alto nível. Os detalhes extensos foram movidos para arquivos em `references/`, seguindo o princípio de divulgação progressiva: o agente lê apenas o conhecimento necessário para a fase atual.

Os arquivos de referência foram divididos por responsabilidade:

- `project-analysis.md`: heurísticas para detectar linguagem, framework, banco de dados, domínio e arquitetura real.
- `anti-pattern-catalog.md`: catálogo de antipadrões, sinais de detecção, severidades e recomendações.
- `audit-report-template.md`: formato obrigatório do relatório de auditoria.
- `mvc-guidelines.md`: arquitetura MVC alvo, responsabilidades por camada e variações por stack.
- `refactoring-playbook.md`: padrões concretos de transformação com exemplos antes/depois.
- `validation-checklist.md`: critérios para validar inicialização, endpoints, testes e regressão arquitetural.
- `workflow-state.md`: modelo de estado, checkpoints, retomada e controle de tarefas.

Também foram criados perfis especializados em `references/agents/` e agentes personalizados em `.codex/agents/`. Cada objetivo principal possui um agente dedicado: análise do projeto, auditoria de antipadrões, geração do relatório, planejamento MVC, escrita de tarefas, implementação e validação. Essa divisão reduz ambiguidade, evita que um único prompt concentre responsabilidades demais e permite que cada etapa use instruções adequadas ao seu nível de risco.

Outra decisão importante foi tornar o controle de estado explícito. A skill cria e atualiza `reports-folder/.refactor-arch/STATE.md` para registrar fase atual, artefatos gerados, confirmação humana, achados por severidade, cobertura dos achados, tarefas de refatoração, validações e erros. Isso permite retomar a execução no ponto correto após interrupções, sem repetir tarefas já concluídas nem avançar sem aprovação.

## Antipadrões incluídos no catálogo

O catálogo foi desenhado para cobrir problemas de arquitetura, segurança, manutenibilidade, performance e qualidade de código encontrados em projetos backend legados. Foram incluídos 15 antipadrões, excedendo o mínimo exigido pelo desafio:

| ID | Antipadrão | Motivo da inclusão |
|---|---|---|
| AP-01 | Injeção de SQL / consulta dinâmica insegura | Cobre falhas críticas de segurança causadas por concatenação de entrada externa em consultas. |
| AP-02 | Segredos fixados no código | Detecta credenciais, tokens e chaves expostas em código, configuração ou respostas HTTP. |
| AP-03 | Endpoint administrativo sem proteção | Identifica rotas perigosas sem autenticação/autorização, como reset de banco ou consultas arbitrárias. |
| AP-04 | Classe/arquivo/método Deus | Captura concentração excessiva de responsabilidades, comum em monólitos legados. |
| AP-05 | Regra de negócio pesada em rota/controller | Direciona a extração de regras para services/use cases e mantém rotas/controllers finos. |
| AP-06 | Persistência misturada com domínio | Detecta SQL, transações e serialização misturados com regras de negócio. |
| AP-07 | Criptografia ou senha insegura | Cobre uso de MD5/SHA1, senhas em texto puro, tokens falsos e ausência de salt. |
| AP-08 | Vazamento de dados sensíveis | Impede exposição de senha, hash, token, cartão, segredo, stack trace ou SQL em respostas/logs. |
| AP-09 | N+1 consultas / consulta em loop | Cobre gargalos comuns de performance por consulta repetida dentro de loops. |
| AP-10 | Estado global mutável | Detecta caches, conexões e contadores globais sem ciclo de vida claro. |
| AP-11 | Validação espalhada e duplicada | Incentiva extração de validators, schemas e constantes de domínio. |
| AP-12 | Tratamento de erros inconsistente | Cobre `except` genérico, vazamento de exceções e ausência de rollback. |
| AP-13 | APIs obsoletas ou legadas | Atende ao requisito de detectar APIs deprecated e recomendar equivalentes modernos. |
| AP-14 | Nomes obscuros e valores mágicos | Endereça legibilidade, nomenclatura ruim e constantes implícitas. |
| AP-15 | Importações mortas e responsabilidades residuais | Apoia a limpeza final após a reorganização das camadas. |

A escolha desses antipadrões foi guiada pelos critérios de severidade do desafio. Os itens `CRITICAL` e `HIGH` priorizam segurança e separação de responsabilidades; os itens `MEDIUM` tratam duplicação, validação, performance e APIs legadas; os itens `LOW` cobrem legibilidade e limpeza incremental. O catálogo também evita achados artificiais: cada problema precisa ter evidência concreta em arquivo e linha, ou explicação estrutural quando a evidência estiver distribuída.

## Estratégias para manter a skill agnóstica

A skill foi projetada para operar sobre comportamento arquitetural, não sobre nomes fixos de arquivos ou frameworks específicos. Em vez de assumir que um projeto é MVC por possuir pastas como `models/`, `routes/` ou `services/`, ela exige leitura do fluxo real: imports, rotas, handlers, queries, serialização, configuração, inicialização e chamadas entre módulos.

As heurísticas de análise cobrem Python/Flask, Node.js/Express e stacks similares. A detecção considera manifests (`requirements.txt`, `package.json`, `pyproject.toml`), imports, entry points, scripts de inicialização, ORMs, conexões diretas com banco, migrations, seeds, rotas e middlewares. Quando há mais de uma stack ou incerteza, a skill deve declarar a ambiguidade em vez de inferir além das evidências.

As diretrizes MVC foram escritas como contrato de responsabilidades, não como uma estrutura rígida. A skill aceita variações como `routes/` no lugar de `views/`, CommonJS em projetos Node.js existentes, blueprints em Flask e uso opcional de repositories quando o projeto ou o risco justificar. O objetivo é preservar a separação entre entrada HTTP, coordenação de caso de uso, regra de negócio, persistência, configuração e tratamento transversal.

O playbook de refatoração também foi mantido genérico. Ele descreve transformações reutilizáveis, como extrair configuração, substituir SQL concatenado por parâmetros, afinar rotas/controllers, dividir objetos Deus, remover N+1 consultas, substituir criptografia fraca, criar DTOs seguros, centralizar tratamento de erros, extrair validação e modernizar APIs obsoletas. Os exemplos servem como padrão de raciocínio, mas a skill deve adaptar nomes, módulos e idioms à stack detectada.

## Desafios encontrados e soluções adotadas

O primeiro desafio foi adaptar o enunciado, baseado em Claude Code, para a estrutura do OpenAI Codex. A solução foi preservar a anatomia conceitual da skill (`SKILL.md` + referências Markdown) e usar os diretórios compatíveis com Codex, incluindo perfis em `references/agents/` e agentes personalizados em `.codex/agents/`.

Outro desafio foi impedir alterações prematuras no código. Como a skill tem capacidade de refatorar projetos, foi necessário explicitar uma regra de segurança forte: antes da confirmação da Fase 2, somente relatórios e artefatos de estado podem ser criados ou atualizados. Essa restrição aparece no `SKILL.md`, nos agentes e no controle de estado.

Também foi necessário garantir rastreabilidade entre auditoria e refatoração. Para isso, a Fase 3 exige uma matriz de cobertura ligando cada achado aprovado a uma decisão (`FIX`, `PARTIAL`, `DEFER`, `ACCEPT_RISK` ou `NOT_APPLICABLE`), etapas do plano, tarefas e validações. Assim, a refatoração não se torna uma reescrita genérica: cada mudança precisa estar vinculada a um problema identificado ou a uma necessidade arquitetural documentada.

A retomada após interrupções foi outro ponto sensível. A solução foi formalizar `STATE.md` como fonte de verdade, com fase atual, artefatos, permissão para modificar código, confirmação humana, tarefas, cobertura dos achados e log de validação. A skill deve ler esse estado antes de qualquer retomada e continuar a partir da primeira tarefa `PENDING` ou `FAILED`.

Por fim, houve o desafio de manter os prompts completos sem sobrecarregar o `SKILL.md`. A solução foi separar o conhecimento em referências especializadas e usar perfis de agentes para cada objetivo. Isso mantém o orquestrador conciso, mas ainda fornece instruções detalhadas para análise, auditoria, relatório, planejamento, implementação e validação quando cada fase precisar delas.
