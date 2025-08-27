document.addEventListener('DOMContentLoaded', async () => {
  const b = await chrome.storage.local.get(['apiKey','sendFullBody']);
  document.getElementById('apiKey').value = b.apiKey || '';
  document.getElementById('sendFullBody').checked = 
      b.sendFullBody === undefined ? true : b.sendFullBody;

  document.getElementById('save').onclick = async () => {
    const apiKey = document.getElementById('apiKey').value;
    const sendFullBody = document.getElementById('sendFullBody').checked;
    await chrome.storage.local.set({ apiKey, sendFullBody });
    document.getElementById('status').innerText = '✅ Saved!';
    setTimeout(() => document.getElementById('status').innerText = '', 2000);
  };
});
