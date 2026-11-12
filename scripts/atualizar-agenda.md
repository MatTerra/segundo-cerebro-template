# Atualizar o dashboard Agenda

Dashboard: {{URL_DASHBOARD}} (tipo Dashboard, datasets `tarefas` e `marcos`, ambos arquivos JSON anexados). Como foi criado e o formato dos dados: `docs/dashboard.md`.
Roda pela tarefa agendada (prompt em `scripts/tarefa-agendada-agenda.md`) e deve ser rodado também ao fim de qualquer sessão que mude tarefas ou `marcos:` no vault (`/fechar` passo 4).

1. Na raiz do vault: `git pull` (se houver remoto).
2. Gerar os dados numa pasta temporária (scratchpad), fora do vault:
   `python -I -X utf8 scripts/agenda_json.py <tmp>/agenda.json <tmp>/marcos.json`
3. Ler os datasets atuais com `ArtifactData` `get`, `url` do dashboard, `collection: "datasets"`, `doc_id` `tarefas` e `marcos`. Guardar `version` e o `source.url` antigo de cada um.
4. Para cada arquivo, enviar como asset: `Artifact` publish com `url` do dashboard, `asset: true`, `file_path` do JSON. A resposta dá a nova url `/_blob/<id>`.
5. `ArtifactData` `batch` com dois `update` (um por dataset), cada um com `if_version` lido no passo 3 e `data`:
   `{"source": {"kind": "file", "url": "<nova url>", "name": "agenda.json" | "marcos.json"}, "updated": {"at": "<agora UTC ISO>", "by": "Claude (scripts/agenda_json.py)"}, "edit": {"via": "claude", "at": "<agora UTC ISO>"}}`
   Conflito de versão: ler de novo e refazer.
6. Só depois do passo 5 dar certo: apagar os assets antigos com `Artifact` `action: "delete"`, `url` do dashboard, `path` = id antigo (32 caracteres depois de `/_blob/`). Nunca apagar um id que algum dataset ainda use.
7. Não mexer em `index.html` nem em outros documentos do painel. Não fazer commit (o passo não muda o vault).
