# Drivers USB por fabricante (instalar só quando o aparelho for definido)

| Fabricante | Driver | Observação |
|---|---|---|
| Samsung | Samsung USB Driver for Mobile Phones | Necessário também para modo Download (Odin) |
| Xiaomi | Mi USB Driver / Mi Flash Tool | Modo fastboot costuma funcionar com o driver Google |
| Motorola | Motorola Device Manager (Lenovo) | Pacote inclui ADB/fastboot driver |
| Pixel/AOSP e outros | Google USB Driver (via SDK Manager) | Padrão para adb/fastboot |
| MediaTek | MTK VCOM/Preloader | Só para modo de recuperação/flash baixo nível |

Validar: aparelho aparece como `device` em `adb devices` (não `unauthorized`/`offline`) e, em modo bootloader, em `fastboot devices`.
Baixar sempre do site do fabricante; conferir hash quando divulgado.
