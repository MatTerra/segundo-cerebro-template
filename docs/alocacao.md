# Alocação da equipe

Página no claude.ai com quem está em qual frente e até quando. Gerada por `scripts/alocacao.py` a partir do vault; nada é digitado na página. Skill: `/alocacao`.

Seções:
- **Capacidade**: ausentes, devs em mais de uma frente, devs sem frente hoje, quem fica livre e quando, prazos vencidos.
- **Uma coluna por gestor**: frentes em andamento ou pausadas, devs, nota e prazo (vencido, até 7 dias, depois, sem prazo).
- **Em especificação** (para alocar) e **Backlog** (contexto).
- **Sair com dono e prazo**: frentes em andamento sem dev ou sem prazo.
- **Gantt**: todas as pessoas de `equipe.md` em ordem alfabética, inclusive sem frente; 3 meses inteiros a partir do mês atual; ausências hachuradas, interrompendo as barras das frentes do dev (férias coletivas = uma linha por pessoa em `equipe.md`); feriados tracejados; frente sem prazo esmaece.

## Dados

### `alocacao:` no frontmatter do hub
Um item por (frente, dev):

```yaml
alocacao:
  - "Integração X | andamento | Ana | Bruno | 2027-03-01 | 2027-03-20 | API pronta em HML"
  - "Integração X | andamento | Ana | Carla | 2027-03-10 | 2027-03-20 |"
  - "Relatório Y | especificacao | Ana | | | | falta dev"
  - "Módulo Z | backlog | | | | | aguarda cliente"
```
Formato: `"frente | estado | gestor | dev | início | fim | nota"`.
- `estado`: `andamento`, `pausado`, `especificacao` ou `backlog`.
- `gestor`: quem cobra a frente; vários = `"Ana, Davi"` (aparece nas duas colunas).
- `dev` vazio ou `-`: sem dono. `início` vazio: já em andamento. `fim` vazio: sem prazo. `fim` é inclusivo.
- Dev em paralelo ou em sequência: uma linha por período (`Bruno` em X até 03-20 e em Y de 03-23 a 04-10 = duas linhas, em hubs diferentes se as frentes forem de projetos diferentes).
- Frente de um cliente com vários projetos irmãos pode ficar toda no hub principal do cliente; use `--projetos` para filtrar.

### `equipe.md` (raiz do vault; modelo em `templates/equipe.md`)
```markdown
## Pessoas
- Ana
- Bruno
## Ausências
- Bruno | 2027-03-01 | 2027-03-12 | férias
## Feriados
- 2027-04-21 | Tiradentes
```
`Pessoas` define quem aparece no Gantt e na capacidade (sem frente também); dev de `alocacao:` fora da lista (ex.: o gestor que executa uma frente) só aparece na coluna. Sem o arquivo, entram os devs citados em `alocacao:`.

## Gerar
```bash
python -I -X utf8 scripts/alocacao.py <tmp>/alocacao.html --titulo "Alocação" [--projetos a,b] [--gestores Ana,Davi] [--meses 3 | --ate YYYY-MM-DD] [--desde YYYY-MM-DD|mes] [--hoje YYYY-MM-DD]
python -I -X utf8 scripts/alocacao.py --texto
```
Gantt: padrão `--meses 3` = meses inteiros, do dia 1 do mês atual ao fim do 2º mês seguinte (linha vermelha marca hoje). `--desde` (data ou `mes`) e `--ate` sobrescrevem início e fim.
`--texto` imprime o mesmo resumo em Markdown (para responder no chat sem abrir a página).

## Publicar
Primeira vez: `Artifact` publish do HTML (ícone `calendar`); gravar a URL em CLAUDE.md > Configuração > "Página de alocação". Depois: publish com a mesma `url`. A skill `/alocacao` faz os dois. `/fechar` regenera e republica quando `alocacao:` ou `equipe.md` mudou.
