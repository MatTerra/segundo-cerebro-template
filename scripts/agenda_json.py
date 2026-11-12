"""Gera os dados do dashboard Agenda (URL na Configuração do CLAUDE.md; ver docs/dashboard.md).

- tarefas: linhas formato plugin Tasks em projetos/** e inbox.md
- marcos: lista `marcos:` no frontmatter dos hubs, cada item "YYYY-MM-DD | tipo | frente | nota"
  (tipo: prazo | previsao | evento | lancamento)

Uso: python -I scripts/agenda_json.py <agenda.json> <marcos.json>
"""
import hashlib
import json
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
TASK = re.compile(r"^\s*- \[( |x|X)\] (.*)$")
DATE = {"prazo": "📅", "agendado": "⏳", "concluido": "✅"}


def parse(line, projeto, arquivo, n):
    m = TASK.match(line)
    if not m:
        return None
    feito, texto = m.group(1).lower() == "x", m.group(2)
    row = {"id": hashlib.sha1(f"{arquivo}:{texto}".encode()).hexdigest()[:10], "projeto": projeto, "arquivo": arquivo}
    for campo, emoji in DATE.items():
        d = re.search(emoji + r"\s*(\d{4}-\d{2}-\d{2})", texto)
        row[campo] = d.group(1) if d else ""
        texto = re.sub(emoji + r"\s*\d{4}-\d{2}-\d{2}", "", texto)
    tags = re.findall(r"#([\w/\-]+)", texto)
    texto = re.sub(r"\s#[\w/\-]+", "", texto)
    texto = re.sub(r"\[\[([^\]|]+)(\|[^\]]+)?\]\]", r"\1", texto).strip()
    aguardando = next((t.split("/", 1)[1] for t in tags if t.startswith("aguardando/")), "")
    if "bloqueado" in tags:
        quem = "bloqueado"
    elif aguardando:
        quem = "aguardando " + aguardando
    elif "eu" in tags:
        quem = "Eu"
    else:
        quem = ""
    row.update(texto=texto, feito=feito, quem=quem)
    return row


def coletar_tarefas():
    rows = []
    fontes = [(md, md.relative_to(VAULT / "projetos").parts[0]) for md in sorted((VAULT / "projetos").rglob("*.md"))]
    if (VAULT / "inbox.md").exists():
        fontes.append((VAULT / "inbox.md", "inbox"))
    for md, projeto in fontes:
        arquivo = md.relative_to(VAULT).as_posix()
        for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            r = parse(line, projeto, arquivo, n)
            if r:
                rows.append(r)
    return rows


def coletar_marcos():
    marcos = []
    for md in sorted((VAULT / "projetos").glob("*/*.md")):
        if md.stem == md.parent.name:
            marcos += parse_marcos(md.read_text(encoding="utf-8"), md.parent.name)
    return marcos


def main():
    rows, marcos = coletar_tarefas(), coletar_marcos()
    Path(sys.argv[1]).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    Path(sys.argv[2]).write_text(json.dumps(marcos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(rows), "tarefas,", len(marcos), "marcos")


def parse_marcos(texto, projeto):
    if not texto.startswith("---"):
        return []
    fm = texto.split("---", 2)[1].splitlines()
    out, dentro = [], False
    for line in fm:
        if re.match(r"^marcos:\s*$", line):
            dentro = True
            continue
        if dentro and not line.startswith(" "):
            break
        m = re.match(r'^\s+-\s+"?(\d{4}-\d{2}-\d{2})\s*\|\s*(\w+)\s*\|\s*([^|]+?)\s*\|\s*(.*?)"?\s*$', line) if dentro else None
        if m:
            data, tipo, frente, nota = m.groups()
            mid = hashlib.sha1(f"{projeto}:{data}:{tipo}:{frente}".encode()).hexdigest()[:10]
            out.append({"id": mid, "projeto": projeto, "frente": frente, "data": data, "tipo": tipo, "nota": nota})
    return out


if __name__ == "__main__":
    main()
