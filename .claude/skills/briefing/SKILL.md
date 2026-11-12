---
name: briefing
description: Pesquisa um tema (norma, regulação, tecnologia, mercado) em fontes primárias e salva um briefing durável em ref/, separando o que está escrito em norma/doc do que é inferência. Use para "pesquise X", "prepare um briefing sobre X", "de onde vem isso?", "pesquisa profunda".
argument-hint: "<tema> [projeto]"
---

# /briefing

## 1. Escopo
- Pergunta central em uma frase; projeto ligado (`[[<slug>]]`) se houver.
- Já existe nota? `grep -ril "<termo>" ref projetos` — se sim, atualizar em vez de criar.

## 2. Pesquisar
- Várias buscas no mesmo turno (`WebSearch`; modo `extended` para norma recente ou nicho).
- **Fonte primária primeiro**: texto da norma/lei (diário oficial, portal de legislação, órgão regulador), RFC, documentação oficial do fornecedor. Blog/escritório só como pista para achar a primária.
- Ler no texto original: navegador embutido (`get_page_text`) ou `curl -sL -A "Mozilla/5.0"` para uma pasta nova no scratchpad (PDF: skill `pdf`). Anotar artigo/inciso/seção exata.
- Tema regulatório: conferir vigência (revogado? alterado por norma posterior?).
- Tema longo ou de muitas frentes: subagente(s) em paralelo, cada um com uma pergunta fechada, devolvendo citação + URL.

## 3. Escrever `ref/<slug-do-tema>.md`
```markdown
---
tipo: ref
atualizado: YYYY-MM-DD
tags: [ref/<area>]
projetos: ["[[<slug>]]"]
---
# <Tema>

> [!summary] Resposta curta
> 2–4 linhas respondendo a pergunta central.

## O que está escrito (fonte primária)
- <afirmação> — <norma/doc, art./seção> ([link](url))

## Inferência / interpretação
- <afirmação> — por quê; o que confirmaria

## Em aberto
> [!question] ...

## Fontes
- <título>, <órgão>, <data> — url
```
- Toda afirmação de "obrigatório/permitido/proibido" precisa de citação; sem citação vai para Inferência.
- Corrigir notas antigas que afirmavam algo sem fonte (mover para Inferência, com data).

## 4. Propagar
- Link no hub do projeto (Mapa ou Contexto) e linha no Log; tarefa de retorno a alguém (`#eu`) se o briefing responde pedido de terceiro.
- Responder ao dono com o resumo curto + o link da nota. `/fechar`.
