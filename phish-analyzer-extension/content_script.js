// content_script.js
console.log("✅ Content script loaded into Gmail");

(async () => {
  // Helper: find currently open Gmail message DOM (works on Gmail web view)
  function getGmailMessageData() {
    try {
      // Gmail's DOM changes, target typical selectors
      // Subject
      const subjectEl = document.querySelector('h2[role="heading"]') || document.querySelector('.hP');
      const subject = subjectEl ? subjectEl.innerText.trim() : "(no subject)";

      // Sender
      const fromEl = document.querySelector('.gD') || document.querySelector('.yX.xY .gD');
      const sender = fromEl ? fromEl.getAttribute('email') || fromEl.innerText.trim() : "(unknown)";

      // Body (prefer expanded readable text)
      const bodyEl = document.querySelector('div.a3s.aXjCH') || document.querySelector('.ii.gt');
      const body = bodyEl ? bodyEl.innerText.trim() : "";

      // Extract URLs from DOM anchors found inside bodyEl
      let urls = [];
      if (bodyEl) {
        const anchors = bodyEl.querySelectorAll('a[href]');
        anchors.forEach(a => {
          try { urls.push(a.href); } catch(e) {}
        });
      }

      if (!subject && !sender && !body) return null;
      return { subject, sender, recipient: "(me)", body, urls };
    } catch (e) {
      return null;
    }
  }

  // Insert overlay panel (or update existing)
  // Insert overlay panel (or update existing)
function showOverlay(result) {
  const risk = result.final_risk || 0;
  let riskClass = "phish-safe";
  let riskLabel = "Safe";

  if (risk >= 0.6) {
    riskClass = "phish-danger";
    riskLabel = "Phishing";
  } else if (risk >= 0.3) {
    riskClass = "phish-suspicious";
    riskLabel = "Suspicious";
  }

  let panel = document.getElementById('phish-analyzer-panel');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'phish-analyzer-panel';
    panel.style.position = 'fixed';
    panel.style.right = '16px';
    panel.style.bottom = '24px';
    panel.style.zIndex = 2147483647;
    panel.style.background = '#ffffff';
    panel.style.border = '1px solid #ddd';
    panel.style.boxShadow = '0 6px 18px rgba(0,0,0,0.12)';
    panel.style.padding = '12px';
    panel.style.width = '360px';
    panel.style.fontFamily = 'Arial, sans-serif';
    panel.style.borderRadius = '8px';
    document.body.appendChild(panel);
  }

  // Fill content
  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center">
      <strong style="font-size:17px;">Email Phish Analyzer</strong>
      <a id="phish-close" style="cursor:pointer;color:#666;font-size:18px;">✕</a>
    </div>
    <div style="margin-top:8px;font-size:15px;">
      <!-- Final risk: <strong>${risk.toFixed(2)}</strong> -->
      <span style="
        display:inline-block;
        margin-left:6px;
        padding:2px 8px;
        border-radius:6px;
        font-size:13px;
        font-weight:bold;
        ${riskClass === 'phish-safe' ? 'background:#e6f4ea;color:#137333;' :
          riskClass === 'phish-suspicious' ? 'background:#fff4e5;color:#b26a00;' :
          'background:#fde8e6;color:#d93025;'}
      ">
        ${riskLabel}
      </span>
    </div>
    <div style="margin-top:8px">
      <details open>
        <summary style="cursor:pointer;font-weight:500;font-size:14px;">Reason & Actions</summary>
        <div style="margin-top:8px;color:#222;font-size:13px">
          <div style="margin-bottom:10px;">
            <strong>LLM Reason:</strong> 
            <span style="color:#1976d2;">${result.llm_reason || ''}</span>
          </div>
          <div style="margin-top:8px">
            <strong>Recommended Actions:</strong>
            <ol id="phish-actions" style="padding-left:20px;margin-top:6px;margin-bottom:0;"></ol>
          </div>
        </div>
      </details>
    </div>
  `;

  const closeBtn = panel.querySelector('#phish-close');
  closeBtn.onclick = () => panel.remove();

  // Actions list
  const actionsEl = panel.querySelector('#phish-actions');
  actionsEl.innerHTML = '';
  const actions = result.llm_actions || [];
  actions.forEach(a => {
    const li = document.createElement('li');
    li.innerText = a.replace(/^\s*\d+\.[\s-]*/, '');
    li.style.marginBottom = '8px';
    li.style.lineHeight = '1.5';
    actionsEl.appendChild(li);
  });
}


  // Show spinner while background analysis runs (with min display time)
  let spinnerTimeout = null;
  function showSpinner() {
    let spinner = document.getElementById('phish-analyzer-spinner');
    if (spinner) return;
    const s = document.createElement('div');
    s.id = 'phish-analyzer-spinner';
    s.style.position = 'fixed'; s.style.right = '16px'; s.style.bottom = '24px';
    s.style.zIndex = 2147483646; s.style.padding = '10px'; s.style.background = '#fff';
    s.style.border = '1px solid #ddd'; s.style.borderRadius = '8px';
    s.innerHTML = '<span class="phish-spinner" style="display:inline-block;width:18px;height:18px;border:3px solid #ccc;border-top:3px solid #333;border-radius:50%;animation:phish-spin 1s linear infinite;margin-right:8px;vertical-align:middle"></span>Analyzing email...';
    document.body.appendChild(s);
    // Add spinner CSS if not present
    if (!document.getElementById('phish-spinner-style')) {
      const style = document.createElement('style');
      style.id = 'phish-spinner-style';
      style.innerHTML = `@keyframes phish-spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}`;
      document.head.appendChild(style);
    }
    // Ensure spinner stays at least 800ms
    spinnerTimeout = Date.now();
  }
  function hideSpinner() {
    const s = document.getElementById('phish-analyzer-spinner');
    if (!s) return;
    const elapsed = Date.now() - (spinnerTimeout || 0);
    if (elapsed < 800) {
      setTimeout(() => { if (s) s.remove(); }, 800 - elapsed);
    } else {
      s.remove();
    }
  }

  // When user opens an email or uses extension action, extract and send to background
  async function analyzeCurrentEmail() {
    const data = getGmailMessageData();
    if (!data) {
      alert('Could not extract email data. Please open an email and try again.');
      return;
    }
    showSpinner();
    // send to background (service worker) to forward to backend
    chrome.runtime.sendMessage({ type: 'analyze_email', payload: data }, (resp) => {
      hideSpinner();
      if (chrome.runtime.lastError) {
        showOverlay({ final_risk: 0, label: 'Error', llm_reason: chrome.runtime.lastError.message, llm_actions: [] });
        return;
      }
      if (!resp || resp.error) {
        showOverlay({ final_risk: 0, label: 'Error', llm_reason: resp?.error || 'unknown', llm_actions: [] });
        return;
      }
      // show overlay with results
      showOverlay(resp.result || {});
    });
  }

  // Add a small analyze button inside Gmail toolbar for convenience (idempotent)
  function attachAnalyzeButton() {
    // Try multiple selectors for Gmail toolbar
    const toolbars = [
      ...document.querySelectorAll('div[aria-label="More"]'),
      ...document.querySelectorAll('div.aU'),
      ...document.querySelectorAll('div[role="toolbar"]')
    ];
    // let toolbar = toolbars.find(tb => tb && !tb.querySelector('#phish-btn'));
    // if (toolbar) {
    //   if (document.getElementById('phish-btn')) return;
    //   const btn = document.createElement('button');
    //   btn.id = 'phish-btn';
    //   btn.innerText = 'Analyze';
    //   btn.style.marginLeft = '8px';
    //   btn.onclick = analyzeCurrentEmail;
    //   toolbar.appendChild(btn);
    // } else {
      // Fallback: floating button if no toolbar found
      if (document.getElementById('phish-float-btn')) return;
      const floatBtn = document.createElement('button');
      floatBtn.id = 'phish-float-btn';
      floatBtn.innerText = 'Analyze';
      floatBtn.style.position = 'fixed';
      floatBtn.style.right = '24px';
      floatBtn.style.bottom = '100px';
      floatBtn.style.zIndex = 2147483647;
      floatBtn.style.background = '#1976d2';
      floatBtn.style.color = '#fff';
      floatBtn.style.border = 'none';
      floatBtn.style.borderRadius = '24px';
      floatBtn.style.padding = '12px 24px';
      floatBtn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.18)';
      floatBtn.style.fontSize = '16px';
      floatBtn.style.cursor = 'pointer';
      floatBtn.onclick = analyzeCurrentEmail;
      document.body.appendChild(floatBtn);
    // }
  }

  // Attempt to auto analyze when the DOM stabilizes (user opens mail)
  let lastHash = '';
  setInterval(() => {
    // simple heuristic: url changes when an email is opened
    if (location.href !== lastHash) {
      lastHash = location.href;
      // try attach UI and optionally auto-run analysis
      setTimeout(() => {
        attachAnalyzeButton();
        // Optionally auto-run analysis (uncomment to enable)
        // analyzeCurrentEmail();
      }, 1500);
    }
  }, 1200);

})();
