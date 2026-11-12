---
name: worklog
description: Reconstrói o dia (ou a semana) do dono a partir de commits, reuniões, diário e cards Jira tocados, propõe a tabela de worklog por card e só lança no Jira após "ok" explícito. Use para "lançar horas", "worklog", "o que fiz ontem/hoje/na semana".
argument-hint: "[YYYY-MM-DD | YYYY-MM-DD..YYYY-MM-DD]"
---

# /worklog

Escrita no Jira é externa: **nada é lançado sem "ok" explícito do dono na conversa.**
Sem Jira configurado: fazer só os passos 1–4 (reconstrução do dia no diário).

## 1. Período
Padrão: hoje. Datas relativas → absolutas. Semana = seg..sex. Conferir se o dia já tem `✅ lançado` no diário (não lançar duas vezes).
Ver o que já existe no Jira para o período:
`acli jira workitem search --jql "worklogAuthor = currentUser() AND worklogDate >= <ini> AND worklogDate <= <fim>" --fields "key,summary" --limit 50`.

## 2. Evidência (em paralelo)
- **Git**: para cada repo com `.git` na pasta de repositórios da Configuração:
  `git -C <repo> log --all --author="<nome do autor git>" --since="<ini> 00:00" --until="<fim> 23:59" --format="%ad|%s|%D" --date=iso`
  Chave Jira no branch/mensagem (ex.: `ABC-123`) → card.
- **Reuniões**: fonte configurada (Fellow `search_meetings`, Roam `meeting_list`, agenda Outlook) no período: título, início, fim. Duração = fim − início.
- **Vault**: `diario/<dia>.md` (Feito) e `git log --since --until` do próprio vault (trabalho de gestão/planejamento).
- **Jira**: cards que o dono atualizou ou comentou no período.

## 3. Mapear para cards
- Card próprio do trabalho quando houver.
- Senão, card balde de [[buckets-worklog]], respeitando as regras de lá (tetos diários, para onde vai o excedente).
- Reunião de status/cliente → card da frente ou balde gerencial, conforme [[buckets-worklog]].
- Horas: blocos de 0,5 h; total do dia ~ jornada do dono. Commits sem duração: estimar pelo intervalo entre commits e dizer que é estimativa.

## 4. Propor
Escrever a tabela em `diario/<dia>.md` > Worklog sugerido (um bloco por dia):
| card | horas | o quê |
|---|---|---|
Mostrar ao dono com total por dia e as lacunas (horas sem evidência). Perguntar o que falta; não inventar.

## 5. Lançar (só após "ok")
- O `acli` não tem comando de worklog. Lançar por MCP Atlassian (`addWorklogToJiraIssue` ou equivalente), uma chamada por linha: card, tempo (`2h 30m`), início (`YYYY-MM-DDTHH:MM:SS.000<offset do fuso>`), comentário = "o quê".
- Se o MCP falhar: entregar a tabela pronta para o dono lançar à mão e dizer o erro.
- Conferir depois com a busca `worklogAuthor` do passo 1.
- Depois: marcar o bloco do diário com `✅ lançado YYYY-MM-DD`; regra nova de mapeamento → `ref/buckets-worklog.md`; `/fechar`.
