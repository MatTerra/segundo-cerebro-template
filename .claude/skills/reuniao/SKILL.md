---
name: reuniao
description: Registra uma reunião no segundo cérebro a partir de link do Fellow (fellow.link), tema/título, magic minutes do Roam (ro.am/share), transcrição do Teams ou relato do dono. Cria a nota em projetos/<slug>/reunioes/, leva action items do dono ao hub, atualiza Log e diário. Use quando o dono mandar link de reunião, pedir "puxa/registra/incorpora a reunião X", ou pedir cards a partir de uma reunião (--cards).
argument-hint: "<fellow.link/... | ro.am/share/... | tema> [projeto] [--cards]"
---

# /reuniao

Entrada: um ou mais links/temas, opcionalmente o projeto e `--cards`.

## 1. Preparar
- `git pull` na raiz do vault.
- Projeto: o que o dono disse; senão deduzir pelo título/participantes e conferir com os hubs em `projetos/`. Se nenhum servir: perguntar se é projeto novo (então `/novo-projeto`).
- Já existe nota com o mesmo `fonte:`? `grep -rl "<código do link>" projetos/` — se sim, atualizar, não duplicar.

## 2. Achar a reunião

**Fellow** (`fellow.link/XXXX` não abre por fetch nem navegador; resolver via MCP):
1. `search_meetings` com `from_date`/`to_date` em volta da data provável (padrão: últimos 30 dias até hoje), `title` e/ou `note_summary` com o tema. Uma busca por vez; ampliar janela se não achar.
2. O resultado é grande e vai para `tool-results/`. NÃO ler o arquivo inteiro nem escrever parser novo. Usar:
   ```bash
   python -I -X utf8 scripts/fellow_extrair.py "<arquivo tool-results>"                 # lista data | título | link | note_id
   python -I -X utf8 scripts/fellow_extrair.py "<arquivo>" --link XXXX --quotes 40     # nota completa + falas
   ```
   O script casa pelo `meeting_link`; sai com erro listando códigos não achados.
3. Nota rasa (só "AI-Detected Action Items")? Complementar com `get_meeting_summary` (`note_id`) e, se preciso, `get_meeting_transcript`.

**Roam** (`ro.am/share/...`): MCP do Roam (`meeting_info`, `meeting_transcript`) se disponível; senão abrir o link com o navegador embutido (`get_page_text`); falhando, pedir ao dono para colar o resumo.

**Teams/Outlook**: MCP Microsoft 365 se disponível (agenda + chat); transcrição só se o dono colar ou exportar.

**Sem gravação**: registrar stub com o que o dono contou e marcar `> [!question]` para completar depois.

## 3. Escrever a nota
`projetos/<slug>/reunioes/YYYY-MM-DD-<titulo-kebab>.md` a partir de `templates/reuniao.md`:
- Pessoas: conferir nomes em `ref/pessoas.md`; pessoa nova relevante vai para lá.
- Separar fato de inferência; incerto ganha `(?)`.
- Não copiar backlog/estimativa de card: só a chave.

## 4. Propagar (na mesma hora)
- Hub `projetos/<slug>/<slug>.md`: action items do dono/time viram `- [ ] ... 📅/⏳` em Próximos passos (`#aguardando/<pessoa>` quando depende de outro, `#eu` quando é ação humana do dono); decisões relevantes viram `> [!decision] YYYY-MM-DD: ... (fonte: [[nota]])`; linha no Log; link no Mapa; `atualizado:`.
- Prazo novo de frente: `marcos:` no frontmatter do hub (formato em `docs/dashboard.md`).
- `diario/YYYY-MM-DD.md` (criar de `templates/diario.md` se faltar): linha em Feito.

## 5. `--cards` (sugerir issues)
- Listar candidatos: título, tipo, descrição curta, critério de aceite, prioridade sugerida, origem (ponto da reunião).
- Conferir duplicata: `acli jira workitem search --jql "project = <KEY> AND text ~ \"<termo>\"" --fields "key,summary,status" --limit 20`.
- Mostrar ao dono. Criar no Jira **só após "ok" explícito**; depois anotar as chaves no hub/nota.
- Pedido de análise de viabilidade no código: subagente lendo o repo na pasta de repositórios da Configuração.

## 6. Fechar
Rodar `/fechar`.
