---
name: setup-host
description: Valida ou instala o ambiente do PC (git, python, adb, fastboot, scrcpy) e drivers USB. Use na fase 0 ou quando o adb não funciona por falta de ferramenta.
---

# setup-host (fase 0)

## Quando usar
Início do projeto, máquina nova, ou `adb`/`fastboot` "não reconhecido".

## Passos
1. Verificar (PowerShell 5.1: sem `&&`; o PATH pode não persistir entre chamadas):
   `git --version; python --version; adb version; fastboot --version; scrcpy --version`
2. Faltando algo, instalar por winget: `Git.Git`, `Python.Python.3.12`, `Google.PlatformTools`, `Genymobile.scrcpy`.
3. `python` apontando para o atalho da Microsoft Store = não instalado. Usar o de `%LOCALAPPDATA%\Programs\Python\Python312` e reiniciar o terminal.
4. Driver USB só quando o aparelho for definido (ver `references/drivers-usb.md`).
5. `scripts/adb_util.py` já localiza adb/fastboot no diretório do winget mesmo sem PATH.

## Critério de sucesso
Os cinco comandos do passo 1 imprimem versão. Registrar em `docs/progresso.md` só o que mudou.

## Rollback / riscos
Instalações via winget são reversíveis (`winget uninstall`). Nenhum risco para o aparelho.
