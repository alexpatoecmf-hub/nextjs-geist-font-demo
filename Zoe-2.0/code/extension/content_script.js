(function(){
  function showSuggestionOverlay(text, url) {
    const overlayUrl = chrome.runtime.getURL('suggestion_overlay.html');
    fetch(overlayUrl).then(r => r.text()).then(html => {
      const container = document.createElement('div');
      container.innerHTML = html;
      document.body.appendChild(container);

      const overlay = document.getElementById('zoe-suggestion-overlay');
      if (overlay) {
        const txt = overlay.querySelector('.zoe-suggestion-text');
        if (txt) txt.textContent = text || '';
        overlay.dataset.zoeUrl = url || '';
        const openBtn = overlay.querySelector('#zoe-accept');
        if (openBtn) {
          openBtn.onclick = () => {
            const target = overlay.dataset.zoeUrl || '';
            if (target) {
              window.location.href = target;
            }
            overlay.remove();
          };
        }
        const closeBtn = overlay.querySelector('#zoe-dismiss');
        if (closeBtn) {
          closeBtn.onclick = () => overlay.remove();
        }
      }
    });
  }

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!message) return;
    const action = message.action;
    if (!action) return;

    if (action === 'navigate') {
      if (message.url) window.location.href = message.url;
    } else if (action === 'scroll') {
      const dir = message.direction || 'down';
      const amount = window.innerHeight;
      window.scrollBy(0, dir === 'down' ? amount : -amount);
    } else if (action === 'click') {
      const selType = message.selector_type;
      const selValue = message.selector_value;
      if (selValue) {
        if (selType === 'text') {
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT, null, false);
          let el = walker.nextNode();
          let found = null;
          while (el) {
            if (el.textContent && el.textContent.trim() === selValue) {
              found = el;
              break;
            }
            el = walker.nextNode();
          }
          if (found) found.click();
        } else {
          const el = document.querySelector(selValue);
          if (el) el.click();
        }
      }
    } else if (action === 'proactive_suggestion') {
      showSuggestionOverlay(message.text, message.url);
    }
  });
})();
