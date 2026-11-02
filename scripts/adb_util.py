"""Wrapper único de adb/fastboot: serial, timeout, log por aparelho, dry-run e saída bruta em arquivo."""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DISP = RAIZ / "dispositivos"


def achar(nome):
    """Localiza adb/fastboot no PATH ou no diretório do winget (Google.PlatformTools)."""
    p = shutil.which(nome)
    if p:
        return p
    base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    for c in glob.glob(os.path.join(base, "Google.PlatformTools*", "**", nome + ".exe"), recursive=True):
        return c
    return None


def pasta_dispositivo(serial, codename=None):
    """dispositivos/<codename>-<serial>; renomeia 'desconhecido-<serial>' quando o codename aparece."""
    if DISP.is_dir():
        for d in sorted(DISP.iterdir()):
            if d.is_dir() and d.name.endswith("-" + serial):
                if codename and d.name.startswith("desconhecido-"):
                    novo = DISP / f"{codename}-{serial}"
                    if not novo.exists():
                        try:
                            d.rename(novo)
                            return novo
                        except OSError:
                            pass
                return d
    return DISP / f"{codename or 'desconhecido'}-{serial}"


def agora():
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


def emitir(obj, codigo=0):
    """Saída final padrão: UM JSON compacto no stdout."""
    print(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
    sys.exit(codigo)


def parser_base(descricao, altera=False):
    p = argparse.ArgumentParser(description=descricao)
    p.add_argument("--serial", default=os.environ.get("ANDROID_SERIAL"), required=not os.environ.get("ANDROID_SERIAL"))
    p.add_argument("--dry-run", action="store_true", help="só registra os comandos, não executa")
    p.add_argument("--timeout", type=int, default=60)
    if altera:
        p.add_argument("--aplicar", action="store_true", help="executa de verdade (padrão: dry-run)")
    return p


def dry(args):
    return args.dry_run or (hasattr(args, "aplicar") and not args.aplicar)


class Adb:
    def __init__(self, serial, dry_run=False, timeout=60):
        self.serial, self.dry, self.timeout = serial, dry_run, timeout
        self.comandos = []  # comandos registrados/executados nesta sessão

    @property
    def dir(self):
        return pasta_dispositivo(self.serial)

    def _log(self, linha):
        try:
            (self.dir / "logs").mkdir(parents=True, exist_ok=True)
            with open(self.dir / "logs" / "adb.log", "a", encoding="utf-8") as f:
                f.write(f"{agora()} {linha}\n")
        except OSError:
            pass

    def run(self, args, ferramenta="adb", timeout=None):
        exe = achar(ferramenta) or ferramenta
        cmd = [exe, "-s", self.serial] + [str(a) for a in args]
        texto = f"{ferramenta} -s {self.serial} " + " ".join(str(a) for a in args)
        self.comandos.append(texto)
        if self.dry:
            self._log("[dry-run] " + texto)
            return {"rc": 0, "out": "", "err": "", "dry": True}
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=timeout or self.timeout)
            res = {"rc": r.returncode, "out": r.stdout, "err": r.stderr, "dry": False}
        except subprocess.TimeoutExpired:
            res = {"rc": 124, "out": "", "err": "timeout", "dry": False}
        except OSError as e:
            res = {"rc": 127, "out": "", "err": str(e), "dry": False}
        self._log(f"rc={res['rc']} {texto}")
        return res

    def shell(self, comando, timeout=None):
        return self.run(["shell", comando], timeout=timeout)

    def fastboot(self, args, timeout=None):
        return self.run(args, ferramenta="fastboot", timeout=timeout)

    def salvar_bruto(self, nome, texto):
        """Grava a saída bruta em logs/ e devolve só o caminho relativo à raiz do projeto."""
        if self.dry:
            return None
        pasta = self.dir / "logs"
        pasta.mkdir(parents=True, exist_ok=True)
        arq = pasta / f"{datetime.now():%Y%m%d-%H%M%S}-{nome}.txt"
        arq.write_text(texto or "", encoding="utf-8")
        return str(arq.relative_to(RAIZ))

    def bruto(self, nome, args, timeout=None):
        """Executa, salva a saída bruta e devolve (rc, texto, caminho)."""
        r = self.run(args, timeout=timeout)
        return r["rc"], r["out"], self.salvar_bruto(nome, r["out"] + r["err"])

    def prop(self, nome):
        return self.shell(f"getprop {nome}")["out"].strip()
