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

## Etapa 3 - Skills e agentes da trilha sem root: CONCLUÍDA (Sonnet)
- Skills em `.claude/skills/` (todas ≤ 30 linhas): `setup-host`, `diagnostico-adb`, `backup-verificado`, `debloat-seguro`, `tuning-android`, `protocolo-benchmark`, `relatorio-e-perfil`; `references/` em `setup-host` (drivers USB) e `diagnostico-adb` (problemas comuns).
- Agentes em `.claude/agents/`: `coletor` (haiku), `triagem` (sonnet), `otimizador-android` (sonnet), `qa-benchmark` (haiku), `documentador` (haiku).
- Perfis de fabricante `perfis/fabricantes/{samsung,xiaomi,motorola}.yaml`: listas de candidatos a debloat e pacotes críticos, **não validados em aparelho real** (`status: inicial-nao-validado`).
- Ajuste: `LIMITE_REGRESSAO` em `scripts/benchmark.py` passou de 10% para 5% (alinhado a `docs/metodologia.md`).
- Lacuna conhecida: `debloat.py` só barra os críticos do Android (lista interna); os `criticos_nao_tocar_prefixos` dos perfis de fabricante ainda não são lidos pelo script, a skill instrui a respeitá-los. Candidato a melhoria na Etapa 4.
- Pendente: resíduo de teste `dispositivos/fakecode-FAKE123/` (dados fictícios, fora do git); apagar manualmente (o PowerShell bloqueia `Remove-Item` nesta pasta).
- Não testado: agentes e skills ainda não foram exercitados com aparelho real.

## Próxima: Etapa 4 - Orquestrador + piloto sem root (Opus para o desenho; Sonnet na execução)
Ler apenas: `CLAUDE.md`, `docs/metodologia.md`, `docs/gates.md` e a Etapa 4 do plano (`C:\Users\eduar_pfb8sj5\.claude\plans\iniciaremos-um-projeto-de-glittery-cloud.md`).
Entregar: `.claude/agents/orquestrador.md` (ciclo de fases/gates e contrato de delegação: entrada = caminho do estado + tarefa; saída = JSON resumido; para em cada gate e pede aprovação ao usuário).
**Pré-requisito para a execução:** o usuário escolher o aparelho piloto e conectá-lo (depuração USB ativa, driver do fabricante instalado). Depois: triagem, baseline, G1, otimização, re-benchmark e relatório. Pronto quando houver `relatorio.md` com antes/depois e rollback do debloat testado.
