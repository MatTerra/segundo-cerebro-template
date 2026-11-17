"""Registra o turno do dia (início, pausa, volta, fim) na linha `Turno:` de diario/YYYY-MM-DD.md.

Entende texto livre: os horários e as palavras em volta viram marcações.
  python -I -X utf8 scripts/turno.py entrei 0800 e pretendo almoçar 1230
  python -I -X utf8 scripts/turno.py voltei 13h30
  python -I -X utf8 scripts/turno.py saí agora
  python -I -X utf8 scripts/turno.py                 (só mostra)
  python -I -X utf8 scripts/turno.py desfaz          (remove a última marcação)
  python -I -X utf8 scripts/turno.py ontem saí 18h   (data: ontem, anteontem ou YYYY-MM-DD)

Formato da linha: `Turno: 08:00–12:30 · 13:30–~18:00 · total 9h00 (previsto)`.
`~HH:MM` = horário previsto (ainda não confirmado); `…` = intervalo aberto.
Faz git pull/commit/push só do arquivo do diário (`--sem-git` para pular).
"""
import re
import subprocess
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
INICIO = ("entr", "cheg", "comec", "inici", "volt", "retom", "retorn", "abri", "start")
FIM = ("sai", "almoc", "paus", "parei", "fim", "termin", "encerr", "interv", "fech", "stop")
PREVISTO = ("pretend", "vou", "prev", "planej", "devo", "deve", "plano")
LINHA = re.compile(r"^Turno:.*$", re.M)
INTERVALO = re.compile(r"(\d\d:\d\d)–(~?\d\d:\d\d|…)")


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def hora(tok):
    """'0800', '8:00', '8h', '12h30', '8' -> 'HH:MM'; senão None."""
    m = re.fullmatch(r"(\d{1,2})(?:[:h](\d{2})?)?|(\d{2})(\d{2})", tok)
    if not m:
        return None
    h, mi = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
    h, mi = int(h), int(mi or 0)
    return f"{h:02d}:{mi:02d}" if h < 24 and mi < 60 else None


def interpretar(args):
    """Texto livre -> (dia, [(tipo, 'HH:MM', previsto)], desfaz, pedido_sem_horario)."""
    dia, eventos, tipo, prev, desfaz, solto = date.today(), [], None, False, False, False
    for bruto in args:
        for tok in re.split(r"[\s,;.]+", norm(bruto)):
            if not tok:
                continue
            if re.fullmatch(r"\d{4}-\d\d-\d\d", tok):
                dia = date.fromisoformat(tok)
            elif tok == "ontem":
                dia = date.today() - timedelta(days=1)
            elif tok == "anteontem":
                dia = date.today() - timedelta(days=2)
            elif tok in ("desfaz", "desfazer", "undo"):
                desfaz = True
            elif tok.startswith(PREVISTO):
                prev = solto = True
            elif tok.startswith(INICIO):
                tipo, solto = "inicio", True
            elif tok.startswith(FIM):
                tipo, solto = "fim", True
            elif tok == "agora" or hora(tok):
                h = datetime.now().strftime("%H:%M") if tok == "agora" else hora(tok)
                eventos.append((tipo, h, prev))
                tipo, prev, solto = None, False, False
    return dia, eventos, desfaz, solto


def ler(texto):
    m = LINHA.search(texto)
    return [list(p) for p in INTERVALO.findall(m.group(0))] if m else []


def aplicar(iv, tipo, h, prev):
    marca = f"~{h}" if prev else h
    aberto = bool(iv) and (iv[-1][1] == "…" or iv[-1][1].startswith("~"))
    if tipo is None:
        tipo = "fim" if aberto else "inicio"
    if tipo == "inicio":
        if prev:
            raise ValueError("início previsto não é registrado; diga quando começar")
        antes = iv[-2][1].lstrip("~") if len(iv) > 1 else "00:00"
        if iv and iv[-1][1] == "…":
            if minutos(antes, h) < 0:
                raise ValueError(f"início {h} antes do fim anterior {antes}")
            iv[-1][0] = h  # correção do início do intervalo aberto
        elif iv and iv[-1][1].startswith("~"):
            iv[-1][1] = iv[-1][1][1:]  # pausa prevista vira real ao voltar
            iv.append([h, "…"])
        else:
            if iv and minutos(iv[-1][1], h) < 0:
                raise ValueError(f"início {h} antes do fim anterior {iv[-1][1]}")
            iv.append([h, "…"])
    else:
        if not iv:
            raise ValueError(f"fim às {h} sem início registrado")
        if minutos(iv[-1][0], h) <= 0:
            raise ValueError(f"fim {h} não é depois do início {iv[-1][0]}")
        iv[-1][1] = marca  # fecha o aberto, confirma o previsto ou corrige o último fim
    return iv


def minutos(a, b):
    ha, ma = map(int, a.split(":"))
    hb, mb = map(int, b.split(":"))
    return (hb * 60 + mb) - (ha * 60 + ma)


def formatar(iv, dia):
    total, nota = 0, ""
    for ini, fim in iv:
        if fim == "…":
            if dia == date.today():
                total += max(0, minutos(ini, datetime.now().strftime("%H:%M")))
                nota = " (até agora)"
            else:
                nota = " (intervalo sem fim)"
        else:
            total += minutos(ini, fim.lstrip("~"))
            if fim.startswith("~") and not nota:
                nota = " (previsto)"
    partes = " · ".join(f"{a}–{b}" for a, b in iv)
    return f"Turno: {partes} · total {total // 60}h{total % 60:02d}{nota}"


def gravar(arq, dia, linha):
    if arq.exists():
        texto = arq.read_text(encoding="utf-8")
    else:
        modelo = VAULT / "templates" / "diario.md"
        base = modelo.read_text(encoding="utf-8") if modelo.exists() else "---\ntipo: diario\ndata: {{date}}\n---\n# {{date}}\n"
        texto = base.replace("{{date}}", dia.isoformat())
    if LINHA.search(texto):
        texto = LINHA.sub(linha, texto, count=1)
    else:
        texto, n = re.subn(r"^(# .*\n)", rf"\1\n{linha}\n", texto, count=1, flags=re.M)
        if not n:
            texto = texto.rstrip("\n") + f"\n\n{linha}\n"
    arq.parent.mkdir(exist_ok=True)
    arq.write_text(texto, encoding="utf-8")


def git(*a):
    return subprocess.run(["git", "-C", str(VAULT), *a], capture_output=True, text=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if a != "--sem-git"]
    usar_git = "--sem-git" not in sys.argv
    dia, eventos, desfaz, solto = interpretar(args)
    arq = VAULT / "diario" / f"{dia.isoformat()}.md"
    mexe = bool(eventos) or desfaz

    if mexe and usar_git:
        git("pull", "-q", "--ff-only")
    iv = ler(arq.read_text(encoding="utf-8")) if arq.exists() else []

    if not mexe:
        if solto:
            print(f"ERRO: não achei horário em: {' '.join(args)}. Ex.: 'entrei 08:00', 'almoço 12h30', 'saí agora'.")
            sys.exit(2)
        print(formatar(iv, dia) + f" [{dia}]" if iv else f"Sem turno registrado em {dia}.")
        return

    try:
        if desfaz:
            if not iv:
                raise ValueError("nada para desfazer")
            if iv[-1][1] == "…":
                iv.pop()
            else:
                iv[-1][1] = "…"
        for tipo, h, prev in eventos:
            iv = aplicar(iv, tipo, h, prev)
    except ValueError as e:
        print(f"ERRO: {e}. Atual: {formatar(iv, dia) if iv else 'vazio'}")
        sys.exit(2)

    linha = formatar(iv, dia) if iv else "Turno: —"
    gravar(arq, dia, linha)
    status = ""
    if usar_git:
        rel = arq.relative_to(VAULT).as_posix()
        git("add", rel)
        c = git("commit", "-q", "-m", f"turno: {dia.isoformat()}", "--", rel)
        p = git("push", "-q") if c.returncode == 0 else c
        status = " · git ok" if p.returncode == 0 else f" · git falhou: {(p.stderr or p.stdout).strip()[:120]}"
    print(f"{linha} [{dia}]{status}")


if __name__ == "__main__":
    main()
