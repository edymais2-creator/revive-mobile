# Problemas comuns de ADB

- **`adb` não reconhecido**: ver `setup-host`; `scripts/adb_util.py` acha o binário do winget sozinho.
- **`unauthorized`**: revogar autorizações em Opções do desenvolvedor, reconectar e aceitar o prompt.
- **`offline`**: reiniciar o servidor adb; trocar cabo (cabos só de carga são comuns); testar porta USB 2.0.
- **`more than one device/emulator`**: informar `--serial` ou `ANDROID_SERIAL`.
- **Aparelho some ao rodar benchmark**: economia de bateria ou "USB só carregar"; escolher "Transferência de arquivos".
- **Xiaomi**: ativar também "Depuração USB (configurações de segurança)" para `input` e instalação via USB.
- **Samsung**: Knox pode bloquear alguns comandos `pm`; registrar no perfil.
- **Timeout em dumpsys**: aumentar `--timeout`; aparelho pode estar em suspensão profunda.
- **`adb` por Wi-Fi**: só com autorização prévia por USB; evitar para benchmark (instável).
