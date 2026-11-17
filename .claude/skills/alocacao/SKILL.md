---
name: alocacao
description: Relatório de alocação da equipe gerado do vault - frentes por gestor com dev e prazo, em especificação, backlog, sem dono/sem prazo, capacidade (ausências, devs livres) e Gantt dos devs em 6 meses. Publica e mantém a página no claude.ai. Use para "/alocacao", "relatório de alocação", "o que está no colo de cada um", "quem está livre", "o que não está alocado/sem prazo", "pauta de gestão", "gantt da equipe", e quando o dono mudar dev, gestor, prazo ou ausência de uma frente.
argument-hint: "[--texto] [--projetos a,b]"
---

# /alocacao

Dados: `alocacao:` no frontmatter dos hubs + `equipe.md` na raiz. Formato e regras em `docs/alocacao.md`.
Script: `scripts/alocacao.py` (só lê o vault; HTML ou `--texto`). Página: URL em CLAUDE.md > Configuração > "Página de alocação".

## Pergunta pontual ("quem está livre?", "o que está sem prazo?")
`python -I -X utf8 scripts/alocacao.py --texto` na raiz do vault e responder a partir da saída. Não reler hubs.

## Mudança dita pelo dono ("Fulano pega X a partir de segunda, prazo sexta")
1. Datas absolutas (segunda = próxima segunda; prazo "5 dias úteis" conta só dias úteis e pula os feriados de `equipe.md`). Feriado no prazo: avisar em uma linha.
2. Editar a linha certa de `alocacao:` no hub da frente (uma linha por dev; dev novo em paralelo = linha nova). Ausência: `equipe.md`. Pessoa nova ou que saiu: `equipe.md > Pessoas`.
3. Prazo de entrega combinado com cliente também vai em `marcos:` (dashboard Agenda).
4. Linha no Log do hub e no diário do dia. Seguir para "Publicar".

## Publicar (relatório completo, ou depois de mudança)
1. `git pull --rebase -q`. Sem `equipe.md`: criar de `templates/equipe.md` e perguntar ao dono a lista de pessoas.
2. `python -I -X utf8 scripts/alocacao.py <scratchpad>/alocacao.html --titulo "<título da Configuração>" [--gestores A,B]` (ordem das colunas, se a Configuração disser).
3. Ler os avisos do script (`estado inválido`). Corrigir no hub e gerar de novo.
4. URL configurada: `Artifact` publish com `url` e `file_path` do HTML (atualiza no mesmo link). Sem URL: publicar novo (ícone `calendar`), gravar a URL em CLAUDE.md > Configuração e commitar.
5. Responder com o link e o resumo de `--texto` em poucas linhas (sem dono, sem prazo, livres, vencidos).

## Regras
- A página é gerada: nunca editar o HTML publicado à mão. Correção de conteúdo = corrigir `alocacao:`/`equipe.md` e gerar de novo.
- Prazo realinhado com o cliente em reunião vale mais que o antigo: atualizar a linha, não alertar o antigo.
- Sem segredo nem dado pessoal (só nome e papel).
