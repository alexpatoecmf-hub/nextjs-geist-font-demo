# -*- coding: utf-8 -*-
# Core nativo (PT-BR) - Zoe
import sys
import json
import struct
import threading
import time
from learning_module import LearningModule

learning_engine = None

def send_message(message):
    try:
        encoded_content = json.dumps(message).encode('utf-8')
        encoded_length = struct.pack('@I', len(encoded_content))
        sys.stdout.buffer.write(encoded_length)
        sys.stdout.buffer.write(encoded_content)
        sys.stdout.buffer.flush()
    except (IOError, BrokenPipeError):
        sys.exit(0)

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        sys.exit(0)
    message_length = struct.unpack('@I', raw_length)[0]
    message_content = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message_content)

def send_command(command):
    if learning_engine:
        action = command.get("action")
        if action == "navigate":
            domain = command.get("url").split('/')[2] if '//' in command.get("url") else command.get("url")
            learning_engine.log_event("url_visitada", {"nome": domain, "url": command.get("url")})
        elif action in ["scroll", "click"]:
            learning_engine.log_event("comando_executado", {
                "nome": action,
                "detalhes": command
            })
    send_message(command)

def send_status(status_message):
    send_message({"type": "status", "message": status_message})

def check_suggestions_periodically():
    while True:
        time.sleep(300)
        if not learning_engine:
            continue
        sugestao = learning_engine.check_for_suggestion()
        if sugestao:
            send_status(f"Sugestão proativa encontrada: {sugestao.get('suggestion_text', 'N/A')}")
            send_message({
                "action": "proactive_suggestion",
                "text": sugestao.get('suggestion_text'),
                "url": sugestao.get('url')
            })

def run_demo_sequence():
    time.sleep(5)
    send_status("Demo: Navegando para o GitHub para gerar dados de aprendizado...")
    send_command({"action": "navigate", "url": "https://github.com"})
    time.sleep(4)
    send_status("Demo: Navegando para o site do Python...")
    send_command({"action": "navigate", "url": "https://www.python.org"})
    time.sleep(4)
    send_status("Demo: Rolando a página para baixo...")
    send_command({"action": "scroll", "direction": "down"})
    time.sleep(2)
    send_status("Demo: Clicando em 'Docs'...")
    send_command({"action": "click", "selector_type": "text", "selector_value": "Docs"})
    time.sleep(4)
    send_status("Sequência de demonstração finalizada.")

if __name__ == '__main__':
    learning_engine = LearningModule()
    send_status("Módulo de aprendizado da Zoe inicializado.")
    training_result = learning_engine.train_model()
    send_status(training_result)

    suggestion_thread = threading.Thread(target=check_suggestions_periodically)
    suggestion_thread.daemon = True
    suggestion_thread.start()
    send_status("Motor de sugestões proativas iniciado.")

    demo_thread = threading.Thread(target=run_demo_sequence)
    demo_thread.daemon = True
    # demo_thread.start() # Descomente para executar a demonstração automaticamente

    send_status("Host Python iniciado. Aguardando comandos da extensão.")

    while True:
        try:
            received_message = read_message()
            if learning_engine:
                learning_engine.log_event("extension_response", {"data": received_message})
            send_status(f"Resposta recebida da extensão: {json.dumps(received_message)}")
        except (struct.error, json.JSONDecodeError, KeyboardInterrupt, IOError, BrokenPipeError):
            sys.exit(0)
