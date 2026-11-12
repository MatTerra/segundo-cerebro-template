# Protocolo do segundo cérebro (para Claude)

Vault Obsidian versionado em git. Leitor principal: Claude. O dono raramente lê os `.md`.
Otimizar para recuperação por agente, não para estética.

> [!warning] Vault ainda não configurado?
> Se a seção **Configuração** abaixo ainda tiver `{{...}}`, rodar `/init-segundo-cerebro` antes de qualquer outra coisa.

## Configuração (preenchida por `/init-segundo-cerebro`)
- Dono: {{NOME}} (tratar por {{APELIDO}}). Idioma: {{IDIOMA}}. Fuso: {{FUSO}}.
- Vault: `{{CAMINHO_VAULT}}`, remoto `{{REMOTO_GIT}}`.
- Pasta dos repositórios de código: `{{PASTA_REPOS}}` (evidência de trabalho por `git log`).
- Tag de ação humana: `#eu` (fixa; scripts dependem dela).
- Reuniões: {{FONTE_REUNIOES}} (fellow | roam | teams | nenhuma).
- Tarefas formais: {{TRACKER}} (jira | nenhum). Site: `{{JIRA_SITE}}`. Projetos de interesse: {{JIRA_PROJETOS}}.
- GitHub: orgs {{GITHUB_ORGS}}; usuário {{GITHUB_USER}}.
- Dashboard Agenda: {{URL_DASHBOARD}} (ver `scripts/atualizar-agenda.md`).
- Tarefa agendada do dashboard: {{TAREFA_AGENDADA}}.
- Integração global (contexto em todas as conversas): {{INTEGRACAO_GLOBAL}} (instalada | não). Ver `docs/global.md`.

## Ao iniciar sessão que envolva acompanhamento
1. `git pull` (pode haver edição feita pelo Obsidian em outra máquina).
2. Ler [[agora]] (foco + pendências abertas) e o diário mais recente em `diario/`.
3. Ler só os hubs `projetos/<slug>/<slug>.md` relevantes ao pedido; abrir subnotas só se precisar do detalhe.
4. Ler [[como-trabalhar]] (preferências do dono).

## Skills do vault (`.claude/skills/`, usar em vez de improvisar)
- `/init-segundo-cerebro`: configuração inicial (uma vez por vault).
- `/reuniao <link|tema> [--cards]`: reunião → nota em `reunioes/`, tarefas no hub, Log, diário.
- `/novo-projeto`: pasta + hub + subnotas + reuniões para frente nova.
- `/hoje`: pendências do dia (`scripts/hoje.py` + fontes externas configuradas).
- `/worklog [data]`: reconstruir dia, propor tabela de horas, lançar só com "ok".
- `/briefing <tema>`: pesquisa em fonte primária → `ref/`, fato vs inferência.
- `/esquecidos`: PRs e cards parados; retrato no diário, ações `#eu` no hub.
- `/fechar`: Log/diário, commit, push, dashboard se tarefas/marcos mudaram. Rodar ao fim de toda interação com mudanças.
- Fora do vault: skill global `segundo-cerebro` (fonte em `global/`, instalada em `~/.claude/` por `scripts/instalar_global.py`).
- `repos:` dos hubs precisa ter o nome exato da pasta do repo: é por ele que o hook liga uma sessão fora do vault ao projeto.

Guia completo de funcionamento: `docs/funcionamento.md`. Dashboard: `docs/dashboard.md`.

## Gotchas de ambiente
- Python no Windows: rodar com `-X utf8` (ou `PYTHONIOENCODING=utf-8`); cp1252 quebra com acento/emoji.
- Fellow: `fellow.link/XXXX` não abre por fetch/navegador; casar pelo `meeting_link` do `search_meetings` (`scripts/fellow_extrair.py`).
- `acli` (Atlassian CLI) não lança worklog: usar o MCP/conector Atlassian para isso.
- Tarefa agendada pode não conseguir publicar `Artifact` sem aprovação: conferir de vez em quando se o dashboard está de fato atualizando.
- `gh ... --jq` com aspas: usar Bash, não PowerShell 5.1.
- (Acrescentar aqui gotchas novos do ambiente do dono, com data.)

## Convenções Obsidian (usar sempre)
- Frontmatter YAML em toda nota. Campos de projeto: `tipo: projeto`, `status: ativo|bloqueado|aguardando|pausado|concluido`, `prioridade: 1-3` (1=alta), `jira: [KEY-123]`, `repos: [nome-pasta]`, `atualizado: YYYY-MM-DD`, `confianca: confirmado|inferido` (inferido = deduzido de git/memória, falta o dono confirmar), `marcos:` (prazos da frente).
- Links `[[nome-da-nota]]` entre projetos, refs, diário. Nome de arquivo = slug kebab-case, sem acento.
- Tarefas no formato do plugin Tasks: `- [ ] texto 📅 YYYY-MM-DD` (prazo), `⏳ YYYY-MM-DD` (agendado), `✅ YYYY-MM-DD` ao concluir, `#bloqueado` / `#aguardando/<pessoa>` / `#eu` (ação humana).
- Callouts: `> [!warning]` gotcha, `> [!decision]` decisão com data e motivo, `> [!question]` pergunta aberta para o dono.
- Tags: `#projeto/<slug>`, `#sistema/<repo>`.
- Datas absolutas sempre (nunca "ontem", "semana que vem").

## Estrutura
- `agora.md` — foco atual, top prioridades, perguntas abertas. Manter curto (<80 linhas); detalhe vai no projeto.
- `inbox.md` — captura bruta. Triagem: mover para projeto/ref e apagar do inbox.
- `projetos/<slug>/` — uma pasta por frente de trabalho.
  - `<slug>.md` = hub (`tipo: projeto`). Seções: Mapa, Contexto, Estado, Próximos passos (tarefas), Decisões, Log (datado, mais recente em cima). Hub enxuto: é o que se lê primeiro.
  - Subnotas `<slug>-<tema>.md` (`tipo: projeto-nota`, `projeto: "[[<slug>]]"`) quando um tema cresce. Prefixo do slug porque wikilink resolve pelo nome do arquivo, que precisa ser único no vault.
  - `reunioes/YYYY-MM-DD-<titulo>.md` (`tipo: reuniao`, `fonte:` link): uma por reunião. Pontos e decisões; tarefas vão para o hub.
  - Tarefas e decisões ficam **só no hub**. Subnota guarda detalhe e linka o hub.
  - Documentos para cliente (propostas, planilhas) ficam fora do vault, na pasta de `pasta_docs:` do hub.
- `ref/` — fatos duráveis (repos, convenções, buckets de horas, pessoas, preferências). Sem estado efêmero.
- `diario/YYYY-MM-DD.md` — log do dia: feito, decidido, travado, worklog sugerido.
- `arquivo/` — projetos concluídos (mover a pasta inteira, `status: concluido`).
- `templates/` — modelos. `scripts/` — utilitários Python. `docs/` — guias deste sistema.

## Regras de atualização
- Toda informação nova do dono: registrar no lugar certo NA MESMA hora, não no fim.
- Ao concluir algo: marcar tarefa `✅ data`, linha no Log do projeto e no diário do dia.
- Ao final de interação com mudanças: `/fechar` (commit + push + dashboard).
- Não guardar segredos, tokens, senhas, dados pessoais de clientes.
- Se `confianca: inferido`, perguntar ao dono na primeira oportunidade e atualizar.
- Fonte de verdade de tarefas formais = tracker (Jira). Aqui: contexto, decisões, pendências informais, o que o tracker não captura.
- **Não duplicar backlog** (lista de demandas, estimativas, descrição de card): fica no tracker. No vault só a chave e o que o tracker não guarda (decisão de abordagem, fato técnico, contexto do cliente).
- Escrita externa (worklog, comentário, transição de card, mensagem, e-mail): só com "ok" explícito do dono.

## Fontes externas
Ver `docs/fontes.md` para comandos de cada fonte (Jira via `acli`, GitHub via `gh`, Fellow/Roam/Teams via MCP, git local).

## Relação com a auto-memória do Claude
A memória do Claude Code (`~/.claude/projects/.../memory/`) guarda preferências de trabalho e gotchas técnicos por repo. Este vault guarda estado de projetos e acompanhamento. Gotcha técnico longo fica na memória; aqui só link/resumo.
