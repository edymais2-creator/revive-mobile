"""Tweaks sem root: animações, compilação ART, limite de processos em cache. Reversível; --aplicar exige G1."""
import json

import estado
from adb_util import Adb, dry, emitir, parser_base

ANIM = ("window_animation_scale", "transition_animation_scale", "animator_duration_scale")
BG = "activity_manager_constants"


def main():
    p = parser_base("Tweaks reversíveis", altera=True)
    p.add_argument("--animacao", type=float, help="escala das animações (ex.: 0.5; 0 desliga)")
    p.add_argument("--compilar", nargs="?", const="speed-profile", help="cmd package compile -m <modo> -a")
    p.add_argument("--limite-bg", type=int, help="max_cached_processes")
    p.add_argument("--reverter", action="store_true", help="restaura valores salvos em tweaks-anterior.json")
    a = p.parse_args()
    adb = Adb(a.serial, dry(a), a.timeout)
    arq = adb.dir / "tweaks-anterior.json"
    if not dry(a) and not estado.gate_aprovado(a.serial, "G1"):
        emitir({"ok": False, "erro": "G1 não aprovado em estado.json; --aplicar bloqueado"}, 1)

    feitos = []
    if a.reverter:
        ant = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
        if not ant and not dry(a):
            emitir({"ok": False, "erro": "sem tweaks-anterior.json para reverter"}, 1)
        for chave, valor in (ant or {k: "null" for k in (*ANIM, BG)}).items():
            if valor in ("null", "", None):
                adb.shell(f"settings delete global {chave}")
            else:
                adb.shell(f"settings put global {chave} {valor}")
            feitos.append(f"restaurar {chave}")
        adb.shell("cmd package compile --reset -a", timeout=900)
        feitos.append("compile --reset")
    else:
        antes = {}
        def guardar(chave):
            antes[chave] = adb.shell(f"settings get global {chave}")["out"].strip() or "null"
        if a.animacao is not None:
            for k in ANIM:
                guardar(k)
                adb.shell(f"settings put global {k} {a.animacao}")
            feitos.append(f"animacoes={a.animacao}")
        if a.limite_bg is not None:
            guardar(BG)
            adb.shell(f"settings put global {BG} max_cached_processes={a.limite_bg}")
            feitos.append(f"max_cached_processes={a.limite_bg}")
        if a.compilar:
            adb.shell(f"cmd package compile -m {a.compilar} -a", timeout=900)
            feitos.append(f"compile {a.compilar}")
        if not feitos:
            emitir({"ok": False, "erro": "nada a fazer: use --animacao, --limite-bg, --compilar ou --reverter"}, 1)
        if not dry(a) and antes:
            arq.parent.mkdir(parents=True, exist_ok=True)
            atual = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
            for k, v in antes.items():
                atual.setdefault(k, v)  # preserva o valor original
            arq.write_text(json.dumps(atual, indent=1), encoding="utf-8")
    if not dry(a):
        estado.registrar_resultado(a.serial, "tweaks", {"acoes": feitos})
    emitir({"ok": True, "dry_run": dry(a), "acoes": feitos, "comandos": adb.comandos[:8],
            "total_comandos": len(adb.comandos)})


if __name__ == "__main__":
    main()
