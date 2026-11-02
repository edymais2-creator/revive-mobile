# revive-mobile

## Missão
Prolongar a vida útil de celulares afetados por obsolescência programada: otimizar o Android de fábrica, avaliar sistemas alternativos (LineageOS, /e/OS, GSIs, postmarketOS) e, quando viável, ajustar kernel/drivers. A estrutura é agnóstica de dispositivo: o que se aprende vira perfil reutilizável em `perfis/`.

## Regras de segurança (inegociáveis)
- Sem root primeiro. Desbloqueio, flash de ROM e kernel só após gate aprovado pelo usuário (ver `docs/gates.md`).
- Nenhuma ação destrutiva (`fastboot flash|erase|oem unlock|flashing unlock`, `dd` via adb, `pm uninstall` sem `--user 0`) sem gate correspondente aprovado em `estado.json`.
- Backup verificado (com hash) antes de G2. Nunca apagar `backups/`.
- Todo script tem `--dry-run` e devolve resumo JSON compacto.
- Sem push/remotos sem pedido explícito. Não versionar dados pessoais nem `backups/`.

## Mapa de pastas
- `scripts/` Python (ADB/fastboot) · `templates/` modelos · `docs/` metodologia, gates, progresso
- `perfis/fabricantes/<marca>.yaml` · `perfis/dispositivos/<codename>.yaml` conhecimento cacheado
- `dispositivos/<codename>-<serial>/` `estado.json`, `benchmarks/`, `logs/`, `relatorio.md`, `backups/` (gitignored)
- `.claude/` agents, skills, hooks, settings

## Fases operacionais (por aparelho)
0 Setup do host → 1 Triagem → 2 Baseline → **G1** → 3 Otimização sem root + re-benchmark → **G2** → 4 SO alternativo + checklist funcional → **G3** → 5 Validação, relatório e atualização de `perfis/`.
Encerrar em qualquer gate é válido; a fase 3 já é uma entrega.

## Agentes → modelos
| Agente | Modelo |
|---|---|
| orquestrador | Sonnet |
| coletor | Haiku |
| triagem | Sonnet |
| otimizador-android | Sonnet |
| qa-benchmark | Haiku |
| avaliador-so | Opus |
| engenheiro-kernel | Opus |
| documentador | Haiku |

## Economia de tokens
1. Modelo certo por tarefa (Haiku mecânico, Sonnet padrão, Opus só alto risco).
2. Scripts fazem o trabalho pesado; saídas brutas vão para `logs/`, o agente recebe só JSON resumido.
3. Estado em arquivo (`estado.json`), nunca no histórico de conversa; subagente recebe caminho do estado + tarefa.
4. Skills curtas (≤ ~80 linhas) com detalhes em `references/`, lidos sob demanda.
5. Este arquivo ≤ ~100 linhas; o resto em `docs/`.
6. Pesquisa de comunidade é salva em `perfis/`; não repetir.
7. Sessões curtas por etapa; handoff em `docs/progresso.md`.

## Etapas de construção
Cada etapa roda no modelo previsto no plano (Etapa 1 Sonnet, 2 Sonnet, 3 Sonnet/Haiku, 4 Opus→Sonnet, 5 Opus, 6 Sonnet). Não antecipar etapas. Cada sessão começa lendo só `docs/progresso.md` e termina atualizando-o.
Plano completo: `C:\Users\eduar_pfb8sj5\.claude\plans\iniciaremos-um-projeto-de-glittery-cloud.md`.

## Ponteiros
- `docs/metodologia.md` fluxo e critérios · `docs/gates.md` G1/G2/G3 · `docs/progresso.md` estado atual
- `templates/` perfil-dispositivo.yaml, relatorio.md, matriz-decisao-so.md

## Ambiente
Windows 11, PowerShell 5.1 (sem `&&`/`||`). Ferramentas: git, python 3.12, adb, fastboot, scrcpy (via winget).
