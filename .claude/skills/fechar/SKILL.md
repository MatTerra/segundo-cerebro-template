---
name: fechar
description: Fecha uma interação no segundo cérebro - confere Log/diário, commita e dá push, e atualiza o dashboard Agenda se tarefas ou marcos mudaram. Use ao final de qualquer sessão que alterou o vault, ou quando o dono disser "fecha", "salva", "commita".
---

# /fechar

1. `git status --short` na raiz do vault. Nada mudou: dizer isso e parar.
2. Conferir, para cada projeto tocado (`git diff --name-only`):
   - hub com linha datada no Log e `atualizado:` = hoje;
   - tarefas concluídas com `✅ YYYY-MM-DD`;
   - `diario/<hoje>.md` com linha em Feito (criar de `templates/diario.md` se faltar);
   - `agora.md` ainda < 80 linhas e coerente (foco/prazos mudaram? atualizar);
   - nada de segredo, token, senha, dado pessoal de cliente.
3. Sem remoto configurado: só commit. Com remoto: `git pull --rebase -q`, depois `git add -A && git commit -m "<Projeto>: <resumo curto>" && git push`.
   Conflito no rebase: resolver mantendo as duas edições; se for ambíguo, parar e perguntar.
4. A mudança tocou linha de tarefa (`- [ ]`, `- [x]`, `📅`, `⏳`, `✅`) ou `marcos:` em algum hub?
   `git diff HEAD~1 -U0 | grep -E '^[+-].*(- \[.\]|📅|⏳|✅|marcos:|^\+  - ")'`
   Se sim e há dashboard configurado: seguir `scripts/atualizar-agenda.md` (sem commit, é só o dashboard).
5. Resumo em 1–2 linhas: commit, push, dashboard atualizado ou não.
