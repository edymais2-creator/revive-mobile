"""Benchmark: boot (opcional), abertura de apps, jank (gfxinfo), RAM livre, bateria; compara antes/depois."""
import json
import re
import statistics
import time
from pathlib import Path

import estado
from adb_util import Adb, agora, dry, emitir, parser_base

# métrica -> True se "menor é melhor"
MENOR_MELHOR = {"boot_s": True, "app_ms": True, "jank_pct": True, "p90_ms": True, "ram_livre_mb": False}
LIMITE_REGRESSAO = 0.10


def num(padrao, texto, tipo=float):
    m = re.search(padrao, texto)
    return tipo(m.group(1)) if m else None


def medir_boot(adb):
    t0 = time.time()
    adb.run(["reboot"])
    adb.run(["wait-for-device"], timeout=300)
    while time.time() - t0 < 300:
        if adb.shell("getprop sys.boot_completed")["out"].strip() == "1":
            return round(time.time() - t0, 1)
        time.sleep(2)
    return None


def abrir_app(adb, pkg):
    adb.shell(f"am force-stop {pkg}")
    adb.shell(f"dumpsys gfxinfo {pkg} reset")
    out = adb.shell(f"am start -W -n $(cmd package resolve-activity --brief {pkg} | tail -n 1)")["out"]
    ms = num(r"TotalTime:\s*(\d+)", out)
    adb.shell("input swipe 500 1200 500 400 150")
    time.sleep(1)
    g = adb.shell(f"dumpsys gfxinfo {pkg}")["out"]
    adb.shell("input keyevent KEYCODE_HOME")
    return {"app_ms": ms, "jank_pct": num(r"Janky frames:\s*\d+ \(([\d.]+)%\)", g),
            "p90_ms": num(r"90th percentile:\s*(\d+)ms", g)}


def medir_uma(adb, apps):
    r = {"ram_livre_mb": None, "bateria_pct": None, "bateria_temp_c": None}
    mem = num(r"MemAvailable:\s+(\d+)", adb.shell("cat /proc/meminfo")["out"], int)
    r["ram_livre_mb"] = mem // 1024 if mem else None
    bat = adb.shell("dumpsys battery")["out"]
    r["bateria_pct"] = num(r"level:\s*(\d+)", bat, int)
    t = num(r"temperature:\s*(\d+)", bat, int)
    r["bateria_temp_c"] = t / 10 if t is not None else None
    por_app = {pkg: abrir_app(adb, pkg) for pkg in apps}
    for chave in ("app_ms", "jank_pct", "p90_ms"):
        vals = [v[chave] for v in por_app.values() if v[chave] is not None]
        r[chave] = round(statistics.mean(vals), 2) if vals else None
    r["apps"] = por_app
    return r


def agregar(execucoes):
    out = {}
    for k in list(MENOR_MELHOR) + ["bateria_pct", "bateria_temp_c"]:
        vals = [e[k] for e in execucoes if e.get(k) is not None]
        out[k] = round(statistics.median(vals), 2) if vals else None
    return out


def comparar(antes, depois):
    linhas, regressoes = {}, []
    for k, menor in MENOR_MELHOR.items():
        a, d = antes.get(k), depois.get(k)
        if a is None or d is None or a == 0:
            continue
        delta = (d - a) / a
        pior = delta > LIMITE_REGRESSAO if menor else delta < -LIMITE_REGRESSAO
        linhas[k] = {"antes": a, "depois": d, "delta_pct": round(delta * 100, 1)}
        if pior:
            regressoes.append(k)
    return {"metricas": linhas, "regressoes": regressoes, "aprovado": not regressoes}


def main():
    p = parser_base("Benchmark antes/depois")
    p.add_argument("--rotulo", default="baseline", help="nome do arquivo em benchmarks/ (ex.: baseline, depois)")
    p.add_argument("--execucoes", type=int, default=3)
    p.add_argument("--apps", nargs="*", default=["com.android.settings"])
    p.add_argument("--medir-boot", action="store_true", help="reinicia o aparelho para medir o boot")
    p.add_argument("--comparar", nargs=2, metavar=("ANTES", "DEPOIS"), help="rótulos já salvos em benchmarks/")
    a = p.parse_args()
    adb = Adb(a.serial, dry(a), a.timeout)
    bdir = adb.dir / "benchmarks"

    if a.comparar:
        try:
            ant, dep = [json.loads((bdir / f"{r}.json").read_text(encoding="utf-8"))["mediana"] for r in a.comparar]
        except (OSError, KeyError, ValueError) as e:
            emitir({"ok": False, "erro": f"benchmark ausente: {e}"}, 1)
        res = comparar(ant, dep)
        estado.registrar_resultado(a.serial, f"comparacao_{a.comparar[0]}_{a.comparar[1]}", res)
        emitir({"ok": True, **res})

    if a.dry_run:
        medir_uma(adb, a.apps)
        if a.medir_boot:
            adb.run(["reboot"])
        emitir({"ok": True, "dry_run": True, "execucoes": a.execucoes, "comandos": adb.comandos[:8],
                "total_comandos": len(adb.comandos)})

    execs = []
    for _ in range(a.execucoes):
        e = medir_uma(adb, a.apps)
        if a.medir_boot:
            e["boot_s"] = medir_boot(adb)
        execs.append(e)
    dados = {"rotulo": a.rotulo, "data": agora(), "apps": a.apps, "execucoes": execs, "mediana": agregar(execs)}
    bdir.mkdir(parents=True, exist_ok=True)
    (bdir / f"{a.rotulo}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    estado.registrar_resultado(a.serial, f"benchmark_{a.rotulo}", {"mediana": dados["mediana"]})
    emitir({"ok": True, "rotulo": a.rotulo, "mediana": dados["mediana"], "arquivo": str(Path("benchmarks") / f"{a.rotulo}.json")})


if __name__ == "__main__":
    main()
