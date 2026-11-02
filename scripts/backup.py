"""Backup não destrutivo: lista de apps + APKs, mídia, manifesto SHA-256 e verificação."""
import hashlib
import json
from pathlib import Path

import estado
from adb_util import Adb, agora, dry, emitir, parser_base

MIDIA = ["/sdcard/DCIM", "/sdcard/Pictures", "/sdcard/Documents", "/sdcard/Download", "/sdcard/Movies",
         "/sdcard/Music"]


def sha256(arq):
    h = hashlib.sha256()
    with open(arq, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def manifesto(pasta):
    """{caminho_relativo: sha256} de tudo na pasta, exceto o próprio manifesto."""
    return {str(f.relative_to(pasta)): sha256(f) for f in sorted(pasta.rglob("*"))
            if f.is_file() and f.name != "manifesto.json"}


def verificar(pasta):
    man = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))["arquivos"]
    faltando = [k for k in man if not (pasta / k).is_file()]
    corrompidos = [k for k, h in man.items() if k not in faltando and sha256(pasta / k) != h]
    return {"ok": not faltando and not corrompidos, "arquivos": len(man),
            "faltando": faltando[:10], "corrompidos": corrompidos[:10]}


def main():
    p = parser_base("Backup de apps e mídia com hash")
    p.add_argument("--destino", help="pasta de saída (padrão: dispositivos/<id>/backups/<data>)")
    p.add_argument("--sem-midia", action="store_true")
    p.add_argument("--sem-apps", action="store_true")
    p.add_argument("--max-apps", type=int, default=200)
    p.add_argument("--verificar", metavar="PASTA", help="só verifica um backup existente contra o manifesto")
    a = p.parse_args()

    if a.verificar:
        pasta = Path(a.verificar)
        if not (pasta / "manifesto.json").is_file():
            emitir({"ok": False, "erro": "manifesto.json ausente"}, 1)
        emitir(verificar(pasta))

    adb = Adb(a.serial, dry(a), a.timeout * 5)
    pasta = Path(a.destino) if a.destino else adb.dir / "backups" / agora().replace(":", "")
    resumo = {"apps": 0, "apks": 0, "midia_pastas": 0, "falhas": 0}

    if not a.sem_apps:
        rc, out, _ = adb.bruto("pm-list-3p", ["shell", "pm list packages -3"])
        pacotes = [l.split(":", 1)[1].strip() for l in out.splitlines() if l.startswith("package:")][:a.max_apps]
        if not a.dry_run:
            (pasta / "apps").mkdir(parents=True, exist_ok=True)
            (pasta / "apps" / "lista.json").write_text(json.dumps(pacotes, indent=1), encoding="utf-8")
        resumo["apps"] = len(pacotes)
        for pkg in pacotes if not a.dry_run else []:
            for linha in adb.shell(f"pm path {pkg}")["out"].splitlines():
                if linha.startswith("package:"):
                    dest = pasta / "apps" / pkg
                    dest.mkdir(exist_ok=True)
                    r = adb.run(["pull", linha[8:].strip(), str(dest)])
                    resumo["apks"] += r["rc"] == 0
                    resumo["falhas"] += r["rc"] != 0
        if a.dry_run:
            adb.run(["pull", "<apk de cada app>", str(pasta / "apps")])

    if not a.sem_midia:
        for origem in MIDIA:
            if a.dry_run:
                adb.run(["pull", origem, str(pasta / "midia")])
                continue
            (pasta / "midia").mkdir(parents=True, exist_ok=True)
            r = adb.run(["pull", origem, str(pasta / "midia")], timeout=a.timeout * 30)
            resumo["midia_pastas"] += r["rc"] == 0

    if a.dry_run:
        emitir({"ok": True, "dry_run": True, "destino": str(pasta), "comandos": adb.comandos[:12],
                "total_comandos": len(adb.comandos)})

    man = manifesto(pasta)
    texto = json.dumps({"criado": agora(), "arquivos": man}, indent=1)
    (pasta / "manifesto.json").write_text(texto, encoding="utf-8")
    hash_man = hashlib.sha256(texto.encode()).hexdigest()
    ver = verificar(pasta)
    estado.registrar_backup(a.serial, str(pasta), hash_man, len(man))
    emitir({"ok": ver["ok"], "destino": str(pasta), **resumo, "arquivos": len(man),
            "sha256_manifesto": hash_man, "verificado": ver["ok"]}, 0 if ver["ok"] else 1)


if __name__ == "__main__":
    main()
