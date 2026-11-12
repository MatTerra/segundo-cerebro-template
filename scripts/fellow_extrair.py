"""Extrai reuniões do resultado bruto do Fellow `search_meetings` (salvo em tool-results/).

O MCP do Fellow devolve {"result": "<meeting_search ...>[json]</meeting_search>"}, centenas de KB.
Os links curtos `fellow.link/XXXX` não abrem direto, mas cada reunião traz `meeting_link`; casar por ele.

Uso:
  python -I -X utf8 scripts/fellow_extrair.py <arquivo>                  # lista: data | título | link | note_id
  python -I -X utf8 scripts/fellow_extrair.py <arquivo> --link XXXXXXXXXXXX [--link ...]
  python -I -X utf8 scripts/fellow_extrair.py <arquivo> --note 12345678
  python -I -X utf8 scripts/fellow_extrair.py <arquivo> --link X --quotes 40   # inclui até N falas
"""
import argparse
import json
import sys


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        bruto = f.read()
    try:
        d = json.loads(bruto)
        texto = d.get("result", bruto) if isinstance(d, dict) else bruto
        if isinstance(texto, list):
            texto = "".join(x.get("text", "") for x in texto if isinstance(x, dict))
    except json.JSONDecodeError:
        texto = bruto
    ini = texto.find(">", texto.find("<meeting_search")) + 1 if "<meeting_search" in texto else 0
    fim = texto.rfind("</meeting_search>")
    fim = fim if fim != -1 else len(texto)
    return json.loads(texto[ini:fim].strip() or "[]")


def codigo(link):
    return (link or "").rstrip("/").rsplit("/", 1)[-1].upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--link", action="append", default=[], help="código ou URL fellow.link")
    ap.add_argument("--note", action="append", default=[], help="note_id")
    ap.add_argument("--quotes", type=int, default=0, help="máx. falas da transcrição por reunião")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    reunioes = carregar(a.arquivo)
    links = {codigo(x) for x in a.link}
    notes = {str(x) for x in a.note}

    if not links and not notes:
        for m in sorted(reunioes, key=lambda m: m.get("start_time", "")):
            print(f"{m.get('start_time','')[:10]} | {m.get('title','')} | {m.get('meeting_link','')} | note_id={m.get('note_id','')}")
        print(f"\n{len(reunioes)} reuniões")
        return

    achou = set()
    for m in reunioes:
        c = codigo(m.get("meeting_link"))
        if c not in links and str(m.get("note_id")) not in notes:
            continue
        achou.add(c)
        print("=" * 70)
        print(f"# {m.get('title','')}")
        print(f"data: {m.get('start_time','')} -> {m.get('end_time','')}")
        print(f"fonte: {m.get('meeting_link','')}  ({m.get('url','')})")
        print(f"note_id: {m.get('note_id','')}  meeting_id: {m.get('meeting_id','')}")
        print("\n## Nota\n" + (m.get("note") or "(vazia)"))
        q = m.get("quotes") or []
        if a.quotes and q:
            print(f"\n## Falas ({min(len(q), a.quotes)} de {len(q)})")
            for x in q[: a.quotes]:
                print(f"- {x.get('speaker','?')}: {x.get('text') or x.get('quote') or ''}")
    faltam = links - achou
    if faltam:
        print(f"\nNÃO ACHADOS neste resultado: {', '.join(sorted(faltam))} (ampliar datas/termos do search_meetings)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
