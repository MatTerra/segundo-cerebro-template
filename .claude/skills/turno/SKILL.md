---
name: turno
description: Registra o turno de trabalho do dia (início, pausa, volta, fim, horários previstos) na linha `Turno:` do diário, com total de horas, sem gastar contexto. Use para "/turno", "entrei 8h", "comecei agora", "vou almoçar 12h30", "voltei", "parei às 18h", "quantas horas fiz hoje".
argument-hint: "[ontem|YYYY-MM-DD] <texto livre com horários> | desfaz"
model: haiku
allowed-tools: Bash(python -I -X utf8 scripts/turno.py *)
---

# /turno

Resultado (o script já gravou, commitou e deu push só do diário):

!`python -I -X utf8 scripts/turno.py "$ARGUMENTS"`

Regras, para gastar o mínimo:
- Responder em **uma linha** com o resultado acima. Não ler arquivos nem rodar mais nada.
- Saída começa com `ERRO`: mostrar o erro e pedir o horário em uma frase curta.
- Se acima aparece o comando em vez de um resultado (injeção não rodou): executar uma vez `python -I -X utf8 scripts/turno.py <texto do pedido>` na raiz do vault e responder em uma linha.
- Formato: `Turno: 08:00–12:30 · 13:30–~18:00 · total 9h00 (previsto)`; `~` = previsto, `…` = aberto. O `/worklog` usa essa linha como jornada do dia.
