"""Estado por aparelho: dispositivos/<codename>-<serial>/estado.json (fase, gates, backups, resultados)."""
import argparse
import json
import sys

from adb_util import agora, emitir, pasta_dispositivo

GATES = ("G1", "G2", "G3")


def caminho(serial, codename=None):
    return pasta_dispositivo(serial, codename) / "estado.json"


def carregar(serial):
    c = caminho(serial)
    return json.loads(c.read_text(encoding="utf-8")) if c.is_file() else None


def novo(serial, codename=None):
    return {"serial": serial, "codename": codename or "desconhecido", "criado": agora(), "fase": 0,
            "gates": {g: {"aprovado": False} for g in GATES}, "backups": [], "resultados": {}}


def salvar(serial, est):
    c = caminho(serial, est.get("codename") if est.get("codename") != "desconhecido" else None)
    c.parent.mkdir(parents=True, exist_ok=True)
    c.write_text(json.dumps(est, ensure_ascii=False, indent=2), encoding="utf-8")
    return c


def atualizar(serial, fn, codename=None):
    est = carregar(serial) or novo(serial, codename)
    if codename and est.get("codename") == "desconhecido":
        est["codename"] = codename
    fn(est)
    salvar(serial, est)
    return est


def gate_aprovado(serial, gate):
    try:
        est = carregar(serial)
        return bool(est and est["gates"][gate].get("aprovado") is True)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def registrar_resultado(serial, nome, dados):
    atualizar(serial, lambda e: e["resultados"].__setitem__(nome, {"data": agora(), **dados}))


def registrar_backup(serial, caminho_backup, sha256, itens=0):
    atualizar(serial, lambda e: e["backups"].append(
        {"data": agora(), "caminho": caminho_backup, "sha256": sha256, "itens": itens}))


def _json_ou_texto(v):
    try:
        return json.loads(v)
    except ValueError:
        return v


def main():
    p = argparse.ArgumentParser(description="Estado do aparelho")
    sub = p.add_subparsers(dest="cmd", required=True)
    for nome in ("init", "show", "aprovar-gate", "registrar"):
        s = sub.add_parser(nome)
        s.add_argument("--serial", required=True)
        if nome == "init":
            s.add_argument("--codename", default=None)
        if nome == "aprovar-gate":
            s.add_argument("gate", choices=GATES)
            s.add_argument("--confirmacao", required=True, help="texto literal da confirmação do usuário")
            s.add_argument("--evidencia", action="append", default=[])
            s.add_argument("--revogar", action="store_true")
        if nome == "registrar":
            s.add_argument("--fase", type=int)
            s.add_argument("--resultado", nargs=2, metavar=("NOME", "JSON"))
            s.add_argument("--backup", nargs=2, metavar=("CAMINHO", "SHA256"))
    a = p.parse_args()

    try:
        if a.cmd == "init":
            if carregar(a.serial):
                emitir({"ok": True, "criado": False, "arquivo": str(caminho(a.serial))})
            est = novo(a.serial, a.codename)
            emitir({"ok": True, "criado": True, "arquivo": str(salvar(a.serial, est))})
        est = carregar(a.serial)
        if est is None:
            emitir({"ok": False, "erro": "estado.json inexistente; rode 'init'"}, 1)
        if a.cmd == "show":
            emitir({"ok": True, "fase": est["fase"], "codename": est["codename"],
                    "gates": {g: est["gates"].get(g, {}).get("aprovado", False) for g in GATES},
                    "backups": len(est["backups"]), "resultados": list(est["resultados"])})
        if a.cmd == "aprovar-gate":
            est["gates"][a.gate] = {"aprovado": not a.revogar, "data": agora(),
                                    "usuario_confirmou": a.confirmacao, "evidencias": a.evidencia}
            salvar(a.serial, est)
            emitir({"ok": True, "gate": a.gate, "aprovado": not a.revogar})
        if a.cmd == "registrar":
            if a.fase is not None:
                est["fase"] = a.fase
            if a.resultado:
                est["resultados"][a.resultado[0]] = {"data": agora(), "dados": _json_ou_texto(a.resultado[1])}
            if a.backup:
                est["backups"].append({"data": agora(), "caminho": a.backup[0], "sha256": a.backup[1]})
            salvar(a.serial, est)
            emitir({"ok": True, "fase": est["fase"]})
    except (OSError, ValueError, KeyError) as e:
        emitir({"ok": False, "erro": str(e)}, 1)


if __name__ == "__main__":
    main()
