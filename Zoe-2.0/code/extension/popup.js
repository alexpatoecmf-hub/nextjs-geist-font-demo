(function(){
  const btn = document.getElementById('btnZoeLive');
  const status = document.getElementById('status');
  const circle = document.getElementById('circleListening');
  const transcricao = document.getElementById('transcricao');
  let recognizer = null;
  let listening = false;

  function iniciarReconhecimento() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      status.textContent = "Navegador não suporta Web Speech API. Use Chrome/Chromium moderno.";
      return;
    }
    recognizer = new SpeechRecognition();
    recognizer.lang = 'pt-BR';
    recognizer.continuous = false;
    recognizer.interimResults = false;

    recognizer.onstart = () => {
      listening = true;
      circle.style.display = 'block';
      status.textContent = "Ouvindo...";
    };
    recognizer.onresult = (evt) => {
      const transcript = Array.from(evt.results)
        .map(r => r[0].transcript)
        .join('');
      transcricao.textContent = transcript;
      enviarComandoPorVoz(transcript);
    };
    recognizer.onerror = (e) => {
      status.textContent = `Erro de voz: ${e.error}`;
      terminarReconhecimento();
    };
    recognizer.onend = () => {
      terminarReconhecimento();
    };
    recognizer.start();
  }

  function terminarReconhecimento() {
    listening = false;
    circle.style.display = 'none';
    status.textContent = "Pronto.";
  }

  function enviarComandoPorVoz(texto) {
    if (!texto) {
      status.textContent = "Nenhum comando de voz detectado.";
      return;
    }

    // Envia o texto bruto para o host nativo, que usará a IA para interpretá-lo.
    status.textContent = "Enviando para a IA da Zoe...";
    chrome.runtime.sendMessage({ toHost: { text: texto } }, (resp) => {
      // O host nativo pode enviar uma resposta de status, mas a ação principal
      // será um novo comando enviado para o content_script.
      // A UI aqui não precisa fazer mais nada.
      if (resp && resp.status === 'host_indisponivel') {
          status.textContent = "Erro: Host nativo da Zoe não está conectado.";
      }
    });
  }

  btn.addEventListener('click', () => {
    if (listening) {
      if (recognizer) recognizer.stop();
      terminarReconhecimento();
    } else {
      iniciarReconhecimento();
    }
  });
})();
