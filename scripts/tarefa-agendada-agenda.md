# Prompts das tarefas agendadas

Criadas por `/init-segundo-cerebro` com o tool `create_scheduled_task` (app desktop do Claude). Trocar `{{...}}` antes de criar.

## atualizar-agenda (sugestão: `30 7,13 * * 1-5`)

```
Atualize os dados do dashboard Agenda ({{URL_DASHBOARD}}) a partir do vault Obsidian em {{CAMINHO_VAULT}}.

Siga exatamente o procedimento do arquivo {{CAMINHO_VAULT}}/scripts/atualizar-agenda.md (git pull; rodar `python -I -X utf8 scripts/agenda_json.py <tmp>/agenda.json <tmp>/marcos.json` com os arquivos numa pasta temporária fora do vault; enviar os dois JSON como assets do dashboard; atualizar os datasets `tarefas` e `marcos` com ArtifactData batch usando if_version; só então apagar os assets antigos).

Regras:
- Não altere a página (index.html) nem outros documentos do dashboard.
- Não faça commit nem edite notas do vault.
- Se o `git pull` falhar ou o script der erro, pare e diga o erro no resumo, sem tocar no dashboard.
- Resumo final em uma linha: quantas tarefas e marcos foram enviados, ou o erro.
```

> [!warning] A primeira execução agendada pode parar pedindo aprovação para `Artifact`/`ArtifactData`. Abrir a execução uma vez e aprovar; depois conferir se o painel está de fato atualizando.

## esquecidos-semanal (opcional; sugestão: `0 8 * * 1`)

```
Trabalhe no vault Obsidian em {{CAMINHO_VAULT}} (leia o CLAUDE.md dele primeiro e siga as convenções).

1. `git pull` no vault.
2. Execute a skill `/esquecidos` (.claude/skills/esquecidos/SKILL.md no vault) com as orgs e projetos da Configuração do CLAUDE.md.
3. Compare com o último diário que tenha a seção "PRs/issues esquecidos" e destaque o que continua parado e o que foi resolvido.
4. Registre a seção "## PRs/issues esquecidos (varredura YYYY-MM-DD)" no diario/YYYY-MM-DD.md de hoje (crie de templates/diario.md se não existir). Ações do dono viram tarefas `#eu` no hub do projeto certo; marque ✅ as que já se resolveram.
5. Commit e push: `git add -A && git commit -m "Varredura semanal de PRs/issues esquecidos" && git push`.

Somente leitura no GitHub e Jira: nunca comentar, aprovar, mergear, fechar PR nem transicionar card. Termine com um resumo de até 10 linhas dos itens mais críticos.
```
