---
name: project-architectural-report
description: Generate comprehensive read-only architectural reports for a software project, including dependency audit, architectural analysis, component deep dives, MANIFEST tracking, project overview, and report index. Use when the user asks Codex to analyze project architecture, audit dependencies, understand components, or produce the equivalent of the Claude Code project-analizer architectural report workflow.
---

# Project Architectural Report

Use this skill to run the Codex equivalent of the original Claude Code `project-analizer` skill. The workflow is read-only for source code: do not refactor, edit, upgrade, or otherwise alter project implementation files. The only files this workflow should create or modify are generated report artifacts inside the selected output folder.

## Source Parity

The original Claude command is retained verbatim in `references/generate-architectural-report.original.md` for parity checks. The Codex-ready specialist profiles are in:

- `references/agents/dependency-auditor.md`
- `references/agents/architectural-analyzer.md`
- `references/agents/component-deep-analyzer.md`

Read the relevant profile before producing that report type. For the full workflow, read all three profiles.

When delegating work to subagents, use the exact prompt templates preserved in `references/generate-architectural-report.original.md`, adapting only Claude-specific tool names and timestamp filename syntax for Codex.

## Parameters

Extract these parameters from the user request:

- `project-folder`: optional analysis scope. Default: workspace root.
- `output-folder`: optional report destination. Default: `docs/agents` relative to the workspace root.
- `ignore-folders`: optional comma-separated folders or files to exclude.

Use filesystem-safe timestamps in filenames: `YYYY-MM-DD_HH-mm-ss`. Inside report content, use the normal human-readable timestamp.

## Full Workflow

### Phase 1: Initialize Output Structure

Create this structure under `output-folder`:

```text
output-folder/
|-- dependency-auditor/
|-- architectural-analyzer/
|-- component-deep-analyzer/
`-- MANIFEST.md
```

Create `MANIFEST.md` with:

```markdown
# MANIFEST - [PROJECT_NAME]
Generated on: [YYYY-MM-DD HH:MM:SS]

## Parameters
- Project folder: [PROJECT_FOLDER]
- Output folder: [OUTPUT_FOLDER]
- Ignore folders: [IGNORE_FOLDERS]

## Execution Status: IN_PROGRESS

## Reports

### dependency-auditor
- Status: PENDING
- Started: -
- Completed: -
- Output: -

### architectural-analyzer
- Status: PENDING
- Started: -
- Completed: -
- Output: -
- Components Found: -

### Components
```

Use the manifest as the single source of truth throughout the workflow. Update statuses incrementally. When using subagents, record the subagent IDs in `MANIFEST.md` so interrupted long-running analyses can be resumed.

### Phase 2: Dependency and Architecture Reports

Produce the dependency audit and architectural analysis. Prefer parallel execution when Codex subagent tooling is available and policy permits it. Otherwise, generate them sequentially in the main Codex turn.

If delegating this phase, use the original dependency-auditor and architectural-analyzer prompt templates from `references/generate-architectural-report.original.md`.

For dependency auditing, follow `references/agents/dependency-auditor.md` and write:

```text
[OUTPUT_FOLDER]/dependency-auditor/dependencies-report-[TIMESTAMP].md
```

For architectural analysis, follow `references/agents/architectural-analyzer.md` and write:

```text
[OUTPUT_FOLDER]/architectural-analyzer/architectural-report-[TIMESTAMP].md
```

After both reports are created:

- Mark each report as `COMPLETED` in `MANIFEST.md`.
- Record started/completed timestamps and output paths.
- Extract every component listed in the architectural report's Critical Components Analysis section.
- Add each component to the manifest with `PENDING` status.

### Phase 3: Component Deep Analysis

For every component identified by the architectural report, follow `references/agents/component-deep-analyzer.md` and write one report per component:

```text
[OUTPUT_FOLDER]/component-deep-analyzer/component-analysis-[COMPONENT_NAME]-[TIMESTAMP].md
```

Analyze one component per report. Prefer parallel execution when Codex subagent tooling is available and policy permits it. If any component fails, mark it `FAILED` with the error in `MANIFEST.md`, continue with the remaining components, and report the failures at the end.

If delegating this phase, use the original component-deep-analyzer prompt template from `references/generate-architectural-report.original.md` for each component.

### Phase 4: Validate Completeness

Verify that every path recorded in `MANIFEST.md` exists. Then update:

- `Execution Status: COMPLETED` if all reports succeeded.
- `Execution Status: PARTIAL` if one or more component reports failed.

Add a completion timestamp.

### Phase 5: Project Overview

Read all generated reports and create:

```text
[OUTPUT_FOLDER]/PROJECT-OVERVIEW-[TIMESTAMP].md
```

Use this structure:

```markdown
# [PROJECT_NAME] - Project Overview

**Generated on**: [YYYY-MM-DD HH:MM:SS]

## Summary

[Two or three factual paragraphs synthesizing key findings.]

## Architecture Overview

[High-level architectural summary from the architectural report.]

## Dependencies Health

[Critical dependency findings only.]

## Components Analyzed

[Each component with one or two factual sentences.]

## Critical Findings

### Security Risks
[Aggregated security concerns.]

### Technical Debt
[Aggregated technical debt items.]

### Single Points of Failure
[Critical dependencies and architectural bottlenecks.]

## Reports Index

See [MANIFEST.md](./MANIFEST.md) for the complete list of generated reports.
```

Do not include recommendations, action plans, implementation guidance, or time estimates. Summarize findings only.

### Phase 6: README Index

Create:

```text
[OUTPUT_FOLDER]/README-[TIMESTAMP].md
```

Use this structure:

```markdown
# [PROJECT_NAME] - Architectural Analysis Reports

**Generated on**: [YYYY-MM-DD HH:MM:SS]

## Quick Links

- [Project Overview](./PROJECT-OVERVIEW-[TIMESTAMP].md) - Executive summary of all findings
- [MANIFEST](./MANIFEST.md) - Complete registry of all reports

---

## Architecture and Dependencies

- [Project Architecture](./architectural-analyzer/architectural-report-[TIMESTAMP].md)
- [Dependencies Report](./dependency-auditor/dependencies-report-[TIMESTAMP].md)

## Component Analysis

[One link per component report.]

---

## Workflow Execution

Analysis completed in these phases:
1. Dependency and architecture analysis
2. Component deep-dive analysis
3. Report synthesis and documentation

Total reports generated: [N]
```

Validate that every README link points to an existing file.

## Recovery

If the workflow is interrupted:

1. Read `MANIFEST.md`.
2. Keep completed report paths intact.
3. Resume from the last incomplete phase.
4. Use recorded subagent IDs or resume parameters when available.
5. Resume from the first `PENDING` or `FAILED` item unless the user asks to rerun everything.
6. Do not regenerate completed reports without explicit user instruction.

## Reporting Rules

- Use relative paths in report content when referencing project files.
- Include line numbers when citing specific source locations where practical.
- State uncertainty explicitly instead of fabricating facts.
- If web access or MCP servers are unavailable for dependency verification, include the limitation and list affected dependencies under Unverified Dependencies.
- Do not modify project code, dependency files, lockfiles, environment files, or infrastructure files.
