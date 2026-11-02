---
name: protocolo-benchmark
description: Mede baseline e re-benchmark reprodutíveis com scripts/benchmark.py (abertura de apps, jank, RAM, boot) e compara antes/depois. Use na fase 2 e após cada otimização.
---

# protocolo-benchmark (fases 2 e 3)

## Condições controladas (anotar no relatório)
Bateria >= 50% e carregador na mesma condição, temperatura da bateria estável (< 38 °C), brilho fixo, Wi-Fi igual, sem instalação/atualização em curso, tela desbloqueada, sem apps abertos. Mesmo conjunto de `--apps` em todas as medições.

## Passos
1. Baseline: `python scripts/benchmark.py --serial <S> --rotulo baseline --execucoes 3 --apps com.android.settings <outros>`
   Mínimo 3 execuções; vale a **mediana**. Acrescentar `--medir-boot` só quando o usuário aceitar o reinício.
2. Simular antes: `--dry-run`.
3. Após cada mudança: `--rotulo depois-<mudança>` com os mesmos parâmetros.
4. Comparar: `python scripts/benchmark.py --serial <S> --comparar baseline depois-<mudança>`
   Retorna `metricas`, `regressoes`, `aprovado`. Menor é melhor para `app_ms`, `jank_pct`, `p90_ms`, `boot_s`; maior para `ram_livre_mb`.
5. Regressão > 5% em qualquer métrica: reverter a mudança (`debloat-seguro` / `tuning-android`).

## Resultados
`dispositivos/<id>/benchmarks/<rotulo>.json` (execuções + mediana) e `estado.json` (resumo). Saídas brutas ficam em `logs/`.

## Limitações
Medição por adb é ruidosa; se a variação entre execuções passar de ~10%, repetir sob condições mais controladas antes de concluir. Usar apps reais do usuário (além de Configurações) para o resultado refletir o uso.
