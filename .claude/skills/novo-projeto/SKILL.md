---
name: novo-projeto
description: Cria uma frente de trabalho nova no segundo cérebro (pasta projetos/<slug>/ com hub, subnotas e reuniões) a partir do que o dono passar - links de reunião, pasta de docs, repo, chave Jira, cliente. Use quando ele disser "vamos te contextualizar/atualizar do projeto X" e X não tiver pasta em projetos/.
argument-hint: "<nome> [jira KEY] [repo] [pasta docs] [links de reunião...]"
---

# /novo-projeto

## 1. Coletar (perguntar só o que faltar, numa mensagem)
- nome e cliente; slug kebab-case sem acento (único no vault: `ls projetos arquivo`)
- chave(s) Jira (`jira: [KEY]`), repos (pasta de repositórios da Configuração), pasta de docs do cliente (`pasta_docs:`, fora do vault)
- links de reuniões, prioridade 1–3, prazos conhecidos
Já existe pasta? Não criar: atualizar o hub existente.

## 2. Levantar
Em paralelo quando possível:
- Reuniões: seguir a skill `reuniao` (passos 2–3) para cada link; mais antigas só se necessário.
- Jira: `acli jira workitem search --jql "project = <KEY> ORDER BY updated DESC" --fields "key,issuetype,summary,status,assignee" --limit 50`. Ler para contexto; **não copiar backlog** para o vault.
- Repo: `git -C <repo> log --since=60.days --oneline | head -30`, branches e PRs abertos (`gh pr list`). Fatos técnicos estáveis vão para subnota `-tecnico`.
- Pasta de docs: listar arquivos; ler contrato/spec/proposta para prazos e escopo.

## 3. Criar
`projetos/<slug>/<slug>.md` a partir de `templates/projeto.md`:
- frontmatter completo (`tipo, status, prioridade, jira, repos, pasta_docs, cliente, atualizado, confianca, tags, marcos`). `confianca: inferido` quando veio de git/memória sem o dono confirmar.
- Seções: Mapa, Contexto, Estado, Próximos passos (tarefas Tasks), Decisões, Log.
- Hub enxuto. Tema que cresce vira subnota `<slug>-<tema>.md` (de `templates/projeto-nota.md`): comum `-tecnico`, `-comercial`, `-regulatorio`.
- Reuniões em `projetos/<slug>/reunioes/`.
- Prazos de contrato/homologação em `marcos:` (formato em `docs/dashboard.md`).
- Pessoas novas em `ref/pessoas.md`; repo novo em `ref/repos-e-sistemas.md`.

## 4. Conectar
- `agora.md`: incluir a frente na lista certa (foco ou demais), sem passar de 80 linhas.
- Perguntas que ficaram: `> [!question]` no hub e lista curta ao dono no fim.
- `/fechar`.
