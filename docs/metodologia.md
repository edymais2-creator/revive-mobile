# Metodologia

## Princípio
Intervenção escalonada: do menos ao mais invasivo, com gates de aprovação do usuário. Cada fase gera evidência em arquivo e atualiza `estado.json`.

## Fases por aparelho
0. **Setup do host**: git, python, adb, fastboot, scrcpy; driver USB do fabricante quando o piloto for definido.
1. **Triagem**: inventário (modelo, SoC, Android, patch, Treble, A/B, bootloader); consulta ao cache em `perfis/`; pesquisa de comunidade só se faltar perfil; recomenda trilha.
2. **Baseline**: benchmarks reprodutíveis (boot, abertura de apps, RAM, frames, I/O), mesmas condições (bateria, temperatura, apps em segundo plano). Mínimo de 3 execuções, usar mediana.
3. **G1**, depois **Otimização sem root**: debloat por perfil (`pm uninstall --user 0`, reversível com `cmd package install-existing`), animações, compilação ART, restrições de segundo plano. Re-benchmark; regressão > 5% em qualquer métrica reverte a mudança.
4. **G2**, depois **SO alternativo**: matriz de decisão (`templates/matriz-decisao-so.md`), flash, checklist funcional completo.
5. **G3**, depois **Kernel/drivers**: apenas com fonte disponível (GPL) e ganho esperado documentado.
6. **Validação e relatório**: `relatorio.md` e promoção de aprendizados para `perfis/`.

## Estado e logs
- `dispositivos/<codename>-<serial>/estado.json`: fase atual, gates, hashes de backup, últimas métricas.
- Saídas brutas (`dumpsys`, `logcat`) em `logs/`; scripts devolvem apenas JSON resumido.

## Critérios gerais
- Toda mudança tem rollback documentado e testado antes de avançar.
- Sem backup verificado, sem G2.
- Encerrar em qualquer gate é um resultado válido.
- Conhecimento novo vira perfil (`perfis/fabricantes`, `perfis/dispositivos`); nunca pesquisar duas vezes o mesmo modelo.
