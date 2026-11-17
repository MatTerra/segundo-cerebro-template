# Como o segundo cérebro funciona

## Ideia
- O vault é a memória de trabalho do Claude sobre as frentes do dono: estado, decisões, pendências, contexto que o tracker não guarda.
- Quem lê é o Claude. O dono conversa; o Claude registra na hora e lembra o dono do que importa (prazos, ações `#eu`).
- Tudo em Markdown + git: legível no Obsidian, versionado, sincronizado entre máquinas por `git pull`/`push`.

## Onde vai cada coisa
| informação | lugar |
|---|---|
| Foco da semana, top prioridades, perguntas abertas | `agora.md` (< 80 linhas) |
| Algo solto, sem frente definida | `inbox.md` (triar depois) |
| Estado, tarefas, decisões, log de uma frente | hub `projetos/<slug>/<slug>.md` |
| Detalhe técnico/comercial que cresceu | subnota `projetos/<slug>/<slug>-<tema>.md` |
| Uma reunião | `projetos/<slug>/reunioes/YYYY-MM-DD-<titulo>.md` |
| Fato durável (pessoas, repos, regras de horas, normas) | `ref/` |
| O que aconteceu no dia, worklog sugerido | `diario/YYYY-MM-DD.md` |
| Frente encerrada | `arquivo/<slug>/` |
| Backlog, estimativa, descrição de card | **no tracker (Jira)**, não no vault |
| Segredo, senha, token, dado pessoal de cliente | **em lugar nenhum do vault** |

## Ciclo de uma frente
1. `/novo-projeto` cria a pasta e o hub (`status: ativo`, `confianca: inferido` se veio só de git).
2. `/reuniao` alimenta: nota da reunião → tarefas e decisões no hub → Log → diário.
3. Mudou o estado: atualizar Estado, `atualizado:`, linha no Log (mais recente em cima).
4. Prazo combinado: `marcos:` no frontmatter (aparece no dashboard e no `/hoje`).
5. Concluiu: `status: concluido`, mover a pasta para `arquivo/`, tirar do `agora.md`.

## Ciclo do dia
- Início: `/hoje` (pendências do vault + reuniões + cards).
- Durante: cada informação nova vai para o lugar certo na mesma hora.
- Reuniões: `/reuniao <link>` logo depois.
- Ao longo do dia: `/turno entrei 8h`, `/turno almoço 12h30`, `/turno saí agora` (grava, commita e dá push só do diário).
- Fim: `/fechar` (commit, push, dashboard). Se lança horas: `/worklog` (usa a linha `Turno:` como total do dia).
- Semanal: `/esquecidos` (PRs e cards parados); revisar `inbox.md` e `confianca: inferido`.

## Turno (horários do dia)
`/turno <texto livre>` registra quando o dia começou, pausou, voltou e terminou. Fora do vault, a skill global `segundo-cerebro` chama o mesmo script pelo caminho absoluto.

| pedido | efeito |
|---|---|
| `/turno entrei 0800 e pretendo almoçar 1230` | abre 08:00 e marca a pausa prevista `~12:30` |
| `/turno voltei 13h30` | confirma a pausa prevista e abre 13:30 |
| `/turno saí agora` | fecha o intervalo aberto na hora atual |
| `/turno` | só mostra o dia |
| `/turno desfaz` | remove a última marcação |
| `/turno ontem saí 18h` | outro dia (`ontem`, `anteontem` ou `YYYY-MM-DD`) |

- Horários aceitos: `08:00`, `8:00`, `0800`, `8h`, `8h30`, `8`, `agora`. Palavras como entrei/comecei/voltei abrem; almoço/pausa/saí/parei fecham; pretendo/vou/previsto marcam como previsto. Sem palavra, alterna: abre se não há intervalo aberto, fecha se há.
- Linha gravada logo abaixo do título de `diario/YYYY-MM-DD.md` (cria o diário de `templates/diario.md` se faltar):
  `Turno: 08:00–12:30 · 13:30–~18:00 · total 9h00 (previsto)`. `~HH:MM` = previsto; `…` = aberto. O total conta o aberto até agora (só hoje) e o previsto como se fosse cumprido.
- Correções: novo "entrei" com intervalo aberto corrige o início; novo "saí" corrige o último fim. Recusa fim antes do início e início antes do fim anterior (sai com `ERRO` e não grava).
- Git: `pull --ff-only`, depois commit e push **só** do arquivo do diário. `--sem-git` pula (testes).
- Custo: a skill roda no modelo `haiku` e recebe a saída do script já pronta (injeção `` !`comando` ``), sem chamada de ferramenta. Script: `scripts/turno.py` (docstring com exemplos).
- `/worklog` usa essa linha como total do dia.

## Tarefas
Formato do plugin Tasks, sempre no hub (ou `inbox.md`):
```
- [ ] Enviar proposta revisada 📅 2027-02-10 #eu
- [ ] Retorno do cliente sobre o escopo ⏳ 2027-02-05 #aguardando/fulano
- [x] Revisar contrato ✅ 2027-02-01
```
- `📅` prazo, `⏳` agendado (quando olhar de novo), `✅` concluído.
- `#eu` = ação humana do dono (o Claude não pode fazer: ligar, decidir, aprovar, assinar).
- `#aguardando/<pessoa>` = depende de outro. `#bloqueado` = travado sem dono claro.
- `scripts/hoje.py` e `scripts/agenda_json.py` dependem exatamente dessas marcas.

## Decisões e perguntas
- `> [!decision] YYYY-MM-DD: <decisão>. Motivo: <...> (fonte: [[nota]])` no hub.
- `> [!question]` para o que só o dono responde. Perguntar na primeira oportunidade e apagar o callout quando respondido.
- `confianca: inferido` em hub = conteúdo deduzido; confirmar com o dono e trocar para `confirmado`.

## Escrita externa
Worklog, comentário em card, transição, criação de card, mensagem, e-mail, publicação: **só com "ok" explícito do dono na conversa**. Propor primeiro (tabela, rascunho), executar depois.

## Alocação da equipe
Ver `docs/alocacao.md`. Dev, gestor e período de cada frente em `alocacao:` no hub; pessoas, ausências e feriados em `equipe.md`. `/alocacao` publica a página (colunas por gestor, sem dono, sem prazo, Gantt) e `/alocacao --texto` responde no chat.

## Dashboard
Ver `docs/dashboard.md`. Gerado dos mesmos dados que o `/hoje`; atualizado por `/fechar` e por tarefa agendada.

## Manutenção
- `agora.md` passou de 80 linhas: mover detalhe para os hubs.
- Hub grande demais: quebrar em subnotas `<slug>-<tema>.md`.
- Skill fazendo algo errado de forma recorrente: corrigir o `SKILL.md` (com data do motivo), não só a resposta.
- Gotcha de ambiente novo: seção Gotchas do `CLAUDE.md`.
