---
name: backup-verificado
description: Faz backup não destrutivo (lista de apps, APKs, mídia) com manifesto SHA-256 e verificação. Obrigatório antes de G2. Use quando o usuário quiser proteger dados ou antes de qualquer desbloqueio.
---

# backup-verificado

## Quando usar
Antes do G1 (recomendado) e **obrigatoriamente antes do G2** (desbloqueio apaga tudo).

## Passos
1. Espaço livre no PC >= tamanho de `/sdcard` + folga (checar `data_livre_mb` e tamanho da mídia).
2. Pré-visualizar: `python scripts/backup.py --serial <S> --dry-run`
3. Executar: `python scripts/backup.py --serial <S>` (opções: `--sem-midia`, `--sem-apps`, `--max-apps`, `--destino`).
   Destino padrão: `dispositivos/<codename>-<serial>/backups/<data>/` com `apps/`, `midia/`, `manifesto.json`.
4. Verificar: `python scripts/backup.py --serial <S> --verificar <pasta>` deve retornar `ok:true`, sem faltando/corrompidos.
5. O hash do manifesto fica em `estado.json` (`backups[]`); ele é a evidência exigida pelo G2.
6. Dados que o script NÃO cobre: contas/dados internos de apps, SMS, contatos, WhatsApp, 2FA. Orientar o usuário a usar backup do próprio app/Google e **migrar autenticadores antes**.
7. Restauração testada por amostragem: abrir 3 arquivos de mídia e instalar 1 APK de teste em outro aparelho, se possível.

## Critério de sucesso
`verificado: true`, itens > 0, hash registrado, amostra de restauração conferida.

## Regras
Nunca apagar nem sobrescrever `backups/` (o hook bloqueia). Pasta está no `.gitignore`: nunca versionar dados pessoais.
Para G2, partições críticas (EFS/persist/modem) exigem root ou ferramenta do fabricante: registrar como pendência se indisponível.
