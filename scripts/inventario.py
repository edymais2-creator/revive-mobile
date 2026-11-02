"""Inventário do aparelho: props, CPU/RAM/armazenamento, bateria, bootloader, codename."""
import json
import re

import estado
from adb_util import Adb, dry, emitir, parser_base

PROPS = {
    "codename": "ro.product.device", "fabricante": "ro.product.manufacturer", "modelo": "ro.product.model",
    "android": "ro.build.version.release", "sdk": "ro.build.version.sdk",
    "patch_seguranca": "ro.build.version.security_patch", "soc": "ro.board.platform",
    "hardware": "ro.hardware", "abi": "ro.product.cpu.abi", "treble": "ro.treble.enabled",
    "dinamica": "ro.boot.dynamic_partitions", "slot": "ro.boot.slot_suffix",
    "bl_travado": "ro.boot.flash.locked", "verified_boot": "ro.boot.verifiedbootstate",
    "vbmeta": "ro.boot.vbmeta.device_state", "build": "ro.build.display.id",
}


def parse_getprop(texto):
    return dict(re.findall(r"^\[([^\]]+)\]: \[(.*)\]$", texto, re.M))


def main():
    p = parser_base("Inventário do aparelho")
    a = p.parse_args()
    adb = Adb(a.serial, dry(a), a.timeout)
    cmds = {"getprop": ["shell", "getprop"], "meminfo": ["shell", "cat /proc/meminfo"],
            "cpuinfo": ["shell", "cat /proc/cpuinfo"], "df": ["shell", "df /data"],
            "bateria": ["shell", "dumpsys battery"]}
    brutos, arquivos = {}, {}
    for nome, args in cmds.items():
        rc, out, arq = adb.bruto(nome, args)
        brutos[nome] = out if rc == 0 else ""
        arquivos[nome] = arq
    if a.dry_run:
        emitir({"ok": True, "dry_run": True, "serial": a.serial, "comandos": adb.comandos})

    props = parse_getprop(brutos["getprop"])
    if not props:
        emitir({"ok": False, "erro": "sem resposta do aparelho (adb/serial/autorização USB)",
                "serial": a.serial, "bruto": arquivos["getprop"]}, 1)
    inv = {k: props.get(v, "") for k, v in PROPS.items()}
    mem = re.search(r"MemTotal:\s+(\d+)", brutos["meminfo"])
    inv["ram_mb"] = int(mem.group(1)) // 1024 if mem else None
    inv["cpu_nucleos"] = len(re.findall(r"^processor\s*:", brutos["cpuinfo"], re.M)) or None
    linhas = brutos["df"].strip().splitlines()
    if len(linhas) > 1:
        c = linhas[-1].split()
        if len(c) >= 4 and c[1].isdigit():
            inv["data_total_mb"], inv["data_livre_mb"] = int(c[1]) // 1024, int(c[3]) // 1024
    bat = dict(re.findall(r"^\s*(level|temperature|health|status):\s*(\d+)", brutos["bateria"], re.M))
    inv["bateria_pct"] = int(bat["level"]) if "level" in bat else None
    inv["bateria_temp_c"] = int(bat["temperature"]) / 10 if "temperature" in bat else None
    inv["bootloader_desbloqueado"] = (inv["bl_travado"] == "0" or inv["vbmeta"] == "unlocked"
                                      or inv["verified_boot"] == "orange")

    estado.atualizar(a.serial, lambda e: None, codename=inv["codename"] or None)
    pasta = adb.dir
    (pasta / "inventario.json").write_text(json.dumps(inv, ensure_ascii=False, indent=2), encoding="utf-8")
    estado.registrar_resultado(a.serial, "inventario", {"arquivo": str((pasta / "inventario.json").relative_to(pasta.parents[1]))})
    emitir({"ok": True, "serial": a.serial, "inventario": inv, "bruto": arquivos["getprop"]})


if __name__ == "__main__":
    main()
