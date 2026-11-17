"""Traz para esta cópia do vault as novidades do template (skills, scripts, docs, global/, templates/).

Merge de 3 vias por arquivo (git merge-file): base = commit do template aplicado por último
(gravado em `.segundo-cerebro/template.json`), "template" = template atual, "este vault" = HEAD local.
Personalização local sobrevive; trecho mexido dos dois lados vira conflito (marcadores <<<<<<<).
Conteúdo pessoal nunca é tocado: projetos/, diario/, arquivo/, ref/, agora.md, inbox.md, README.md.

Uso (na raiz do vault):
  python -I -X utf8 scripts/atualizar_template.py --iniciar <url-do-template> [--base <sha>]
  python -I -X utf8 scripts/atualizar_template.py --status
  python -I -X utf8 scripts/atualizar_template.py --aplicar
  python -I -X utf8 scripts/atualizar_template.py --ignorar <caminho>   (nunca atualizar esse arquivo/pasta)

--iniciar sem --base: base = template atual (vault considerado em dia). Vault criado de uma cópia
do template: passar --base com o commit do template de onde ele saiu.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
CONF = VAULT / ".segundo-cerebro" / "template.json"
REMOTO = "template"
PESSOAL = ["projetos", "diario", "arquivo", "ref", "agora.md", "inbox.md", "README.md", ".segundo-cerebro"]


def git(*a, ok=True):
    r = subprocess.run(["git", "-C", str(VAULT), *a], capture_output=True, text=True, encoding="utf-8")
    if ok and r.returncode != 0:
        sys.exit(f"ERRO git {' '.join(a)}: {(r.stderr or r.stdout).strip()}")
    return r


def ler_conf():
    if not CONF.exists():
        sys.exit("ERRO: vault sem vínculo com o template. Rodar --iniciar <url-do-template>.")
    return json.loads(CONF.read_text(encoding="utf-8"))


def gravar_conf(c):
    CONF.parent.mkdir(exist_ok=True)
    CONF.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def buscar(c):
    if git("remote", "get-url", REMOTO, ok=False).returncode != 0:
        git("remote", "add", "--no-tags", REMOTO, c["url"])
    git("remote", "set-url", "--push", REMOTO, "NUNCA-dar-push-do-vault-pessoal-no-template")
    git("fetch", "-q", "--no-tags", REMOTO, c["branch"])
    return git("rev-parse", f"{REMOTO}/{c['branch']}").stdout.strip()


def mudancas(c, novo):
    excl = [f":(exclude){p}" for p in PESSOAL + c.get("ignorar", [])]
    r = git("diff", "--name-status", "--no-renames", c["base"], novo, "--", ".", *excl)
    return [ln.split("\t", 1) for ln in r.stdout.splitlines() if ln]


def blob(rev, caminho):
    r = subprocess.run(["git", "-C", str(VAULT), "show", f"{rev}:{caminho}"], capture_output=True)
    return r.stdout if r.returncode == 0 else b""


def editado_aqui(c, caminho):
    """Arquivo local difere da versão base do template?"""
    return blob("HEAD", caminho).replace(b"\r\n", b"\n") != blob(c["base"], caminho).replace(b"\r\n", b"\n")


def mesclar(caminho, base, novo):
    """3 vias sobre blobs (LF, sem efeito de autocrlf). Retorna nº de conflitos; -1 se não deu."""
    nosso, deles = blob("HEAD", caminho), blob(novo, caminho)
    antigo = blob(base, caminho) if base else b""
    if 0 in nosso or 0 in deles or 0 in antigo:  # binário
        return -1
    with tempfile.TemporaryDirectory() as d:
        arqs = []
        for nome, dado in (("vault", nosso), ("base", antigo), ("template", deles)):
            f = Path(d) / nome
            f.write_bytes(dado.replace(b"\r\n", b"\n"))
            arqs.append(str(f))
        r = subprocess.run(["git", "merge-file", "-p", "-L", "este vault", "-L", "base", "-L", "template", *arqs],
                           capture_output=True)
    if r.returncode < 0 or r.returncode > 127:
        return -1
    destino = VAULT / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(r.stdout)
    if r.returncode == 0:
        git("add", "--", caminho)
    return r.returncode


def status(c):
    novo = buscar(c)
    if novo == c["base"]:
        print(f"Em dia com o template ({novo[:7]}).")
        return
    print(f"Base {c['base'][:7]} -> template {novo[:7]}\n\nNovidades:")
    print(git("log", "--format=- %h %ad %s", "--date=short", f"{c['base']}..{novo}").stdout.rstrip())
    print("\nArquivos (A novo, M alterado, D removido no template):")
    for st, caminho in mudancas(c, novo):
        marca = "  [editado aqui]" if (VAULT / caminho).exists() and editado_aqui(c, caminho) else ""
        print(f"  {st} {caminho}{marca}")


def aplicar(c):
    sujo = git("status", "--porcelain").stdout.strip()
    if sujo:
        sys.exit("ERRO: há mudanças não commitadas. Commitar (/fechar) antes de atualizar.\n" + sujo)
    novo = buscar(c)
    if novo == c["base"]:
        print(f"Em dia com o template ({novo[:7]}).")
        return
    limpos, conflitos, falhas = [], [], []
    for st, caminho in mudancas(c, novo):
        existe = (VAULT / caminho).exists()
        if st == "A" and not existe:
            git("checkout", novo, "--", caminho)
            limpos.append(f"A {caminho}")
        elif st == "D":
            if existe and editado_aqui(c, caminho):
                falhas.append(f"{caminho}: removido no template, mas editado aqui (decidir se apaga)")
            elif existe:
                git("rm", "-q", "--", caminho)
                limpos.append(f"D {caminho}")
        elif st == "M" and not existe:
            falhas.append(f"{caminho}: mudou no template, mas foi apagado aqui (trazer de volta ou --ignorar)")
        else:
            r = mesclar(caminho, c["base"] if st == "M" else None, novo)
            if r == 0:
                limpos.append(f"{st} {caminho}")
            elif r > 0:
                conflitos.append(caminho)
            else:
                falhas.append(f"{caminho}: binário editado dos dois lados")
    anterior = c["base"]
    c["base"] = novo
    gravar_conf(c)
    git("add", "--", CONF.relative_to(VAULT).as_posix())
    print(f"Template aplicado até {novo[:7]} (sem commit; base anterior {anterior[:7]}).")
    print(f"\nLimpos ({len(limpos)}):")
    print("\n".join(f"  {x}" for x in limpos) or "  nenhum")
    if conflitos:
        print(f"\nCONFLITOS ({len(conflitos)}): resolver os marcadores <<<<<<< e dar git add:")
        print("\n".join(f"  {x}" for x in conflitos))
    if falhas:
        print(f"\nFALHAS ({len(falhas)}): ver `git diff {anterior[:7]} {novo[:7]} -- <arquivo>` e decidir à mão:")
        print("\n".join(f"  {x}" for x in falhas))
    tocados = [x.split(" ", 1)[1] for x in limpos] + conflitos
    if any(t.startswith("global/") or t == "scripts/contexto_sessao.py" for t in tocados):
        print("\nglobal/ mudou: rodar `python -I -X utf8 scripts/instalar_global.py` depois do commit.")
    if any(t.startswith(".claude/skills/") for t in tocados):
        print("Skills mudaram: valem em sessão nova do Claude Code.")
    if b"{{" in (VAULT / "CLAUDE.md").read_bytes():
        print("CLAUDE.md tem {{...}}: campo novo na Configuração, preencher.")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--iniciar", metavar="URL")
    g.add_argument("--status", action="store_true")
    g.add_argument("--aplicar", action="store_true")
    g.add_argument("--ignorar", metavar="CAMINHO")
    ap.add_argument("--base")
    ap.add_argument("--branch", default="main")
    a = ap.parse_args()
    if a.iniciar:
        c = {"url": a.iniciar, "branch": a.branch, "base": "", "ignorar": []}
        if CONF.exists():
            c["ignorar"] = json.loads(CONF.read_text(encoding="utf-8")).get("ignorar", [])
        novo = buscar(c)
        c["base"] = git("rev-parse", a.base).stdout.strip() if a.base else novo
        gravar_conf(c)
        print(f"Vinculado a {a.iniciar} ({a.branch}), base {c['base'][:7]}. Commitar .segundo-cerebro/template.json.")
    elif a.ignorar:
        c = ler_conf()
        c.setdefault("ignorar", []).append(a.ignorar.replace("\\", "/"))
        gravar_conf(c)
        print(f"Ignorando {a.ignorar} nas próximas atualizações.")
    elif a.status:
        status(ler_conf())
    else:
        aplicar(ler_conf())


if __name__ == "__main__":
    main()
