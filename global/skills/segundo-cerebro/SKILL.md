---
name: segundo-cerebro
description: Consulta e alimenta o segundo cérebro (vault em {{CAMINHO_VAULT}}) a partir de QUALQUER conversa, mesmo fora do vault. Use quando a conversa envolver um projeto, cliente, card Jira, reunião, prazo, decisão ou pessoa do trabalho do dono; quando ele perguntar "o que sabemos sobre X", "qual o estado de X", "o que falta em X"; quando disser "anota/registra no segundo cérebro"; ou quando surgir decisão, prazo ou pendência que valha guardar.
argument-hint: "[consultar <tema> | registrar <info>]"
---

# /segundo-cerebro (global)

Vault: `{{CAMINHO_VAULT}}`. Protocolo completo: `{{CAMINHO_VAULT}}/CLAUDE.md` (ler antes de escrever).

## Consultar (só leitura, sem pedir licença)
1. Projeto do repo atual: o hook de início de sessão já pode ter injetado o resumo ("Segundo cérebro: ..."). Se não:
   `grep -rl -i "<nome da pasta do repo>" "{{CAMINHO_VAULT}}/projetos" --include="*.md" | head`
   (hubs listam repos em `repos:` no frontmatter).
2. Por tema/card/pessoa: `grep -rn -i "<termo>" "{{CAMINHO_VAULT}}"/{projetos,ref,agora.md} --include="*.md" | head -30`.
3. Ler o hub `projetos/<slug>/<slug>.md` (Estado, Próximos passos, Decisões, Log). Subnotas e `reunioes/` só se precisar de detalhe.
4. Foco e pendências gerais: `agora.md`. Pessoas: `ref/pessoas.md`. Repos: `ref/repos-e-sistemas.md`.
5. Usar o que achar como contexto; citar a nota (`projetos/x/x.md`) quando a resposta depender dela. Nota com `confianca: inferido` = tratar como hipótese.

## Registrar (quando surgir informação durável)
Vale registrar: decisão tomada, prazo combinado, pendência do dono ou de terceiros, fato técnico estável descoberto, mudança de estado de uma frente.
Não vale: detalhe de implementação que já está no código/commit, backlog de card (fica no Jira), segredo, token, dado pessoal de cliente.

1. `git -C "{{CAMINHO_VAULT}}" pull -q` (se houver remoto).
2. Escrever no lugar certo seguindo o `CLAUDE.md` do vault: tarefa (`- [ ] ... 📅/⏳ #eu|#aguardando/<pessoa>`) e decisão (`> [!decision] YYYY-MM-DD: ...`) no hub; linha no Log do hub e `atualizado:`; linha em Feito no `diario/<hoje>.md` (criar de `templates/diario.md` se faltar). Sem hub para o assunto: `inbox.md`.
3. Commit só dos arquivos do vault: `git -C "{{CAMINHO_VAULT}}" add -A && git -C "{{CAMINHO_VAULT}}" commit -m "<projeto>: <resumo>" && git -C "{{CAMINHO_VAULT}}" push`.
4. Tocou tarefa ou `marcos:`: avisar que o dashboard atualiza na próxima execução agendada (ou rodar `scripts/atualizar-agenda.md` se o dono pedir).
5. Dizer em uma linha o que foi registrado e onde.

## Regras
- Datas absolutas sempre.
- Não registrar sem necessidade nem em toda conversa: só o que o dono vai querer lembrar daqui a semanas.
- Fora do vault, o trabalho principal é o do repo atual; registrar é complemento rápido, não desvio.
- Escrita externa (Jira, mensagens) segue exigindo "ok" explícito.
