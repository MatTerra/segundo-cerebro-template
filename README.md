# Segundo cérebro (template)

Vault Obsidian + Claude Code para acompanhar frentes de trabalho: reuniões, tarefas, decisões, prazos, horas.
Quem mantém o vault é o Claude; você conversa, ele registra, lembra e cobra.

## O que vem
- `CLAUDE.md` — protocolo que o Claude segue no vault (convenções, estrutura, regras).
- `.claude/skills/` — comandos:
  - `/init-segundo-cerebro` — configuração inicial (rodar primeiro);
  - `/hoje` — pendências do dia;
  - `/reuniao <link|tema>` — registra reunião (Fellow, Roam, Teams ou relato);
  - `/novo-projeto` — cria uma frente de trabalho;
  - `/briefing <tema>` — pesquisa em fonte primária;
  - `/esquecidos` — PRs e cards parados;
  - `/worklog [data]` — reconstrói o dia e propõe lançamento de horas no Jira;
  - `/fechar` — commit, push e atualização do dashboard.
- `scripts/` — `hoje.py` (pendências), `agenda_json.py` (dados do dashboard), `fellow_extrair.py` (Fellow), procedimento e prompts de tarefa agendada.
- `docs/` — `funcionamento.md` (como o sistema funciona), `dashboard.md` (criação e dados do painel Agenda), `fontes.md` (Jira, GitHub, reuniões).
- `templates/`, `ref/`, `agora.md`, `inbox.md` — esqueletos vazios.

## Requisitos
- [Claude Code](https://claude.com/claude-code) (app desktop recomendado: tem Artifacts para o dashboard e tarefas agendadas).
- git e Python 3.10+.
- Opcionais: [Obsidian](https://obsidian.md) com plugins Tasks e Dataview; `gh` (GitHub CLI); `acli` (Atlassian CLI); MCP/conectores de Fellow, Roam, Microsoft 365, Atlassian.

## Começar
1. Copiar este template para uma pasta sua (ex.: `git clone <este repo> meu-segundo-cerebro`).
2. Abrir a pasta no Claude Code.
3. Rodar `/init-segundo-cerebro` e responder às perguntas. Ele configura o `CLAUDE.md`, cria o repositório privado, os primeiros projetos, o dashboard e a tarefa agendada (pedindo ok em cada passo externo).
4. No dia a dia: `/hoje` de manhã, `/reuniao` depois de cada reunião, `/fechar` no fim.

## Privacidade
O vault vai guardar informação de trabalho: manter o repositório **privado**. Nunca registrar senhas, tokens ou dados pessoais de clientes (o `CLAUDE.md` já instrui o Claude a não fazer isso).
