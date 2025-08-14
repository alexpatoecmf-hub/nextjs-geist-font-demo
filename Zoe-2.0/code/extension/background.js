let portNative = null;
const NOME_HOST = 'com.zoe.native_host';
function conectar() {
  portNative = chrome.runtime.connectNative(NOME_HOST);
  portNative.onMessage.addListener((msg) => {
    forwardToActiveTab(msg);
  });
  portNative.onDisconnect.addListener(() => {
    setTimeout(conectar, 1000);
  });
}
function forwardToActiveTab(message) {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    if (tabs.length === 0) return;
    const tabId = tabs[0].id;
    chrome.tabs.sendMessage(tabId, message);
  });
}
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request && request.toHost) {
    if (portNative) {
      portNative.postMessage(request.toHost);
      sendResponse({status: 'enviado'});
    } else {
      sendResponse({status: 'host_indisponivel'});
    }
    return;
  }
  sendResponse({status: 'ok'});
}
conectar();
// Opcional: outras portas podem ser tratadas aqui
