Zoe 2.0 - PoC (Português)

O que você tem neste pacote
- Núcleo nativo (Python) para orquestrar comandos e aprendizado local
- Módulo de aprendizado local com SQLite (dados 100% locais)
- Extensão Chrome MV3 com UI futurista e Zoe Live (PT-BR)
- Popup com reconhecimento de voz PT-BR via Web Speech API
- Overlay de sugestões na página
- Instruções de instalação no final

Como gerar o ZIP
1) Abra o Terminal (Linux/macOS) ou prompt (Windows).
2) Execute o instalador unificado: python3 install_zoe_unificado.py (ou python install_zoe_unificado.py)
3) Ao finalizar, você encontrará Zoe-2.0.zip na pasta do usuário (ou onde o script informar).
4) Descompacte Zoe-2.0.zip e siga as instruções para instalar a extensão no Chrome e registrar o host nativo.

Observações
- Substitua SEU_ID_DA_EXTENSAO_AQUI pelo ID da extensão no Chrome (obtido em chrome://extensions).
- A parte de voz usa Web Speech API no popup (PT-BR). Caso seu navegador não suporte, aparecerá uma mensagem de fallback.
- Este é um PoC de demonstração com foco em privacidade e controle DOM básico.
