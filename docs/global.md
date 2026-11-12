# Contexto do segundo cérebro em todas as conversas

O `CLAUDE.md` do vault só vale para sessões abertas dentro do vault. Para que uma sessão em qualquer repo ou pasta também saiba das frentes, decisões e pendências, três peças vão para o nível do usuário (`~/.claude/`):

| peça | fonte no vault | destino | quando age |
|---|---|---|---|
| Bloco de instruções | `global/CLAUDE.md` | `~/.claude/CLAUDE.md` (entre marcadores `segundo-cerebro:inicio/fim`) | sempre carregado: diz onde está o vault e quando consultar/registrar |
| Skill `segundo-cerebro` | `global/skills/segundo-cerebro/` | `~/.claude/skills/segundo-cerebro/` | conversa sobre projeto, cliente, card, prazo, reunião, pessoa; "anota no segundo cérebro" |
| Hook `SessionStart` | `scripts/contexto_sessao.py` | `~/.claude/settings.json` | início de cada sessão: injeta o resumo do hub ligado ao repo atual |

## Instalar / atualizar / remover
```bash
python -I -X utf8 scripts/instalar_global.py --dry-run
python -I -X utf8 scripts/instalar_global.py
python -I -X utf8 scripts/instalar_global.py --remover
```
Idempotente: rodar de novo depois de editar `global/` ou de mover o vault. Faz `.bak` de `CLAUDE.md` e `settings.json`. Preserva o resto desses arquivos e outros hooks.

## Como o hook acha o projeto
- Sobe da pasta atual até a raiz do git e compara os nomes (pasta atual, raiz e até 2 pais) com `repos:` do frontmatter de cada hub `projetos/<slug>/<slug>.md`.
- Achou: status, prioridade, jira, Estado (6 linhas), até 8 tarefas abertas e 3 linhas de Log, por hub (máx. ~3500 caracteres).
- Não achou: só o Foco do `agora.md`.
- Dentro do vault: não injeta nada.
- Qualquer erro: sai em silêncio (nunca derruba a sessão). Não faz `git pull` (seria lento); o conteúdo é o da cópia local.

Testar: `python -I -X utf8 scripts/contexto_sessao.py --cwd <pasta de um repo>`.

## Privacidade
O hook injeta conteúdo do vault no contexto de qualquer sessão. Não usar em máquina compartilhada, e manter o vault sem segredos (regra que já vale para ele).
