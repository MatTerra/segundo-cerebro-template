# Dashboard Agenda

Painel no claude.ai (Artifact do tipo **Dashboard**) com as tarefas e os prazos do vault.
Dados gerados por `scripts/agenda_json.py`; nada é digitado à mão no painel.
Atualização: `scripts/atualizar-agenda.md` (ao fim de sessões que mudam tarefas/marcos, via `/fechar`, e por tarefa agendada).

## Dados

### Dataset `tarefas` (arquivo `agenda.json`)
Uma linha por tarefa no formato do plugin Tasks em `projetos/**/*.md` e `inbox.md`:

| campo | conteúdo |
|---|---|
| `id` | sha1 curto de arquivo + texto (estável entre execuções enquanto o texto não muda) |
| `projeto` | pasta em `projetos/` (ou `inbox`) |
| `arquivo` | caminho relativo da nota |
| `texto` | texto da tarefa sem datas, tags e colchetes de wikilink |
| `prazo` / `agendado` / `concluido` | datas de `📅` / `⏳` / `✅` (vazio se não houver) |
| `feito` | true/false |
| `quem` | `Eu` (`#eu`), `aguardando <pessoa>` (`#aguardando/<pessoa>`), `bloqueado` (`#bloqueado`) ou vazio |

### Dataset `marcos` (arquivo `marcos.json`)
Uma linha por item da lista `marcos:` no frontmatter de cada hub `projetos/<slug>/<slug>.md`:

```yaml
marcos:
  - "2027-03-31 | prazo | Homologação | contrato de 2027-01-10"
```
Formato: `"YYYY-MM-DD | tipo | frente | nota"`. Campos gerados: `id, projeto, frente, data, tipo, nota`.

Tipos:
- `lancamento` — data de entrega de um **projeto separado** (contrato próprio) combinada com o cliente.
- `prazo` — data limite de item dentro de uma frente (sustentação, melhoria, homologação).
- `previsao` — estimativa, sem compromisso.
- `evento` — data marcada sem entrega (reunião de kickoff, treinamento, auditoria).

## Criar (uma vez, em `/init-segundo-cerebro`, com ok do dono)
1. Gerar os dados numa pasta temporária fora do vault:
   `python -I -X utf8 scripts/agenda_json.py <tmp>/agenda.json <tmp>/marcos.json`
2. `Artifact` `action: "quickstart"`, `intent: "other"` (painel de dados). O resultado indica o tipo Dashboard; criar a partir dele (`type_url`) com título `Agenda <nome do dono>` e seguir as instruções que o tipo devolve.
3. Dois datasets do tipo arquivo, com estes ids e textos:
   - `tarefas` — título "Tarefas do segundo cérebro", fonte `agenda.json`, `staleAfterHours: 72`.
   - `marcos` — título "Prazos das frentes", fonte `marcos.json`, `staleAfterHours: 72`.
   Campo `schedule`: descrever a cadência real (ex.: "Dias úteis 07:30 e 13:30 e ao fim das sessões que mudam o vault").
4. Visões sugeridas (pedir ao tipo; ajustar ao gosto do dono):
   - Indicadores: tarefas abertas, atrasadas (`prazo` < hoje e não `feito`), vencendo em 7 dias, `#eu` sem data, aguardando outros.
   - Tabela "Atrasadas e vencendo": abertas com `prazo` ≤ hoje+7, ordenadas por `prazo`, colunas `prazo, projeto, texto, quem`.
   - Linha do tempo dos `marcos` (próximos 90 dias), cor por `tipo`.
   - Barras: tarefas abertas por `projeto`, empilhadas por `quem`.
   - Tabela "Aguardando outros": `quem` começa com `aguardando`.
   - Concluídas na semana (`concluido` ≥ segunda-feira).
5. Gravar a URL do painel em `CLAUDE.md` > Configuração e no topo de `scripts/atualizar-agenda.md`.
6. Oferecer fixar no menu lateral do claude.ai (`Artifact` `pin`) só se o dono quiser.

## Atualizar
Ver `scripts/atualizar-agenda.md`. Nunca editar a página nem as visões ao atualizar dados: só trocar a fonte dos datasets.
