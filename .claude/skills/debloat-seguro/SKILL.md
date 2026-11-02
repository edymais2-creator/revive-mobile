---
name: debloat-seguro
description: Remove/desativa apps pré-instalados sem root, por usuário e com rollback, usando scripts/debloat.py e a lista do perfil. Use na fase 3, só após G1 aprovado.
---

# debloat-seguro (fase 3, exige G1)

## Pré-condições
Baseline com >= 3 execuções, inventário, backup recomendado, **G1 aprovado** (`estado.py show`).

## Passos
1. Montar a lista candidata: `perfis/dispositivos/<codename>.yaml` (`pacotes_seguros_remover`); se não houver, `perfis/fabricantes/<marca>.yaml` (`candidatos_debloat`, a validar).
   Cruzar com `pm list packages -3` / `pm list packages -s` do aparelho. Nunca incluir os de `pacotes_criticos_nao_tocar`.
2. Gravar a lista em `dispositivos/<id>/debloat-lista.txt` (um pacote por linha, `#` comenta). Salvar em UTF-8 sem BOM.
3. Simular: `python scripts/debloat.py --serial <S> --lista <arq> --dry-run`
   O script já pula pacotes críticos (`pulados_criticos`).
4. Aplicar **em lotes pequenos** (5-10), preferindo `--acao desativar` (padrão, `pm disable-user --user 0`). `--acao remover` só para o que o perfil marca como seguro.
   `python scripts/debloat.py --serial <S> --lista <arq> --aplicar`
5. Após cada lote: reiniciar, testar chamada, SMS, dados, biometria, câmera; rodar `protocolo-benchmark`. Regressão > 5% ou função quebrada: `--rollback`.
6. Rollback: `python scripts/debloat.py --serial <S> --rollback --aplicar` (usa `debloat-log.json`; tenta `pm enable`, depois `cmd package install-existing --user 0`). Reset de fábrica restaura tudo.

## Critério de sucesso
Falhas = 0, checklist funcional ok, benchmark sem regressão, rollback testado em pelo menos 1 pacote.

## Riscos
Pacote crítico removido pode quebrar telefone/SMS/biometria; apps de operadora podem parar. O hook bloqueia `pm uninstall` sem `--user 0` e sem G1.
