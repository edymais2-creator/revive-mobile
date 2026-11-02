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

## Etapa 2 - Scripts núcleo + hook: CONCLUÍDA (Sonnet)
- `scripts/`: `adb_util`, `estado`, `inventario`, `backup`, `benchmark`, `debloat`, `tweaks`. Todos rodam com `--dry-run` e serial fictício devolvendo JSON compacto; `--aplicar` de `debloat`/`tweaks` é recusado sem G1.
- `.claude/hooks/guard_destrutivo.py` + `.claude/settings.json`: exige G2 para fastboot flash/erase/format/flashing/oem e `dd` via adb; G1 para `pm uninstall --user 0`; bloqueia sempre `pm uninstall` sem `--user 0` e apagar a pasta de backups. Libera após o gate aprovado em `estado.json` do mesmo serial; sem `-s`, só infere o serial se houver um único aparelho registrado. Testado em 39 casos (sem gate, G2, G1), 0 falhas.
- Hook configurado com caminho absoluto do Python 3.12 em `command`/`args` e `onFailure: block` (sem depender do Git Bash). Se o projeto mudar de pasta ou de máquina, ajustar `.claude/settings.json`.
- Limite do hook: só vê o texto do comando; não enxerga comandos montados dentro de scripts. Texto citado dentro de um comando (ex.: mensagem de commit ou here-string) também o dispara: falso positivo aceito; para editar docs use as ferramentas de arquivo.
- Corrigido: `debloat.py` lia a lista com BOM (PowerShell 5.1 `Set-Content -Encoding utf8`); agora usa `utf-8-sig`.
- Projeto movido para `D:\Otimizacao_celulares`; remoto `origin` = https://github.com/edymais2-creator/revive-mobile (gh autenticado).
- Não validado com aparelho real: os scripts só rodaram em `--dry-run`; o parse da saída do adb será exercitado na Etapa 4.

## Próxima: Etapa 3 - Skills e agentes da trilha sem root (Sonnet / revisão Haiku)
Ler apenas: `CLAUDE.md`, `docs/metodologia.md`, `docs/gates.md` e a Etapa 3 do plano (`C:\Users\eduar_pfb8sj5\.claude\plans\iniciaremos-um-projeto-de-glittery-cloud.md`).
Entregar: skills `setup-host`, `diagnostico-adb`, `backup-verificado`, `debloat-seguro`, `tuning-android`, `protocolo-benchmark`, `relatorio-e-perfil` (≤ ~80 linhas cada, detalhes em `references/`); agentes `coletor`, `triagem`, `otimizador-android`, `qa-benchmark`, `documentador`; perfis iniciais conservadores Samsung, Xiaomi, Motorola.
