# Gates de aprovação

Apenas o usuário aprova. O agente apresenta riscos e evidências, pede confirmação explícita e só então registra a aprovação. Sem aprovação registrada, o hook de segurança (Etapa 2) bloqueia as ações do gate.

Registro em `dispositivos/<codename>-<serial>/estado.json`:
```json
"gates": {
  "G1": {"aprovado": true, "data": "AAAA-MM-DDTHH:MM", "usuario_confirmou": "texto literal da confirmação", "evidencias": ["benchmarks/baseline.json"]}
}
```
Gate ausente ou `aprovado: false` = bloqueado.

## G1 - Debloat e tweaks sem root
- **Pré-condições**: triagem e baseline concluídos; depuração USB autorizada; lista de pacotes candidatos vinda do perfil.
- **Riscos a explicitar**: pacote crítico removido pode quebrar funções (telefone, SMS, biometria); reversível via `install-existing` ou reset de fábrica; alguns apps de operadora deixam de funcionar.
- **Evidências**: `baseline.json` (>= 3 execuções), inventário, lista de pacotes com justificativa, plano de rollback.
- **Registro**: `gates.G1` com data, confirmação e caminhos das evidências.

## G2 - Desbloqueio de bootloader
- **Pré-condições**: G1 encerrado (otimização sem root insuficiente ou SO alternativo desejado); matriz de decisão preenchida; método oficial de desbloqueio conhecido; carga da bateria >= 60%.
- **Riscos a explicitar**: apaga todos os dados; perda de garantia e, em Samsung, trip permanente do Knox; apps bancários/DRM/Widevine L1 podem parar; risco de brick; patches OTA oficiais deixam de valer.
- **Evidências**: backup verificado com hash (SHA-256) em `backups/` e restauração testada por amostragem; cópia das partições críticas quando possível (EFS/persist/modem); firmware stock original baixado e com hash; fonte do procedimento.
- **Registro**: `gates.G2` + `hash_backup` e caminho do firmware stock.

## G3 - Kernel e drivers
- **Pré-condições**: G2 aprovado e SO alternativo funcional ou stock com bootloader desbloqueado; fonte do kernel disponível (GPL) com versão compatível; ganho esperado quantificado.
- **Riscos a explicitar**: bootloop/brick; perda de funções (câmera, modem, sensores) por driver incompatível; instabilidade e superaquecimento; manutenção contínua a cada atualização.
- **Evidências**: repositório e commit do kernel, defconfig, plano de build, imagem de boot original salva e testada para restauração, métrica alvo versus baseline.
- **Registro**: `gates.G3` + commit do kernel e caminho da imagem de recuperação.
