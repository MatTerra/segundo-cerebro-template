"""Pendências do vault para um dia: atrasadas, vencendo, agendadas, ações do dono (#eu), aguardando, marcos próximos.

Uso: python -I -X utf8 scripts/hoje.py [YYYY-MM-DD] [--dias 7]
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agenda_json import coletar_marcos, coletar_tarefas  # noqa: E402


def linha(t):
    datas = " ".join(f"{e}{t[k]}" for k, e in (("prazo", "📅"), ("agendado", "⏳")) if t[k])
    quem = f" [{t['quem']}]" if t["quem"] else ""
    return f"- {t['texto']} {datas}{quem}  ({t['arquivo']})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dia", nargs="?", default=date.today().isoformat())
    ap.add_argument("--dias", type=int, default=7, help="janela à frente para prazos e marcos")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    hoje = a.dia
    limite = (date.fromisoformat(hoje) + timedelta(days=a.dias)).isoformat()

    abertas = [t for t in coletar_tarefas() if not t["feito"]]
    grupos = {
        "Atrasadas": [t for t in abertas if t["prazo"] and t["prazo"] < hoje],
        "Vencem hoje": [t for t in abertas if t["prazo"] == hoje],
        "Agendadas até hoje": [t for t in abertas if t["agendado"] and t["agendado"] <= hoje and t["prazo"] != hoje],
        f"Prazo nos próximos {a.dias} dias": [t for t in abertas if hoje < t["prazo"] <= limite],
        "Ação do dono (#eu, sem data)": [t for t in abertas if t["quem"] == "Eu" and not t["prazo"] and not t["agendado"]],
        "Aguardando outros": [t for t in abertas if t["quem"].startswith("aguardando")],
        "Bloqueadas": [t for t in abertas if t["quem"] == "bloqueado"],
    }
    for titulo, ts in grupos.items():
        if ts:
            print(f"## {titulo} ({len(ts)})")
            for t in sorted(ts, key=lambda t: (t["prazo"] or t["agendado"] or "9", t["projeto"])):
                print(linha(t))
            print()

    marcos = [m for m in coletar_marcos() if m["data"] <= limite and (m["data"] >= hoje or m["tipo"] == "prazo")]
    vencidos = [m for m in marcos if m["data"] < hoje]
    proximos = [m for m in marcos if m["data"] >= hoje]
    if proximos:
        print(f"## Marcos até {limite}")
        for m in sorted(proximos, key=lambda m: m["data"]):
            print(f"- {m['data']} {m['tipo']}: {m['frente']} ({m['projeto']}) — {m['nota']}")
        print()
    if vencidos:
        print("## Prazos de marcos já vencidos (conferir se ainda valem)")
        for m in sorted(vencidos, key=lambda m: m["data"]):
            print(f"- {m['data']}: {m['frente']} ({m['projeto']}) — {m['nota']}")


if __name__ == "__main__":
    main()
