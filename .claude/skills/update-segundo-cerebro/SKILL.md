---
name: update-segundo-cerebro
description: Traz para este vault (cópia pessoal) as novidades do template do segundo cérebro - skills, scripts, docs, integração global, modelos - com merge de 3 vias que preserva a personalização local. Use para "/update-segundo-cerebro", "atualiza o segundo cérebro", "tem novidade no template?", "puxa as melhorias do template".
argument-hint: "[--status]"
---

# /update-segundo-cerebro

Script: `scripts/atualizar_template.py` (docstring com detalhes). Conteúdo pessoal (`projetos/`, `diario/`, `arquivo/`, `ref/`, `agora.md`, `inbox.md`, `README.md`) nunca é tocado.

## 1. Vínculo
- Sem `.segundo-cerebro/template.json`: vault ainda não ligado ao template.
  - Perguntar a URL do template (padrão: a que o dono usou para copiar; ver `git remote -v` e o README do template).
  - Perguntar se o vault está em dia com o template. Sim: `--iniciar <url>`. Não: achar o commit do template de onde ele saiu (`git log template/main` pela data da cópia) e usar `--iniciar <url> --base <sha>`. Na dúvida, usar o primeiro commit do template e esperar mais conflitos.
  - Commitar `.segundo-cerebro/template.json`.

## 2. Ver o que mudou
`python -I -X utf8 scripts/atualizar_template.py --status`
Resumir ao dono: commits novos do template (o que cada um traz) e arquivos `[editado aqui]`, que podem dar conflito. Em dia: dizer e parar. Com `--status` no pedido: parar aqui.

## 3. Aplicar (só com ok do dono)
1. Árvore limpa (senão `/fechar` antes).
2. `python -I -X utf8 scripts/atualizar_template.py --aplicar`.
3. **Conflitos** (`<<<<<<< este vault` / `=======` / `>>>>>>> template`): resolver arquivo a arquivo. Regra: manter a personalização do dono (nomes, tags, escopo, caminhos, URLs, regras próprias) e adotar o comportamento novo do template. Na dúvida, mostrar os dois lados e perguntar. Depois `git add <arquivo>`.
4. **Falhas** (removido no template mas editado aqui, binário): mostrar e perguntar.
5. Avisos do script:
   - `global/` mudou: `python -I -X utf8 scripts/instalar_global.py` (com ok; mostra `--dry-run` antes).
   - `CLAUDE.md` com `{{...}}`: campo novo na Configuração; perguntar o valor e preencher.
   - Skills novas ou mudadas: valem em sessão nova.
6. Conferir: `grep -rn "<<<<<<<\|>>>>>>>" . --include=*.md --include=*.py` vazio; `python -m py_compile scripts/*.py`.
7. Commit `template: atualizado até <sha curto>` + push. Linha no diário do dia (Feito) com o que entrou.

## Ajustes
- Arquivo que o dono reescreveu de vez e não quer mais receber do template: `--ignorar <caminho>`, depois commitar o json.
- Desfazer uma atualização ainda não commitada: `git reset --hard HEAD` (pedir ok: descarta o merge inteiro).
