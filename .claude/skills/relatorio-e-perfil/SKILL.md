---
name: relatorio-e-perfil
description: Gera dispositivos/<id>/relatorio.md a partir do estado e benchmarks e promove aprendizados para perfis/ (dispositivo e fabricante). Use na fase 5 ou ao encerrar em qualquer gate.
---

# relatorio-e-perfil (fase 5)

## Passos
1. Ler só: `dispositivos/<id>/estado.json`, `inventario.json`, `benchmarks/*.json`, `debloat-log.json`, `tweaks-anterior.json`. Não ler `logs/` salvo para investigar falha.
2. Preencher `templates/relatorio.md` em `dispositivos/<id>/relatorio.md`: aparelho, trilha seguida, gates e datas, mudanças aplicadas, tabela antes/depois (mediana e delta %), regressões, rollback testado, pendências.
3. Atualizar/criar `perfis/dispositivos/<codename>.yaml` a partir de `templates/perfil-dispositivo.yaml`:
   - `pacotes_seguros_remover`: só os que passaram no checklist funcional.
   - `pacotes_criticos_nao_tocar`: os que causaram problema.
   - `tweaks_validados`, `problemas_conhecidos`, `benchmarks_referencia`, `trilha_recomendada`, `suporte_comunidade.fontes` (URLs consultadas).
4. Promover ao `perfis/fabricantes/<marca>.yaml` apenas o que vale para a marca inteira (ex.: pacote de bloat comum).
5. Atualizar `docs/progresso.md` (handoff curto).

## Critério de sucesso
Relatório com antes/depois e rollback; perfil gravado; nenhum dado pessoal (serial só no nome da pasta, nunca IMEI, contas ou conteúdo de backup).

## Regra
`perfis/` é cache de conhecimento: nunca pesquisar de novo um modelo que já tem perfil. Não fazer push sem pedido do usuário.
