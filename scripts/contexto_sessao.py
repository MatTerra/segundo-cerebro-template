"""Hook SessionStart global: injeta contexto do segundo cérebro em qualquer sessão do Claude Code.

- Sessão dentro do vault: não faz nada (o CLAUDE.md do vault já cobre).
- Repo ligado a um hub (`repos:` no frontmatter de projetos/<slug>/<slug>.md): status, estado,
  tarefas abertas e últimas linhas do Log desse(s) hub(s).
- Sem hub ligado: só o Foco do agora.md.

Instalado por scripts/instalar_global.py. Lê o JSON do hook no stdin (campo `cwd`).
Nunca falha a sessão: qualquer erro sai em silêncio com código 0.
Teste manual: python -I -X utf8 scripts/contexto_sessao.py --cwd <pasta>
"""
import json
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
MAX_CHARS = 3500
MAX_TAREFAS = 8
MAX_LOG = 3


def frontmatter(texto):
    if not texto.startswith("---"):
        return {}, texto
    _, fm, corpo = texto.split("---", 2)
    campos, chave = {}, None
    for line in fm.splitlines():
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if m:
            chave, valor = m.group(1), m.group(2).strip()
            if valor.startswith("[") and valor.endswith("]"):
                campos[chave] = [v.strip().strip("\"'") for v in valor[1:-1].split(",") if v.strip()]
            else:
                campos[chave] = valor.strip("\"'") if valor else []
        elif chave and re.match(r"^\s+-\s+", line) and isinstance(campos.get(chave), list):
            campos[chave].append(re.sub(r"^\s+-\s+", "", line).strip().strip("\"'"))
    return campos, corpo


def secao(corpo, titulo):
    m = re.search(rf"^## {re.escape(titulo)}\s*$(.*?)(?=^## |\Z)", corpo, re.M | re.S)
    linhas = m.group(1).splitlines() if m else []
    return [l for l in linhas if l.strip() and not re.match(r"^\s*(\d+\.|-|- \[ \])\s*$", l)]


def raiz_git(pasta):
    """Raiz do repo; em worktree (`.git` é arquivo com `gitdir: <repo>/.git/worktrees/x`), a do repo principal."""
    for p in [pasta, *pasta.parents]:
        git = p / ".git"
        if git.is_file():
            m = re.match(r"gitdir:\s*(.+)", git.read_text(encoding="utf-8").strip())
            alvo = Path(m.group(1)) if m else None
            if alvo and "worktrees" in alvo.parts:
                return alvo.parents[2] if alvo.parent.name == "worktrees" else p
            return p
        if git.exists():
            return p
    return pasta


def hubs():
    for md in sorted((VAULT / "projetos").glob("*/*.md")):
        if md.stem == md.parent.name:
            yield md


def resumo_hub(md):
    campos, corpo = frontmatter(md.read_text(encoding="utf-8"))
    rel = md.relative_to(VAULT).as_posix()
    out = [f"### {md.stem} ({rel})",
           " | ".join(f"{k}: {', '.join(v) if isinstance(v := campos[k], list) else v}" for k in ("status", "prioridade", "jira", "atualizado", "confianca") if campos.get(k))]
    estado = secao(corpo, "Estado")[:6]
    if estado:
        out += ["Estado:", *estado]
    abertas = [l.strip() for l in corpo.splitlines() if re.match(r"^\s*- \[ \] ", l)]
    if abertas:
        out += [f"Tarefas abertas ({len(abertas)}):", *abertas[:MAX_TAREFAS]]
    log = [l for l in secao(corpo, "Log") if l.lstrip().startswith("- ")][:MAX_LOG]
    if log:
        out += ["Log recente:", *log]
    return "\n".join(out)


def contexto(cwd):
    cwd = Path(cwd).resolve()
    if cwd == VAULT or VAULT in cwd.parents:
        return ""
    raiz = raiz_git(cwd)
    nomes = {p.name.lower() for p in [cwd, raiz, *raiz.parents][:4] if p.name}
    ligados = []
    for md in hubs():
        campos, _ = frontmatter(md.read_text(encoding="utf-8"))
        repos = campos.get("repos") or []
        repos = repos if isinstance(repos, list) else [repos]
        if {r.lower() for r in repos} & nomes:
            ligados.append((len(repos), md))
    ligados = [md for _, md in sorted(ligados, key=lambda x: x[0])]  # frente específica antes da conta guarda-chuva

    cab = (f"Segundo cérebro em `{VAULT.as_posix()}` (skill `segundo-cerebro` para consultar/registrar; "
           f"protocolo em `{VAULT.as_posix()}/CLAUDE.md`).")
    if ligados:
        corpo = f"Repo `{raiz.name}` ligado a: " + ", ".join(m.stem for m in ligados) + "\n\n" + "\n\n".join(resumo_hub(m) for m in ligados)
    else:
        agora = VAULT / "agora.md"
        foco = secao(frontmatter(agora.read_text(encoding="utf-8"))[1], "Foco")[:10] if agora.exists() else []
        corpo = f"Nenhum hub lista o repo `{raiz.name}` em `repos:`." + ("\nFoco atual (agora.md):\n" + "\n".join(foco) if foco else "")
    texto = cab + "\n" + corpo
    return texto if len(texto) <= MAX_CHARS else texto[:MAX_CHARS] + "\n[...cortado; ler o hub]"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        if "--cwd" in sys.argv:
            print(contexto(sys.argv[sys.argv.index("--cwd") + 1]))
            return
        bruto = sys.stdin.read() if not sys.stdin.isatty() else ""
        dados = json.loads(bruto) if bruto.strip() else {}
        texto = contexto(dados.get("cwd") or Path.cwd())
        if texto:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": texto}}, ensure_ascii=False))
    except Exception:  # hook nunca derruba a sessão
        pass


if __name__ == "__main__":
    main()
