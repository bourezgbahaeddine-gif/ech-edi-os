# Echorouk Editorial OS — Brand Guide

## Official Identity
- Official Name: `Echorouk Editorial OS`
- Arabic Brand Line: `غرفة تحرير الشروق الذكية`
- English Tagline: `The Intelligent Newsroom Operating System`
- Project Slug: `ech-edi-os`
- Env Prefix: `ECHOROUK_OS_`
- Container Prefix: `ech-edi-os-`
- Database Recommendation: `echorouk_editorial_os`
- Legal / Ownership Note Placeholder: `TODO`

## Core Definition
Echorouk Editorial OS is a newsroom operating system that manages the editorial lifecycle from signal capture to Ready for Manual Publish, with strict governance and mandatory Human-in-the-Loop.

## Naming Rules
- Use `Echorouk Editorial OS` in UI metadata, login screens, sidebars, backend titles, API docs, exported documents, and public documentation.
- Use `غرفة تحرير الشروق الذكية` as the Arabic-facing brand line when a compact Arabic product line is needed.
- Use `The Intelligent Newsroom Operating System` as the English tagline when a subtitle is needed.
- Do not use standalone `Editorial OS` in user-facing content unless it is preceded by `Echorouk`.
- Do not reintroduce legacy names such as `Echorouk Swarm`, `Smart Newsroom Platform`, or `Intelligent Newsroom Platform`.

## UI Rules
- Favor the official product name in titles and navigation.
- Preserve Arabic RTL rendering in all Arabic brand copy.
- Keep workflow language aligned with `Ready for Manual Publish`, not auto-publish wording.

## Compose And Infra Rules
- Canonical compose project name: `ech-edi-os`
- Canonical compose network name: `ech-edi-os-network`
- Canonical container names start with `ech-edi-os-`
- Canonical named volumes should prefer the `ech_edi_os_` prefix
- Renaming a live production stack from legacy `ech-swarm` names requires a manual migration plan for volumes and any automation that references old container names

## Logs And API Rules
- Structured logs should expose `Echorouk Editorial OS` where product identity is shown.
- Health and root metadata may expose `version`, but any exposed product name must stay canonical.
- Generated client materials and user agents should use the official product identity.

## Documentation Rules
- Docs should describe the platform as a newsroom operating system.
- Docs should state that the editorial lifecycle ends in `Ready for Manual Publish`.
- Historical session notes, changelogs, or migration records may mention legacy names only when clearly marked as legacy context.
