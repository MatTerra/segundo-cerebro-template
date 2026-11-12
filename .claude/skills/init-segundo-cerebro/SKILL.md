---
name: init-segundo-cerebro
description: Configura um segundo cérebro novo a partir deste template - coleta dados do dono e das fontes (reuniões, Jira, GitHub, repos), preenche a Configuração do CLAUDE.md, cria as notas iniciais, o repositório git, o dashboard Agenda, a tarefa agendada e a integração global (contexto do vault em todas as conversas do Claude Code). Use na primeira sessão do vault, ou quando o dono disser "configura o segundo cérebro", "init", "começar do zero".
argument-hint: "[--refazer]"
---

# /init-segundo-cerebro

Roda uma vez por vault. Idempotente: se um passo já está feito, conferir e seguir.
Escrita externa (repo remoto, dashboard, tarefa agendada) só com "ok" explícito do dono.

## 0. Já configurado?
- `grep -c "{{" CLAUDE.md`. Zero e sem `--refazer`: dizer que já está configurado, mostrar a seção Configuração e perguntar o que mudar. Parar.

## 1. Pré-requisitos (conferir, não instalar sem ok)
Rodar em paralelo e montar uma tabela ok/falta:
- `git --version`, `python --version` (ou `py`), `gh auth status`, `acli --version` (Windows: `$LOCALAPPDATA/Microsoft/WinGet/Links/acli.exe`).
- MCPs disponíveis na sessão (ToolSearch): Fellow (`search_meetings`), Roam (`meeting_list`), Microsoft 365/Teams, Atlassian (`addWorklogToJiraIssue`), Artifact, scheduled-tasks.
- Faltou algo: explicar o que perde (ex.: sem `acli` → `/esquecidos` e `/worklog` sem Jira) e como instalar. Não bloquear: o vault funciona só com git + Python.

## 2. Coletar (uma mensagem só; AskUserQuestion para escolhas fechadas)
- Nome e como quer ser chamado; idioma das respostas; fuso.
- Pasta onde ficam os repositórios de código (ex.: `C:\Projetos`, `~/code`).
- Fonte de reuniões: Fellow, Roam, Teams, nenhuma.
- Tracker: Jira (site `xxx.atlassian.net` + chaves de projeto de interesse) ou nenhum. Usa cards "balde" para lançar horas sem card próprio? Quais e com que regras?
- GitHub: orgs e usuário a acompanhar em `/esquecidos`; filtro de time (prefixos de título, repos, autores) se a org for grande.
- Repositório remoto do vault: criar privado no GitHub (`gh repo create <nome> --private --source . --push`, só com ok) ou outro remoto, ou só local.
- Preferências de trabalho (respostas curtas? o que nunca fazer?) → [[como-trabalhar]].
- Frentes de trabalho atuais (nome, cliente, chave Jira, repo, prazo) — viram projetos no passo 5.

## 3. Preencher
- `CLAUDE.md` > Configuração: trocar cada `{{...}}`. Fonte/tracker ausente: escrever `nenhum` e, nas skills que dependem dele, a skill já pula a etapa.
- `ref/como-trabalhar.md`: preferências, com data.
- `ref/buckets-worklog.md`: cards balde e regras (se houver Jira).
- `ref/pessoas.md`, `ref/repos-e-sistemas.md`: o que já veio na coleta.
- `agora.md`, `inbox.md`: `atualizado:` = hoje.
- `diario/<hoje>.md` de `templates/diario.md` com "Vault configurado" em Feito.
- Apagar o callout "Vault ainda não configurado?" do topo do `CLAUDE.md`.
- `README.md` é do template: substituir por 3 linhas ("Segundo cérebro de <nome>. Ver CLAUDE.md.").

## 4. Git
- Se a pasta veio de `git clone` do template: `git remote remove origin` (o histórico do template não importa; opcionalmente `rm -rf .git && git init`).
- `git init` se preciso; branch `main`; commit inicial "Vault configurado".
- Remoto conforme o passo 2 (só com ok). Confirmar que é **privado**: `gh repo view --json visibility`.

## 5. Projetos iniciais
Para cada frente citada: `/novo-projeto` (pode ser em lote, pedindo só o que faltar). Frente sem detalhe: hub mínimo com `confianca: inferido` e `> [!question]`.
Opcional, com ok: varrer `git log --since=60.days` dos repos da pasta configurada para sugerir frentes esquecidas (vai para `inbox.md`, não vira projeto sozinho).

## 6. Dashboard Agenda (opcional, com ok)
Seguir `docs/dashboard.md` > Criar. Gravar a URL na Configuração do `CLAUDE.md` e no topo de `scripts/atualizar-agenda.md`.

## 7. Tarefa agendada (opcional, com ok)
Criar com o tool `create_scheduled_task` (scheduled-tasks) usando o prompt de `scripts/tarefa-agendada-agenda.md`, com caminho do vault e URL do dashboard preenchidos. Sugestão: `30 7,13 * * 1-5`. Opcional também: `/esquecidos` semanal (prompt no fim do mesmo arquivo). Gravar o id em Configuração.

## 8. Contexto em todas as conversas (recomendado, com ok)
Liga o vault às sessões do Claude Code fora dele (qualquer repo, qualquer pasta). Explicar as três peças e pedir ok:
- bloco no `~/.claude/CLAUDE.md` (sempre carregado; diz onde está o vault e quando consultar/registrar);
- skill global `~/.claude/skills/segundo-cerebro/` (consultar e registrar de fora do vault);
- hook `SessionStart` em `~/.claude/settings.json` que roda `scripts/contexto_sessao.py` e injeta o resumo do hub cujo `repos:` contém a pasta atual (ou o Foco do `agora.md`).
Rodar `python -I -X utf8 scripts/instalar_global.py --dry-run`, mostrar a saída, e só então sem `--dry-run`. Idempotente; faz `.bak` de `CLAUDE.md` e `settings.json`; `--remover` desfaz.
Testar: `python -I -X utf8 scripts/contexto_sessao.py --cwd <um repo ligado a um hub>`.
Mudou a pasta do vault: rodar o instalador de novo.

## 9. Obsidian (ação humana, listar no fim)
- Abrir a pasta como vault no Obsidian.
- Instalar plugins da comunidade **Tasks** e **Dataview** (as consultas do `agora.md` usam Tasks).
- Opcional: plugin Obsidian Git para sincronizar quando editar fora do Claude.
Registrar como tarefas `#eu` em `inbox.md` o que ficar pendente.

## 10. Fechar
`/fechar`. Resumo final: o que foi configurado, o que ficou pendente (`#eu`), e os 3 comandos para começar: `/hoje`, `/reuniao <link>`, `/novo-projeto`.
