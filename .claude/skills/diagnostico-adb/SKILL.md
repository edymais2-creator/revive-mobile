---
name: diagnostico-adb
description: Diagnostica conexão ADB (offline, unauthorized, sem serial) e faz a triagem/inventário do aparelho com scripts/inventario.py. Use na fase 1 ou quando o aparelho não responde.
---

# diagnostico-adb (fase 1: triagem)

## Quando usar
Primeiro contato com um aparelho, ou scripts retornando "sem resposta do aparelho".

## Passos
1. `adb devices -l`
   - `unauthorized`: desbloquear a tela e aceitar a depuração USB (marcar "sempre permitir").
   - `offline` ou vazio: trocar cabo/porta, `adb kill-server; adb start-server`, revisar driver (`setup-host`).
   - Mais de um aparelho: sempre usar `--serial`.
2. Inventário: `python scripts/inventario.py --serial <S>` (primeiro com `--dry-run` se quiser ver os comandos).
   Saída: JSON com codename, fabricante, Android, patch, SoC, RAM, armazenamento, bateria, Treble, A/B, estado do bootloader. Brutos em `dispositivos/<codename>-<serial>/logs/`.
3. `python scripts/estado.py show --serial <S>` confirma o `estado.json` (criado pelo inventário).
4. Procurar `perfis/dispositivos/<codename>.yaml`; se existir, usar o cache e NÃO pesquisar de novo. Senão, `perfis/fabricantes/<marca>.yaml` como ponto de partida e delegar pesquisa de comunidade ao agente `triagem`.
5. Mais detalhes de erros: `references/problemas-comuns.md`.

## Critério de sucesso
`inventario.json` existe, `estado.json` com codename correto, trilha recomendada registrada (sem-root | rom-oficial | gsi | postmarketos | kernel).

## Riscos
Somente leitura. Nenhum gate necessário.
