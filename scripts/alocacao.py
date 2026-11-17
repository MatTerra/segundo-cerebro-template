"""Gera a página de alocação da equipe (frentes por gestor, especificação, backlog, sem dono e Gantt dos devs).

Fontes no vault:
- `alocacao:` no frontmatter dos hubs (`projetos/<slug>/<slug>.md`), um item por (frente, dev):
    "frente | estado | gestor | dev | início | fim | nota"
  estado: andamento | pausado | especificacao | backlog
  dev vazio ou "-" = sem dono; início vazio = já em andamento; fim vazio = sem prazo.
  Frente com dois devs = duas linhas. Gestor com mais de um nome: "Ana, Bia" (aparece nas duas colunas).
- `equipe.md` na raiz (modelo em templates/equipe.md): seções `## Pessoas` (uma pessoa por linha,
  "- Nome"), `## Ausências` ("- Nome | início | fim | motivo") e `## Feriados` ("- YYYY-MM-DD | nome").
  Com equipe.md, o Gantt e a capacidade mostram só as pessoas listadas; sem ele, os devs citados em `alocacao:`.

Uso:
  python -I -X utf8 scripts/alocacao.py <saida.html> [--titulo T] [--projetos a,b] [--gestores A,B] [--meses 6] [--hoje YYYY-MM-DD]
  python -I -X utf8 scripts/alocacao.py --texto [mesmas opções]   (resumo em Markdown no terminal)
"""
import argparse
import html
import re
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
ESTADOS = ("andamento", "pausado", "especificacao", "backlog")
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
SEM = {"", "-", "—", "?"}


# ---------- leitura ----------

def d(s):
    s = (s or "").strip()
    return date.fromisoformat(s) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s) else None


def frontmatter_lista(texto, chave):
    if not texto.startswith("---"):
        return []
    out, dentro = [], False
    for line in texto.split("---", 2)[1].splitlines():
        if re.match(rf"^{chave}:\s*$", line):
            dentro = True
            continue
        if dentro and line.strip() and not line.startswith(" "):
            break
        m = re.match(r'^\s+-\s+"?(.*?)"?\s*$', line) if dentro else None
        if m:
            out.append(m.group(1))
    return out


def ler_alocacao(projetos=None):
    itens = []
    for md in sorted((VAULT / "projetos").glob("*/*.md")):
        if md.stem != md.parent.name or (projetos and md.stem not in projetos):
            continue
        for bruto in frontmatter_lista(md.read_text(encoding="utf-8"), "alocacao"):
            p = [c.strip() for c in bruto.split("|")]
            p += [""] * (7 - len(p))
            frente, estado, gestor, dev, ini, fim, nota = p[:7]
            estado = estado.lower().replace("ç", "c").replace("ã", "a")
            if estado not in ESTADOS:
                print(f"aviso: estado '{estado}' inválido em {md.name}: {bruto}", file=sys.stderr)
                continue
            itens.append({
                "projeto": md.stem, "frente": frente, "estado": estado,
                "gestores": [g.strip() for g in gestor.split(",") if g.strip() not in SEM],
                "dev": "" if dev in SEM else dev, "ini": d(ini), "fim": d(fim), "nota": nota,
            })
    return itens


def ler_equipe():
    arq = VAULT / "equipe.md"
    pessoas, ausencias, feriados = [], [], []
    if not arq.exists():
        return pessoas, ausencias, feriados
    secao = ""
    for line in arq.read_text(encoding="utf-8").splitlines():
        h = re.match(r"^##\s+(.*)", line)
        if h:
            secao = sem_acento(h.group(1)).lower()
            continue
        m = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if not m:
            continue
        p = [c.strip() for c in m.group(1).split("|")]
        if secao.startswith("pessoa"):
            pessoas.append(p[0])
        elif secao.startswith("ausencia") and len(p) >= 3 and d(p[2]):
            ausencias.append({"dev": p[0], "ini": d(p[1]) or d(p[2]), "fim": d(p[2]), "motivo": p[3] if len(p) > 3 else "ausência"})
        elif secao.startswith("feriado") and d(p[0]):
            feriados.append((d(p[0]), p[1] if len(p) > 1 else "feriado"))
    return pessoas, ausencias, feriados


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


# ---------- análise ----------

def ativo(i, hoje):
    return i["estado"] == "andamento" and (i["ini"] or hoje) <= hoje and (i["fim"] is None or i["fim"] >= hoje)


def analisar(itens, pessoas, ausencias, hoje):
    # com equipe.md, só as pessoas listadas (gestor que executa algo não vira linha); sem ele, todos os devs citados
    devs = sorted(set(pessoas) or {i["dev"] for i in itens if i["dev"]}, key=lambda s: sem_acento(s).lower())
    aus_hoje = {a["dev"]: a for a in ausencias if a["ini"] <= hoje <= a["fim"]}
    por_dev = {dev: [i for i in itens if i["dev"] == dev and ativo(i, hoje)] for dev in devs}
    # compromisso futuro: andamento que ainda não começou ou pausado com data de retomada
    futuros = {dev: [i for i in itens if i["dev"] == dev and i["ini"] and i["ini"] > hoje
                     and i["estado"] in ("andamento", "pausado")] for dev in devs}
    return {
        "devs": devs,
        "ausentes": [a for a in ausencias if a["fim"] >= hoje],
        "sobrecarga": {dev: l for dev, l in por_dev.items() if len({x["frente"] for x in l}) > 1},
        "livres": [dev for dev in devs if not por_dev[dev] and dev not in aus_hoje and not futuros[dev]],
        "livres_depois": {dev: max(x["fim"] for x in por_dev[dev] + futuros[dev]) for dev in devs
                          if por_dev[dev] and all(x["fim"] for x in por_dev[dev] + futuros[dev])},
        "sem_dono": frentes_sem(itens, lambda l: all(not x["dev"] for x in l)),
        "sem_prazo": frentes_sem(itens, lambda l: all(x["fim"] is None for x in l)),
        "vencidos": list({i["frente"]: i for i in itens if i["estado"] == "andamento" and i["fim"] and i["fim"] < hoje}.values()),
    }


def agrupar(itens):
    """Itens de mesma (projeto, frente, estado) viram uma frente com vários devs."""
    g = {}
    for i in itens:
        g.setdefault((i["projeto"], i["frente"], i["estado"]), []).append(i)
    return g


def frentes_sem(itens, cond):
    return [k[1] for k, l in agrupar([i for i in itens if i["estado"] == "andamento"]).items() if cond(l)]


# ---------- saída: texto ----------

ANO = date.today().year  # main() ajusta para o ano de --hoje


def fmt(x):
    if not x:
        return "sem prazo"
    return x.strftime("%m-%d") if x.year == ANO else x.isoformat()


def texto(itens, a, hoje):
    out = [f"# Alocação em {hoje.isoformat()}", ""]
    gest = colunas(itens)
    for g, frentes in gest.items():
        out.append(f"## {g}")
        for f in frentes:
            out.append(f"- {f['frente']}: {f['devs'] or 'sem dono'}; {fmt(f['fim'])}" + (f" ({f['nota']})" if f["nota"] else ""))
        out.append("")
    for titulo, est in (("Em especificação", "especificacao"), ("Backlog", "backlog"), ("Pausado", "pausado")):
        l = [k[1] for k in agrupar(itens) if k[2] == est]
        if l:
            out += [f"## {titulo}", "- " + " · ".join(l), ""]
    out.append("## Sem dono: " + (", ".join(a["sem_dono"]) or "nenhuma"))
    out.append("## Sem prazo: " + (", ".join(a["sem_prazo"]) or "nenhuma"))
    out.append("## Vencidos: " + (", ".join(f"{i['frente']} ({fmt(i['fim'])})" for i in a["vencidos"]) or "nenhum"))
    out.append("## Devs sem frente hoje: " + (", ".join(a["livres"]) or "nenhum"))
    if a["livres_depois"]:
        out.append("## Ficam livres: " + ", ".join(f"{dev} depois de {fmt(x)}" for dev, x in sorted(a["livres_depois"].items(), key=lambda t: t[1])))
    out.append("## Ausentes: " + (", ".join(f"{x['dev']} até {fmt(x['fim'])} ({x['motivo']})" for x in a["ausentes"]) or "ninguém"))
    out.append("## Em mais de uma frente: " + (", ".join(f"{dev} ({len({x['frente'] for x in l})})" for dev, l in a["sobrecarga"].items()) or "ninguém"))
    return "\n".join(out)


def colunas(itens, ordem=None):
    ativos = [i for i in itens if i["estado"] in ("andamento", "pausado")]
    gest = {}
    for (proj, frente, est), l in agrupar(ativos).items():
        fins = [x["fim"] for x in l if x["fim"]]
        f = {"frente": frente, "estado": est, "fim": max(fins) if fins else None,
             "devs": ", ".join(dict.fromkeys(x["dev"] for x in l if x["dev"])),
             "nota": "; ".join(dict.fromkeys(x["nota"] for x in l if x["nota"]))}
        for g in (l[0]["gestores"] or ["Sem gestor"]):
            gest.setdefault(g, []).append(f)
    for l in gest.values():
        l.sort(key=lambda f: (f["fim"] is None, f["fim"] or date.max, f["frente"]))
    nomes = sorted(gest, key=lambda g: (-len(gest[g]), g))
    if ordem:
        nomes = [g for g in ordem if g in gest] + [g for g in nomes if g not in ordem]
    return {g: gest[g] for g in nomes}


# ---------- saída: HTML ----------

CSS = """
:root{--bg:#f6f7f5;--paper:#fff;--fg:#1d2420;--muted:#5d6b63;--line:#d9dfdb;--accent:#1f6b4a;--accent-soft:#e3f0e9;
--warn:#9a5b00;--warn-soft:#fbefd9;--late:#a3302b;--late-soft:#f8e1df;--on:#fff;
--f-display:"IBM Plex Sans Condensed","Arial Narrow",system-ui,sans-serif;--f-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121614;--paper:#1a201d;--fg:#e4ebe7;--muted:#9aaba2;--line:#2d3631;--accent:#5fc493;--accent-soft:#1e3329;--warn:#e8b154;--warn-soft:#3a2d16;--late:#f08a83;--late-soft:#3d1f1d;--on:#0f1a14;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121614;--paper:#1a201d;--fg:#e4ebe7;--muted:#9aaba2;--line:#2d3631;--accent:#5fc493;--accent-soft:#1e3329;--warn:#e8b154;--warn-soft:#3a2d16;--late:#f08a83;--late-soft:#3d1f1d;--on:#0f1a14;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--fg);font:12.5px/1.4 var(--f-body)}
.wrap{max-width:1280px;margin:0 auto;padding:16px max(16px,env(safe-area-inset-right,0px)) 20px max(16px,env(safe-area-inset-left,0px));display:grid;gap:10px}
header{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:4px 16px;border-bottom:2px solid var(--accent);padding-bottom:6px}
h1{font:700 22px/1.1 var(--f-display);margin:0}
.meta{color:var(--muted);font-size:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
h2{font:700 12px/1 var(--f-display);text-transform:uppercase;letter-spacing:.08em;color:var(--accent);margin:0 0 6px;display:flex;gap:8px;align-items:baseline}
h2 small{font:400 11.5px var(--f-body);text-transform:none;letter-spacing:0;color:var(--muted)}
section{background:var(--paper);border:1px solid var(--line);border-radius:4px;padding:8px 10px;min-width:0}
ul{margin:0;padding:0;list-style:none;display:grid;gap:3px}
li{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:baseline;border-bottom:1px dotted var(--line);padding-bottom:3px}
li:last-child{border-bottom:0}
b{font-weight:600}.q{color:var(--muted)}
.d{font:500 11px var(--f-mono);white-space:nowrap;padding:1px 5px;border-radius:3px;background:var(--accent-soft);color:var(--accent)}
.d.soon{background:var(--warn-soft);color:var(--warn)}.d.late{background:var(--late-soft);color:var(--late)}
.d.none{background:transparent;color:var(--muted);border:1px solid var(--line)}
.cap{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:4px 16px}
.cap div{border-left:2px solid var(--warn);padding-left:7px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:10px}
.flat li{grid-template-columns:1fr}
.gantt{display:grid;grid-template-columns:130px 1fr;row-gap:2px;font-size:11.5px}
.who{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;align-self:center}
.lane{position:relative;height:20px;border-bottom:1px dotted var(--line)}
.lane.sub{border-bottom-style:none}
.axis{position:relative;height:16px;color:var(--muted);font:500 10.5px var(--f-mono)}
.axis span{position:absolute;transform:translateX(-50%);white-space:nowrap}
.tick{position:absolute;top:0;bottom:0;border-left:1px solid var(--line)}
.hol{position:absolute;top:-1px;bottom:-1px;border-left:2px dashed var(--muted);z-index:1}
.bar{position:absolute;top:2px;height:16px;border-radius:3px;background:var(--accent);color:var(--on);font-size:10.5px;line-height:16px;padding:0 5px;box-sizing:border-box;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;z-index:2}
.bar.soon{background:var(--warn)}.bar.pause{opacity:.55}.bar.late{background:var(--late)}
.bar.off{background:repeating-linear-gradient(45deg,var(--line) 0 4px,transparent 4px 8px);color:var(--muted);border:1px solid var(--line)}
.bar.open{background:linear-gradient(90deg,var(--accent) 45%,transparent);border-radius:3px 0 0 3px}
.lbl{position:absolute;top:2px;line-height:16px;font-size:10.5px;white-space:nowrap;z-index:2}
.gleg{display:flex;flex-wrap:wrap;gap:4px 14px;color:var(--muted);font-size:11px;margin-top:6px}
.gleg i{display:inline-block;width:14px;height:9px;border-radius:2px;vertical-align:middle;margin-right:4px}
"""

E = html.escape


def pill(fim, hoje, vazio="—"):
    if fim is None:
        return f'<span class="d none">{E(vazio)}</span>'
    cls = "late" if fim < hoje else "soon" if fim <= hoje + timedelta(days=7) else ""
    txt = fim.strftime("%m-%d") if fim.year == hoje.year else fim.isoformat()
    return f'<span class="d {cls}">{txt}</span>'


def gantt(itens, a, ausencias, feriados, hoje, meses):
    d0 = hoje
    m, y = hoje.month + meses, hoje.year
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    d1 = date(y, m, min(hoje.day, 28))
    span = (d1 - d0).days or 1

    def p(x):
        return max(0.0, min(100.0, (x - d0).days / span * 100))

    ticks, t = [], date(d0.year + (d0.month == 12), d0.month % 12 + 1, 1)
    while t < d1:
        ticks.append(t)
        t = date(t.year + (t.month == 12), t.month % 12 + 1, 1)
    deco = "".join(f'<div class="tick" style="left:{p(t):.2f}%"></div>' for t in ticks)
    deco += "".join(f'<div class="hol" style="left:{p(f):.2f}%" title="{E(n)}"></div>' for f, n in feriados if d0 <= f < d1)
    eixo = "".join(f'<span style="left:{p(t):.2f}%">{MESES[t.month - 1]}{" " + t.strftime("%y") if t.month == 1 else ""}</span>' for t in ticks)
    h = [f'<div></div><div class="axis">{eixo}</div>']
    for dev in a["devs"]:
        barras = []
        for x in ausencias:
            if x["dev"] == dev and x["fim"] >= d0:
                barras.append((max(x["ini"], d0), x["fim"], x["motivo"], "off", x["motivo"]))
        for i in itens:
            # pausado só entra se tem data de retomada (início)
            if i["dev"] != dev or not (i["estado"] == "andamento" or (i["estado"] == "pausado" and i["ini"])):
                continue
            ini = max(i["ini"] or d0, d0)
            if i["fim"] and i["fim"] < d0:
                continue
            if i["fim"]:
                cls = "soon" if i["fim"] <= hoje + timedelta(days=7) else ""
                cls += " pause" if i["estado"] == "pausado" else ""
                barras.append((ini, i["fim"], i["frente"], cls, i["fim"].strftime("%d/%m")))
            else:
                barras.append((ini, ini + timedelta(days=21), i["frente"], "open", "sem prazo"))
        barras.sort(key=lambda b: b[0])
        lanes = []  # sub-faixas sem sobreposição
        for b in barras:
            for lane in lanes:
                if lane[-1][1] < b[0]:
                    lane.append(b)
                    break
            else:
                lanes.append([b])
        lanes = lanes or [[]]
        for n, lane in enumerate(lanes):
            cls = "lane sub" if n < len(lanes) - 1 else "lane"
            h.append(f'<div class="who">{E(dev) if n == 0 else ""}</div><div class="{cls}">{deco}')
            for k, (ini, fim, rot, c, sufixo) in enumerate(lane):
                l, r = p(ini), p(fim + timedelta(days=1))
                w = r - l
                tip = E(f"{rot}: {ini.isoformat()} a {fim.isoformat()}" if c != "open" else f"{rot}: desde {ini.isoformat()}, sem prazo")
                fora = w < 9 and k == len(lane) - 1 and c != "off"
                h.append(f'<div class="bar {c}" style="left:{l:.2f}%;width:{w:.2f}%" title="{tip}">{"" if fora else E(rot)}</div>')
                if fora:
                    h.append(f'<span class="lbl" style="left:calc({r:.2f}% + 4px)">{E(rot)} · {E(sufixo)}</span>')
            h.append("</div>")
    leg = ('<div class="gleg"><span><i style="background:var(--accent)"></i>frente</span>'
           '<span><i style="background:var(--warn)"></i>prazo nos próximos 7 dias</span>'
           '<span><i style="background:var(--accent);opacity:.55"></i>pausado (retomada)</span>'
           '<span><i style="background:linear-gradient(90deg,var(--accent),transparent)"></i>sem prazo</span>'
           '<span><i style="background:repeating-linear-gradient(45deg,var(--line) 0 3px,transparent 3px 6px);border:1px solid var(--line)"></i>ausência</span>'
           + ('<span>┆ feriado</span>' if any(d0 <= f < d1 for f, _ in feriados) else "") + "</div>")
    return (f'<section><h2>Alocação dos devs <small>{d0.isoformat()} a {d1.isoformat()} · ordem alfabética</small></h2>'
            f'<div class="gantt">{"".join(h)}</div>{leg}</section>')


def pagina(itens, a, ausencias, feriados, hoje, titulo, meses, ordem):
    cap = []
    if a["ausentes"]:
        cap.append("Ausentes: " + ", ".join(f"{x['dev']} (até {fmt(x['fim'])})" for x in a["ausentes"]))
    if a["sobrecarga"]:
        cap.append("Em mais de uma frente: " + ", ".join(f"{dev} ({len({x['frente'] for x in l})})" for dev, l in a["sobrecarga"].items()))
    cap.append("Sem frente hoje: " + (", ".join(a["livres"]) or "ninguém"))
    if a["livres_depois"]:
        cap.append("Ficam livres: " + ", ".join(f"{dev} após {fmt(x)}" for dev, x in sorted(a["livres_depois"].items(), key=lambda t: t[1])))
    if a["vencidos"]:
        cap.append("Prazo vencido: " + ", ".join(i["frente"] for i in a["vencidos"]))
    secs = [f'<section><h2>Capacidade</h2><div class="cap">{"".join(f"<div>{E(c)}</div>" for c in cap)}</div></section>']

    cols = []
    for g, frentes in colunas(itens, ordem).items():
        lis = []
        for f in frentes:
            quem = f["devs"] or "sem dono"
            extra = (" · " + f["nota"]) if f["nota"] else ""
            vazio = "pausado" if f["estado"] == "pausado" else "—"
            lis.append(f'<li><span><b>{E(f["frente"])}</b>: <span class="q">{E(quem + extra)}</span></span>{pill(f["fim"], hoje, vazio)}</li>')
        cols.append(f'<section><h2>{E(g)}</h2><ul>{"".join(lis)}</ul></section>')
    secs.append(f'<div class="cols">{"".join(cols)}</div>')

    grupos = agrupar(itens)
    def lista(est):
        out = []
        for (proj, frente, e), l in grupos.items():
            if e != est:
                continue
            nota = "; ".join(dict.fromkeys(x["nota"] for x in l if x["nota"]))
            fins = [x["fim"] for x in l if x["fim"]]
            out.append(f'<li><span><b>{E(frente)}</b>{(": " + E(nota)) if nota else ""}</span>{pill(max(fins) if fins else None, hoje)}</li>')
        return "".join(out)
    esp, bkl = lista("especificacao"), lista("backlog")
    if esp or bkl:
        secs.append('<div class="cols">'
                    + (f'<section><h2>Em especificação <small>alocar</small></h2><ul>{esp}</ul></section>' if esp else "")
                    + (f'<section><h2>Backlog <small>contexto</small></h2><ul>{bkl}</ul></section>' if bkl else "")
                    + "</div>")
    pend = []
    if a["sem_dono"]:
        pend.append(f'<li><span><b>Sem dono</b>: {E(" · ".join(a["sem_dono"]))}</span></li>')
    if a["sem_prazo"]:
        pend.append(f'<li><span><b>Sem prazo</b>: {E(" · ".join(a["sem_prazo"]))}</span></li>')
    if pend:
        secs.append(f'<section><h2>Sair com dono e prazo</h2><ul class="flat">{"".join(pend)}</ul></section>')
    secs.append(gantt(itens, a, ausencias, feriados, hoje, meses))

    leg = ('<span class="d late">vencido</span><span class="d soon">até 7 dias</span>'
           '<span class="d">depois</span><span class="d none">sem prazo</span>')
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(titulo)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Sans+Condensed:wght@700&family=IBM+Plex+Mono:wght@500&display=swap">
<style>{CSS}</style></head><body><div class="wrap">
<header><h1>{E(titulo)}</h1><div class="meta">Gerado do vault em {hoje.isoformat()} (scripts/alocacao.py) {leg}</div></header>
{"".join(secs)}
</div></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("saida", nargs="?")
    ap.add_argument("--texto", action="store_true")
    ap.add_argument("--titulo", default="Alocação da equipe")
    ap.add_argument("--projetos", default="")
    ap.add_argument("--gestores", default="", help="ordem das colunas")
    ap.add_argument("--meses", type=int, default=6)
    ap.add_argument("--hoje", default="")
    o = ap.parse_args()
    if not o.texto and not o.saida:
        ap.error("informe <saida.html> ou --texto")
    global ANO
    hoje = d(o.hoje) or date.today()
    ANO = hoje.year
    itens = ler_alocacao({p.strip() for p in o.projetos.split(",") if p.strip()} or None)
    pessoas, ausencias, feriados = ler_equipe()
    a = analisar(itens, pessoas, ausencias, hoje)
    if o.texto:
        print(texto(itens, a, hoje))
        return
    ordem = [g.strip() for g in o.gestores.split(",") if g.strip()]
    Path(o.saida).write_text(pagina(itens, a, ausencias, feriados, hoje, o.titulo, o.meses, ordem), encoding="utf-8")
    print(f"{len(itens)} itens de alocação, {len(a['devs'])} pessoas -> {o.saida}")


if __name__ == "__main__":
    main()
