---
name: esquecidos
description: Varre PRs abertos no GitHub e cards do Jira que estão parados/esquecidos nas orgs e projetos configurados, cruza PR com card e registra o retrato no diário. Use para "PRs esquecidos", "o que está parado", "issues esquecidas", ou como varredura semanal.
---

# /esquecidos — PRs e issues parados

Só leitura: nunca comentar, aprovar, mergear, fechar PR nem transicionar card sem "ok" explícito.

## Escopo (da Configuração do `CLAUDE.md`)
- GitHub: orgs configuradas. Org grande e compartilhada: filtrar pelo time do dono (prefixos de chave Jira no título, repos de [[repos-e-sistemas]], autores de [[pessoas]]). Anotar em [[repos-e-sistemas]] os repos/times a ignorar.
- Ignorar PRs em repos **arquivados** (`archived:false` na busca, ou `gh repo view owner/repo --json isArchived`).
- Mais: PRs do próprio dono (`--author @me`) e com review pedida a ele (`--review-requested @me`).
- Jira: projetos de interesse configurados. Sem Jira: pular a parte de cards.

## Critério de "esquecido"
- PR não-draft sem atualização há > 7 dias; ou com `CHANGES_REQUESTED` sem push novo; ou `CONFLICTING`; ou review pedida ao dono há > 3 dias.
- Card em andamento / revisão / homologação sem update há > 14 dias. Status de espera proposital ("Stand By"): só contar.
- Cruzar: card em revisão + PR parado = gargalo de review (prioridade).

## Comandos (usar Bash; PowerShell 5.1 quebra as aspas do `--jq`)
```bash
ORGS="--owner ORG1 --owner ORG2"   # da Configuração
jq='.[] | "\(.updatedAt[0:10]) \(.repository.nameWithOwner)#\(.number) by \(.author.login) draft=\(.isDraft) \(.title)"'
gh search prs --state open --author "@me" $ORGS --limit 100 --json repository,number,title,updatedAt,isDraft,author --jq "$jq" | sort
gh search prs --state open --review-requested "@me" --limit 100 --json repository,number,title,updatedAt,isDraft,author --jq "$jq" | sort
gh search prs --state open $ORGS --archived=false --updated "<$(date -d '-7 days' +%F)" --limit 300 --json repository,number,title,updatedAt,isDraft,author --jq "$jq" | sort
# detalhe por PR
gh pr view N -R owner/repo --json reviewDecision,mergeable,createdAt,updatedAt,reviews
```
```bash
acli jira workitem search --jql 'project in (KEY1, KEY2) AND statusCategory = "In Progress" AND updated <= -14d ORDER BY updated ASC' --fields "key,status,assignee,summary" --limit 300 --csv
acli jira workitem search --jql 'assignee = currentUser() AND statusCategory != Done AND updated <= -14d' --fields "key,status,summary" --limit 100 --csv
```
`acli` não aceita `updated` em `--fields`.

## Saída
1. Seção `## PRs/issues esquecidos (varredura YYYY-MM-DD)` no `diario/YYYY-MM-DD.md`: tabela curta agrupada por ação (revisar, resolver conflito, decidir fechar, cobrar dono do PR).
2. Item que exige ação do dono vira tarefa `#eu` no hub do projeto certo (ou no `inbox.md`).
3. Comparar com o retrato anterior (último diário com essa seção): destacar o que continua parado e marcar `✅` o que se resolveu.
