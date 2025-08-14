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
    const t = texto.toLowerCase();
    let comando = null;

    const abrirMatch = t.match(/abrir\s+([a-z0-9.-]+(?:\.[a-z]{2,})?\/?)/);
    if (abrirMatch) {
      let url = abrirMatch[1];
      if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
      comando = { action: 'navigate', url: url };
    } else if (t.includes('navegar para') || t.includes('vai para')) {
      const partes = t.split(/navegar para|vai para/i);
      const dominio = partes[partes.length - 1].trim();
      if (dominio) {
        let url = dominio;
        if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
        comando = { action: 'navigate', url: url };
      }
    }

    if (!comando && (t.includes('rolar para baixo') || t.includes('rolar para baixo'))) {
      comando = { action: 'scroll', direction: 'down' };
    } else if (!comando && t.includes('rolar para cima')) {
      comando = { action: 'scroll', direction: 'up' };
    }

    if (!comando && t.startsWith('clicar')) {
      const parts = t.split('clicar');
      const seletor = (parts[1] || '').trim();
      if (seletor) {
        comando = { action: 'click', selector_type: 'text', selector_value: seletor };
      }
    }

    if (!comando && t.includes('abrir domínio frequente')) {
      comando = { action: 'proactive_suggestion' };
    }

    if (comando) {
      chrome.runtime.sendMessage({ toHost: comando }, (resp) => {
        status.textContent = resp && resp.status ? `Status: ${resp.status}` : 'Comando enviado';
      });
    } else {
      status.textContent = "Comando não reconhecido. Ex.: abrir youtube.com, rolar para baixo, clicar Docs";
    }
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
