"""Debloat reversível (pm disable-user / uninstall --user 0). Dry-run por padrão; --aplicar exige G1."""
import json

import estado
from adb_util import Adb, agora, dry, emitir, parser_base

# Pacotes (ou prefixos) nunca tocados, mesmo se estiverem na lista.
CRITICOS = ("android", "com.android.phone", "com.android.systemui", "com.android.settings",
            "com.android.providers.", "com.android.bluetooth", "com.android.nfc", "com.android.server.",
            "com.android.packageinstaller", "com.google.android.packageinstaller",
            "com.android.permissioncontroller", "com.google.android.permissioncontroller",
            "com.android.telecom", "com.android.stk", "com.android.inputmethod", "com.android.shell",
            "com.android.vending", "com.google.android.gms", "com.google.android.gsf",
            "com.google.android.webview", "com.android.webview", "com.android.emergency",
            "com.android.cellbroadcast", "com.android.carrierconfig", "com.android.ims")


def critico(pkg):
    return any(pkg == c or (c.endswith(".") and pkg.startswith(c)) for c in CRITICOS)


def ler_lista(caminho):
    texto = open(caminho, encoding="utf-8-sig").read()
    try:
        dados = json.loads(texto)
        return [str(x) for x in dados]
    except ValueError:
        return [l.split("#")[0].strip() for l in texto.splitlines() if l.split("#")[0].strip()]


def main():
    p = parser_base("Debloat com rollback", altera=True)
    p.add_argument("--lista", help="arquivo .txt (um pacote por linha, # comenta) ou .json")
    p.add_argument("--acao", choices=["desativar", "remover"], default="desativar")
    p.add_argument("--rollback", action="store_true", help="reverte o que está em debloat-log.json (ou --lista)")
    a = p.parse_args()
    adb = Adb(a.serial, dry(a), a.timeout)
    log_arq = adb.dir / "debloat-log.json"
    historico = json.loads(log_arq.read_text(encoding="utf-8")) if log_arq.is_file() else []

    if a.rollback:
        alvos = ler_lista(a.lista) if a.lista else [h["pacote"] for h in historico if not h.get("revertido")]
        acao = "rollback"
    else:
        if not a.lista:
            emitir({"ok": False, "erro": "informe --lista"}, 1)
        alvos, acao = ler_lista(a.lista), a.acao
    pulados = [x for x in alvos if critico(x)] if acao != "rollback" else []
    alvos = [x for x in alvos if x not in pulados]

    if not dry(a) and not estado.gate_aprovado(a.serial, "G1"):
        emitir({"ok": False, "erro": "G1 não aprovado em estado.json; --aplicar bloqueado"}, 1)

    ok, falhas = [], []
    for pkg in alvos:
        if acao == "desativar":
            r = adb.shell(f"pm disable-user --user 0 {pkg}")
        elif acao == "remover":
            r = adb.shell(f"pm uninstall --user 0 {pkg}")
        else:
            r1 = adb.shell(f"pm enable {pkg}")
            r = r1 if r1["rc"] == 0 and "enabled" in r1["out"] else adb.shell(f"cmd package install-existing --user 0 {pkg}")
        sucesso = r["dry"] or (r["rc"] == 0 and any(s in r["out"] for s in ("Success", "new state", "enabled", "installed")))
        (ok if sucesso else falhas).append(pkg)
        if not dry(a):
            if acao == "rollback":
                for h in historico:
                    if h["pacote"] == pkg and sucesso:
                        h["revertido"] = True
            elif sucesso:
                historico.append({"data": agora(), "pacote": pkg, "acao": acao})
    if not dry(a):
        adb.dir.mkdir(parents=True, exist_ok=True)
        log_arq.write_text(json.dumps(historico, ensure_ascii=False, indent=1), encoding="utf-8")
        estado.registrar_resultado(a.serial, "debloat", {"acao": acao, "ok": len(ok), "falhas": len(falhas)})
    emitir({"ok": not falhas, "dry_run": dry(a), "acao": acao, "alvos": len(alvos), "sucesso": len(ok),
            "falhas": falhas[:20], "pulados_criticos": pulados, "comandos": adb.comandos[:6]})


if __name__ == "__main__":
    main()
