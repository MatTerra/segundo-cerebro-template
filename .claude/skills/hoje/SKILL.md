---
name: hoje
description: Lista as pendências do dono para o dia - tarefas atrasadas, vencendo, agendadas, ações #eu, aguardando outros, marcos próximos, mais action items de reunião e cards do tracker. Use para "que pendências tenho hoje?", "o que tenho pra hoje/amanhã/essa semana", "bom dia".
argument-hint: "[YYYY-MM-DD] [--dias N]"
---

# /hoje

1. `git pull -q` na raiz do vault (se houver remoto).
2. Vault (fonte principal):
   ```bash
   python -I -X utf8 scripts/hoje.py <YYYY-MM-DD> --dias 7
   ```
   Data relativa do pedido ("amanhã", "sexta") → converter para data absoluta.
3. Em paralelo, fontes externas da Configuração do `CLAUDE.md` (pular a que falhar ou não estiver configurada, dizendo qual):
   - Reuniões: Fellow `get_action_items` do dono em aberto; Roam/Teams se configurado. Item que não está no vault → mostrar como "novo" e oferecer registrar no hub certo.
   - Jira: `acli jira workitem search --jql "assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC" --fields "key,summary,status,priority" --limit 30`.
   - Agenda (Outlook/Roam/Google), se disponível: reuniões do dia.
4. Responder curto, nesta ordem:
   1. **Hoje**: atrasadas + vencem hoje + agendadas + reuniões do dia.
   2. **Esta semana**: prazos e marcos dos próximos dias.
   3. **Cobrar**: aguardando outros com prazo vencido ou parado há mais de 5 dias.
   4. **Sem data (#eu)**: só as 5 mais relevantes pelo foco do `agora.md`; dizer quantas sobram.
   5. Marcos vencidos que ainda constam: perguntar se valem.
   Sem copiar a saída inteira do script.
5. O dono marcou algo como feito ou passou info nova: registrar na hora (`✅ YYYY-MM-DD`, Log, diário) e rodar `/fechar`.
6. Muitas pendências sem data vindas de `confianca: inferido`: sugerir uma rodada de confirmação.
