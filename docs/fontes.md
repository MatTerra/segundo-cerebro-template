# Fontes externas

Todas opcionais. A Configuração do `CLAUDE.md` diz quais estão ativas; skill que depende de fonte ausente pula a etapa e avisa.

## Git local
- Repositórios na pasta da Configuração. Evidência de trabalho: `git -C <repo> log --all --author="<autor>" --since=... --until=... --format="%ad|%s|%D" --date=iso`.
- Chave de card no nome do branch ou na mensagem liga o commit ao card.

## GitHub (`gh`)
- `gh auth status` para conferir login.
- Busca de PRs: ver `/esquecidos`. Usar Bash (aspas do `--jq` quebram no PowerShell 5.1).

## Jira (`acli`, Atlassian CLI)
- Instalar: Windows `winget install Atlassian.AtlassianCLI`; macOS/Linux ver docs da Atlassian. Autenticar: `acli jira auth login --web`.
- Windows sem PATH: `$LOCALAPPDATA/Microsoft/WinGet/Links/acli.exe`.
- Busca: `acli jira workitem search --jql "project = KEY" --fields "key,issuetype,summary,status,assignee" --limit 100` (`--json` ou `--csv` para parsear).
- Card: `acli jira workitem view KEY-123`.
- `acli` não aceita `updated` em `--fields` e não lança worklog: para worklog usar o MCP/conector Atlassian.
- Conferir o site certo (`<empresa>.atlassian.net`): MCP apontado para site errado devolve busca vazia.

## Confluence
Conector Atlassian (claude.ai) ou MCP `atlassian`.

## Reuniões
- **Fellow** (MCP): `search_meetings`, `get_meeting_summary`, `get_meeting_transcript`, `get_action_items`. `fellow.link/XXXX` não abre por fetch: casar pelo `meeting_link` com `scripts/fellow_extrair.py`.
- **Roam** (MCP): `meeting_list`, `meeting_info`, `meeting_transcript`, chat. Links `ro.am/share/...` abrem no navegador embutido. MCP pode exigir aprovação de admin da organização.
- **Microsoft 365** (MCP): agenda Outlook, chats Teams, e-mail (só leitura).

## Artifacts / tarefas agendadas
- Dashboard: `Artifact` + `ArtifactData` (ver `docs/dashboard.md`).
- Tarefas agendadas: tools `scheduled-tasks` do app desktop (prompts em `scripts/tarefa-agendada-agenda.md`).
