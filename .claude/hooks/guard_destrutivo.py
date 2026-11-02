"""Hook PreToolUse (Bash/PowerShell): bloqueia ações destrutivas sem o gate aprovado em estado.json.

Entrada: JSON do Claude Code no stdin. Saída: exit 0 libera; exit 2 bloqueia (motivo no stderr).
Limite conhecido: inspeciona o texto do comando; não enxerga comandos montados dentro de scripts.
"""
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(os.environ.get("REVIVE_RAIZ") or Path(__file__).resolve().parents[2])

# início de um comando simples: começo da linha ou após ; | & ( e aspas/espaços
INI = r"(?:^|[;&|(\n`]|&&|\|\|)\s*(?:&\s*)?[\"']?(?:[\w:.\\/~-]*[\\/])?"
FASTBOOT = re.compile(INI + r"fastboot(?:\.exe)?[\"']?\s+(?P<args>[^;&|\n]*)", re.I)
ADB = re.compile(INI + r"adb(?:\.exe)?[\"']?\s+(?P<args>[^;&|\n]*)", re.I)
SERIAL = re.compile(r"(?:^|\s)-s\s+(\S+)")

FB_G2 = re.compile(r"(?:^|\s)(?:flash|flashall|flashing|erase|format|update|wipe-super|set_active|--set-active"
                   r"|create-logical-partition|delete-logical-partition|resize-logical-partition|snapshot-update"
                   r"|oem\s+(?:un)?lock|oem\s+\w*(?:unlock|lock))\b", re.I)
ADB_DD = re.compile(r"\bshell\b.*\b(?:dd\b.*\bof=|mkfs|blkdiscard|flash_image)", re.I)
PM_UNINSTALL = re.compile(r"\bpm\s+uninstall\b", re.I)
USER0 = re.compile(r"--user\s+0\b")
RM_BACKUPS = re.compile(r"(?:\brm\b|\bRemove-Item\b|\bdel\b|\brmdir\b|\bri\b)[^;&|\n]*\bbackups\b", re.I)


def estados():
    d = RAIZ / "dispositivos"
    out = {}
    if d.is_dir():
        for e in d.glob("*/estado.json"):
            try:
                est = json.loads(e.read_text(encoding="utf-8"))
                out[str(est.get("serial") or e.parent.name.rsplit("-", 1)[-1])] = est
            except (OSError, ValueError):
                pass
    return out


def gate_ok(gate, serial):
    """True se o gate está aprovado para o serial; sem serial, só se houver exatamente um aparelho registrado."""
    todos = estados()
    serial = serial or os.environ.get("ANDROID_SERIAL")
    if serial is None:
        if len(todos) != 1:
            return False
        serial = next(iter(todos))
    est = todos.get(serial)
    try:
        return bool(est and est["gates"][gate].get("aprovado") is True)
    except (KeyError, TypeError, AttributeError):
        return False


def avaliar(cmd):
    """Devolve lista de (gate, motivo) exigidos pelo comando; gate None = bloqueio incondicional."""
    exigidos = []
    if RM_BACKUPS.search(cmd):
        exigidos.append((None, "apagar backups/ é proibido"))
    for m in FASTBOOT.finditer(cmd):
        if FB_G2.search(m.group("args")):
            exigidos.append(("G2", "fastboot " + m.group("args").strip()[:60]))
    for m in ADB.finditer(cmd):
        args = m.group("args")
        if ADB_DD.search(args):
            exigidos.append(("G2", "escrita em bloco via adb: " + args.strip()[:60]))
        elif PM_UNINSTALL.search(args):
            if USER0.search(args):
                exigidos.append(("G1", "pm uninstall --user 0"))
            else:
                exigidos.append((None, "pm uninstall sem --user 0 remove o pacote de todos os usuários"))
    return exigidos


def serial_do(cmd):
    for rx in (FASTBOOT, ADB):
        for m in rx.finditer(cmd):
            s = SERIAL.search(m.group("args"))
            if s:
                return s.group(1)
    return None


def main():
    try:
        dados = json.load(sys.stdin)
        cmd = (dados.get("tool_input") or {}).get("command") or ""
    except (ValueError, AttributeError):
        sys.exit(0)
    exigidos = avaliar(cmd)
    if not exigidos:
        sys.exit(0)
    serial = serial_do(cmd)
    bloqueios = []
    for gate, motivo in exigidos:
        if gate is None:
            bloqueios.append(f"{motivo} (sem exceção)")
        elif not gate_ok(gate, serial):
            bloqueios.append(f"{motivo} exige {gate} aprovado em estado.json (serial={serial or 'não informado'})")
    if bloqueios:
        print("BLOQUEADO por guard_destrutivo: " + "; ".join(bloqueios) +
              ". Apresente riscos ao usuário e registre a aprovação com scripts/estado.py aprovar-gate (docs/gates.md).",
              file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
