# -*- coding: utf-8 -*-
import sys
import json
import struct
import threading
import time
import os
import base64
import io
from groq import Groq
from learning_module import LearningModule
import mss
from PIL import Image

# --- Globals ---
learning_engine = None
groq_client = None

# --- AI Configuration ---
SYSTEM_PROMPT = """
You are an expert command interpreter named Zoe. Your task is to convert a user's natural language request into a specific JSON format.
The JSON output should be a single object with no extra text or explanations.

The only valid actions are 'navigate', 'scroll', 'click', and 'analyze_screen'.

1.  **Navigation**: Convert requests like "abrir", "navegar para", "ir para" into a navigation command.
    - User: "abrir o site da cnn"
    - Assistant: {"action": "navigate", "url": "https://www.cnn.com"}

2.  **Scrolling**: Convert scrolling requests.
    - User: "rola para baixo"
    - Assistant: {"action": "scroll", "direction": "down"}

3.  **Clicking**: Convert requests to click on elements. The selector should be the text of the element.
    - User: "clica em Documentação"
    - Assistant: {"action": "click", "selector_type": "text", "selector_value": "Documentação"}

4.  **Screen Analysis**: Convert requests asking what is on the screen.
    - User: "o que você vê?"
    - Assistant: {"action": "analyze_screen", "question": "O que há nesta imagem?"}
    - User: "leia o texto na tela"
    - Assistant: {"action": "analyze_screen", "question": "Extraia todo o texto que você conseguir ler desta imagem."}

If the command is unclear, return an error object.
    - User: "qual a capital da frança"
    - Assistant: {"action": "error", "message": "Comando não compreendido."}
"""

def get_ai_command(user_text):
    # (Implementation is the same as before, no changes needed here)
    if not groq_client:
        return {"action": "error", "message": "Cliente da IA não inicializado."}
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            model="llama3-8b-8192",
            temperature=0.2,
            max_tokens=150,
        )
        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)
    except Exception as e:
        send_status(f"Erro na API da IA (texto): {e}")
        return {"action": "error", "message": "Erro ao processar comando com a IA."}

def handle_analyze_screen(question):
    send_status("Iniciando análise de tela...")
    try:
        with mss.mss() as sct:
            # Capture the screen
            sct_img = sct.grab(sct.monitors[1])
            # Convert to PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            # Save to an in-memory buffer
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            img_bytes = buffer.getvalue()

            # Encode in base64
            base64_image = base64.b64encode(img_bytes).decode('utf-8')

            send_status("Tela capturada. Enviando para a IA de Visão...")

            # Send to Groq Vision API
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model="llama-4-scout-17b-16e-instruct",
            )
            description = chat_completion.choices[0].message.content
            send_status(f"IA de Visão respondeu: {description}")

    except Exception as e:
        send_status(f"Erro ao analisar a tela: {e}")

# --- Native Messaging ---
def send_message(message):
    # (Implementation is the same)
    try:
        encoded_content = json.dumps(message).encode('utf-8')
        encoded_length = struct.pack('@I', len(encoded_content))
        sys.stdout.buffer.write(encoded_length)
        sys.stdout.buffer.write(encoded_content)
        sys.stdout.buffer.flush()
    except (IOError, BrokenPipeError):
        sys.exit(0)

def read_message():
    # (Implementation is the same)
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        sys.exit(0)
    message_length = struct.unpack('@I', raw_length)[0]
    message_content = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message_content)

def send_command(command):
    # (Implementation is the same)
    if learning_engine:
        action = command.get("action")
        if action == "navigate":
            domain = command.get("url").split('/')[2] if '//' in command.get("url") else command.get("url")
            learning_engine.log_event("url_visitada", {"nome": domain, "url": command.get("url")})
        elif action in ["scroll", "click"]:
            learning_engine.log_event("comando_executado", {"nome": action, "detalhes": command})
    send_message(command)

def send_status(status_message):
    send_message({"type": "status", "message": status_message})

# --- Main Application Logic ---
def initialize_ai():
    # (Implementation is the same)
    global groq_client
    try:
        # Use a path relative to the current working directory
        config_path = os.path.join("Zoe-2.0", "code", "python", "config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        api_key = config.get("groq_api_key")
        if not api_key:
            send_status("ERRO: Chave da API da Groq não encontrada em config.json.")
            return
        groq_client = Groq(api_key=api_key)
        send_status("Cliente da IA Groq inicializado com sucesso.")
    except FileNotFoundError:
        send_status("ERRO: Arquivo de configuração 'config.json' não encontrado.")
    except Exception as e:
        send_status(f"ERRO ao inicializar a IA: {e}")

def main():
    global learning_engine

    initialize_ai()
    learning_engine = LearningModule()
    send_status("Módulo de aprendizado da Zoe inicializado.")
    send_status("Host Python com IA e Visão iniciado. Aguardando comandos.")

    while True:
        try:
            received_message = read_message()
            user_text = received_message.get("text")

            if user_text:
                send_status(f"Recebido texto: '{user_text}'. Processando com IA...")
                command = get_ai_command(user_text)
                action = command.get("action")

                if not action or action == "error":
                    error_message = command.get("message", "Comando não reconhecido.")
                    send_status(f"Erro da IA: {error_message}")
                    continue

                send_status(f"Comando da IA recebido: {json.dumps(command)}")

                if action == "analyze_screen":
                    # This is a blocking call, run in a thread to not block the main loop
                    question = command.get("question", "Descreva o que você vê.")
                    vision_thread = threading.Thread(target=handle_analyze_screen, args=(question,))
                    vision_thread.start()
                else:
                    # Handle other commands directly
                    send_command(command)

        except (struct.error, json.JSONDecodeError, KeyboardInterrupt, IOError, BrokenPipeError):
            sys.exit(0)

if __name__ == '__main__':
    main()
