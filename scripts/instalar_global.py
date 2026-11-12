"""Instala o segundo cérebro no nível do usuário, para dar contexto a TODAS as sessões do Claude Code.

Três peças, todas idempotentes (rodar de novo atualiza):
1. ~/.claude/CLAUDE.md: bloco entre marcadores `segundo-cerebro:inicio/fim` (global/CLAUDE.md).
2. ~/.claude/skills/segundo-cerebro/SKILL.md (global/skills/segundo-cerebro/).
3. ~/.claude/settings.json: hook SessionStart rodando scripts/contexto_sessao.py.

{{CAMINHO_VAULT}} é trocado pelo caminho absoluto deste vault.
Faz backup (.bak) de CLAUDE.md e settings.json antes de alterar.

Uso:
  python -I -X utf8 scripts/instalar_global.py --dry-run   # mostra o que faria
  python -I -X utf8 scripts/instalar_global.py             # instala
  python -I -X utf8 scripts/instalar_global.py --remover   # desfaz as três peças
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
HOME_CLAUDE = Path.home() / ".claude"
INICIO, FIM = "<!-- segundo-cerebro:inicio", "<!-- segundo-cerebro:fim -->"
BLOCO_RE = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIM) + r"\n?", re.S)
MARCA_HOOK = "contexto_sessao.py"


def preencher(texto):
    return texto.replace("{{CAMINHO_VAULT}}", VAULT.as_posix())


def escrever(caminho, conteudo, dry):
    if caminho.exists() and caminho.read_text(encoding="utf-8") == conteudo:
        print(f"= sem mudança: {caminho}")
        return
    print(f"{'(dry) ' if dry else ''}escrevendo: {caminho}")
    if dry:
        return
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if caminho.exists() and caminho.suffix in (".md", ".json") and caminho.name != "SKILL.md":
        shutil.copy2(caminho, caminho.with_name(caminho.name + ".bak"))
    caminho.write_text(conteudo, encoding="utf-8")


def claude_md(remover, dry):
    alvo = HOME_CLAUDE / "CLAUDE.md"
    atual = alvo.read_text(encoding="utf-8") if alvo.exists() else ""
    sem = BLOCO_RE.sub("", atual)
    if remover:
        novo = sem
    else:
        bloco = preencher((VAULT / "global" / "CLAUDE.md").read_text(encoding="utf-8")).rstrip("\n") + "\n"
        novo = (sem.rstrip("\n") + "\n\n" if sem.strip() else "") + bloco
    escrever(alvo, novo, dry)


def skill(remover, dry):
    origem = VAULT / "global" / "skills" / "segundo-cerebro"
    destino = HOME_CLAUDE / "skills" / "segundo-cerebro"
    if remover:
        print(f"{'(dry) ' if dry else ''}removendo: {destino}")
        if not dry and destino.exists():
            shutil.rmtree(destino)
        return
    for arq in origem.rglob("*"):
        if arq.is_file():
            escrever(destino / arq.relative_to(origem), preencher(arq.read_text(encoding="utf-8")), dry)


def hook(remover, dry):
    alvo = HOME_CLAUDE / "settings.json"
    dados = json.loads(alvo.read_text(encoding="utf-8")) if alvo.exists() and alvo.read_text(encoding="utf-8").strip() else {}
    eventos = dados.setdefault("hooks", {})
    grupos = [g for g in eventos.get("SessionStart", []) if not any(MARCA_HOOK in h.get("command", "") for h in g.get("hooks", []))]
    if not remover:
        script = (VAULT / "scripts" / MARCA_HOOK).as_posix()
        python = Path(sys.executable).as_posix()
        grupos.append({"hooks": [{"type": "command", "command": f'"{python}" -I -X utf8 "{script}"', "timeout": 10}]})
    if grupos:
        eventos["SessionStart"] = grupos
    else:
        eventos.pop("SessionStart", None)
    if not eventos:
        dados.pop("hooks", None)
    escrever(alvo, json.dumps(dados, ensure_ascii=False, indent=2) + "\n", dry)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--remover", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"vault: {VAULT.as_posix()}  |  destino: {HOME_CLAUDE.as_posix()}")
    claude_md(a.remover, a.dry_run)
    skill(a.remover, a.dry_run)
    hook(a.remover, a.dry_run)
    if not a.dry_run:
        print("ok. Vale para sessões novas do Claude Code.")


if __name__ == "__main__":
    main()
