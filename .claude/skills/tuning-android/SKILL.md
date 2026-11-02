---
name: tuning-android
description: Aplica tweaks sem root reversíveis (escala de animações, compilação ART, limite de processos em cache) com scripts/tweaks.py. Use na fase 3, após G1.
---

# tuning-android (fase 3, exige G1)

## Pré-condições
G1 aprovado; baseline salvo (`protocolo-benchmark`).

## Tweaks disponíveis (`scripts/tweaks.py`)
| Opção | Efeito | Observação |
|---|---|---|
| `--animacao 0.5` | Escala de animações (0 desliga) | Ganho percebido, não de desempenho real |
| `--compilar [modo]` | `cmd package compile -m speed-profile -a` | Demora (até 15 min); ajuda após debloat/atualização |
| `--limite-bg N` | `max_cached_processes` | Valores baixos liberam RAM mas recarregam apps; testar 16-32 |
| `--reverter` | Restaura valores originais e `compile --reset` | Usa `tweaks-anterior.json` |

## Passos
1. Um tweak por vez. Simular: `python scripts/tweaks.py --serial <S> --animacao 0.5 --dry-run`
2. Aplicar: mesma linha com `--aplicar`. Valores originais ficam em `dispositivos/<id>/tweaks-anterior.json`.
3. Re-benchmark com rótulo próprio e comparar com o baseline (`protocolo-benchmark`).
4. Regressão > 5% em qualquer métrica: `python scripts/tweaks.py --serial <S> --reverter --aplicar`.

## Também sem root (manual, pedir ao usuário)
Desativar apps em segundo plano que ele não usa, limpar armazenamento (> 15% livre), atualizar WebView/Play Services, reduzir widgets e wallpaper animado, verificar saúde da bateria (CPU limitada por bateria degradada).

## Critério de sucesso
Cada tweak mantido tem ganho medido e nenhuma regressão; reversão testada.
