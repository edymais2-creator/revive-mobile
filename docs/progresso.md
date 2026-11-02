# Progresso (handoff entre sessões)

## Etapa 1 - Fundação: CONCLUÍDA (Sonnet)
- Instalados e validados via winget: Git 2.56.0, Python 3.12.10, platform-tools (adb/fastboot 37.0.1), scrcpy 5.0.1.
- Python 3.12 não estava no PATH (só o atalho da Microsoft Store); adicionado ao PATH do usuário (`...\Programs\Python\Python312` e `\Scripts`). Terminais abertos antes disso precisam ser reiniciados.
- Criados: `.gitignore`, `CLAUDE.md`, `templates/`, `docs/metodologia.md`, `docs/gates.md`, esta nota, pastas vazias com `.gitkeep`.
- Commit inicial feito.

### Pendências para o usuário
- Git: `user.name`/`user.email` foram definidos só localmente no repo como "revive-mobile" / "revive-mobile@localhost". Trocar pelos dados reais (`git config user.name ...`).
- Drivers USB do fabricante: instalar quando o piloto for definido.
- Nenhum remoto configurado.

## Próxima: Etapa 2 - Scripts núcleo + hook (Sonnet)
Ler apenas: `CLAUDE.md`, `docs/gates.md`, `docs/metodologia.md`, `templates/perfil-dispositivo.yaml` e a Etapa 2 do plano (`C:\Users\eduar_pfb8sj5\.claude\plans\iniciaremos-um-projeto-de-glittery-cloud.md`).
Entregar: `scripts/` (`adb_util.py`, `estado.py`, `inventario.py`, `backup.py`, `benchmark.py`, `debloat.py`, `tweaks.py`), `.claude/hooks/guard_destrutivo.py` e `.claude/settings.json`.
Pronto quando: todos rodam com `--dry-run` e serial fictício retornando JSON resumido; hook bloqueia `fastboot flash` simulado e libera após gate marcado em `estado.json` de teste. Ao final, atualizar este arquivo.
