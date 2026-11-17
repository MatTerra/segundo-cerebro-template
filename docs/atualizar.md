# Receber novidades do template

Cada pessoa usa uma **cópia** do template como vault próprio (repo privado). O template continua evoluindo: skills novas, correções de scripts, docs. `/update-segundo-cerebro` traz essas novidades para a cópia sem apagar o que é seu.

## Como funciona
- `.segundo-cerebro/template.json` guarda a URL do template, o branch e a **base**: o commit do template aplicado por último.
- O script `scripts/atualizar_template.py` busca o template no remoto `template` e, para cada arquivo que mudou no template desde a base, faz merge de 3 vias (`git merge-file`):
  - base = arquivo como estava no template na última atualização;
  - template = arquivo atual do template;
  - este vault = seu arquivo (HEAD).
- Mudou só no template: entra limpo. Mudou só aqui: fica como está. Mudou o mesmo trecho dos dois lados: conflito com marcadores `<<<<<<< este vault` / `>>>>>>> template`, que o Claude resolve com você.
- Funciona mesmo sem histórico git em comum com o template (cópia por download, `rm -rf .git`, "Use this template" do GitHub).
- Nada é commitado sozinho: a skill revisa, resolve conflitos e só então commita (`template: atualizado até <sha>`).

## O que nunca é tocado
`projetos/`, `diario/`, `arquivo/`, `ref/`, `agora.md`, `inbox.md`, `README.md` e `.segundo-cerebro/`. Mais o que você listar com `--ignorar <caminho>`.

## O que é atualizado (com merge)
`CLAUDE.md`, `.claude/skills/`, `scripts/`, `docs/`, `global/`, `templates/`, `.gitignore` e qualquer arquivo novo que o template ganhar fora da lista acima.

## Personalizar sem brigar com as atualizações
- Dados seus (nome, orgs, projetos Jira, URL do dashboard, pasta de repos) ficam na **Configuração** do `CLAUDE.md` e em `ref/` (`como-trabalhar.md`, `buckets-worklog.md`, `pessoas.md`, `repos-e-sistemas.md`). As skills leem de lá; não precisa editar a skill.
- Editar uma skill é permitido; só aumenta a chance de conflito nas linhas editadas. Reescreveu de vez e não quer mais receber: `--ignorar .claude/skills/<nome>`.
- Skill só sua: criar com nome que o template não usa (ex.: `.claude/skills/minha-<coisa>/`). O template nunca vai mexer nela.

## Comandos
```bash
python -I -X utf8 scripts/atualizar_template.py --status
python -I -X utf8 scripts/atualizar_template.py --aplicar
python -I -X utf8 scripts/atualizar_template.py --iniciar <url> [--base <sha>]
python -I -X utf8 scripts/atualizar_template.py --ignorar <caminho>
```
Vínculo criado pelo `/init-segundo-cerebro` (passo 4). Vault antigo, sem vínculo: a skill pergunta a URL e a base.

## Contribuir de volta
Melhoria que serve para todos (skill, script, correção): fazer no repositório do template, não só na cópia. Depois rodar `/update-segundo-cerebro` na sua cópia para recebê-la; o merge reconhece a mudança e não duplica.
