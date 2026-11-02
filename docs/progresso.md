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

## Etapa 4 - Orquestrador: ESCRITO; piloto PENDENTE
- `.claude/agents/orquestrador.md` (sonnet, tools: Read, Glob, Grep, PowerShell, Agent): ciclo de fases/gates em tabela, contrato de delegação (entrada = estado + tarefa; saída = JSON compacto), formato de pedido de gate. Decisão de desenho: o orquestrador **nunca aprova gates**; para e devolve o pedido, e a sessão principal registra com `estado.py aprovar-gate` só após a confirmação literal do usuário.
- Escrito sem Opus (a sessão rodou em Sonnet por pedido do usuário); se o ciclo se mostrar frágil no piloto, revisar com Opus.
- Ainda não exercitado com aparelho.

## Etapa 4 (preparação) - melhoria no debloat: CONCLUÍDA (Sonnet)
- `debloat.py` agora lê `criticos_nao_tocar_prefixos` de `perfis/fabricantes/<marca>.yaml` e `pacotes_criticos_nao_tocar` de `perfis/dispositivos/<codename>.yaml` (marca/codename vêm de `inventario.json` ou `--marca`). Testado só por importação (7 casos, sem aparelho).
- Commit `95ec41a`, enviado ao GitHub.

## BLOQUEIO ATIVO (2026-11-02): piloto Samsung A71 preso em FRP
- Piloto definido: **Samsung Galaxy A71** (provável codename `a71`, modelo SM-A715F; confirmar pelo inventário quando conectar).
- O usuário não conseguiu ativar Depuração USB porque o aparelho está em tela de verificação FRP (Factory Reset Protection) após reset — pediu "remoção FRP tool", recusado: isso é bypass de proteção de conta, que só ajudo se for comprovadamente o aparelho do próprio usuário E a situação for uma destas (perguntar qual antes de prosseguir):
  1. Ele lembra a conta Google/Samsung que estava no aparelho → login normal na tela de verificação, não é bypass.
  2. Esqueceu a senha mas tem acesso à conta por outro meio → recuperar em accounts.google.com antes de qualquer reset.
  3. Aparelho de terceiro (compra, herança) sem a conta do proprietário anterior → contatar esse proprietário para remover a conta dele (Configurações > Contas, ou remotamente por "Find My Mobile"/"Find My Device") ou fazer login quando solicitado.
  4. Aparelho de empresa/escola com MDM → contatar o administrador de TI.
- Nenhuma instrução de hard reset foi executada ainda (orientação dada, aguardando confirmação do usuário sobre qual caso acima se aplica).
- **Não prosseguir com adb/scripts no A71 enquanto o FRP não for resolvido pelo caminho legítimo.** Sem depuração USB ativa, nenhum script deste projeto funciona nele.

## Próxima sessão: Etapa 4 (execução) - piloto sem root (Sonnet)
1. Primeiro, resolver o bloqueio de FRP acima com o usuário (qual dos 4 casos se aplica) antes de tocar no aparelho.
2. Depois do reset (se necessário) e login bem-sucedido: ativar Opções do desenvolvedor + Depuração USB, instalar driver Samsung, conectar e confirmar com `adb devices`.
3. Backup recomendado antes de debloat (apps/mídia via `backup.py`; contas e WhatsApp ficam fora do script, orientar backup nativo).
4. Ler apenas: `CLAUDE.md`, este arquivo e `docs/gates.md`. Rodar pelo `orquestrador`: triagem, baseline, pedido de G1 (parar e aguardar confirmação literal do usuário antes de `estado.py aprovar-gate`), otimização em lotes, re-benchmark, relatório.
5. Lembrar: desbloqueio de bootloader (G2) trippa o Knox permanentemente; só com decisão consciente do usuário.
Pronto quando: `relatorio.md` com comparação antes/depois e rollback do debloat testado.

## Resíduo pendente (qualquer sessão)
- Apagar manualmente `dispositivos/fakecode-FAKE123/` (dados de teste, fora do git; `Remove-Item` direto falhou nesta máquina).
