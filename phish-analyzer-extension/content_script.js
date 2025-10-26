// content_script.js
console.log("Content script loaded into Gmail");

(async () => {
  // Helper: find currently open Gmail message DOM (works on Gmail web view)
  function getGmailMessageData() {
    try {
      // Gmail's DOM changes, target typical selectors
      // Subject
      const subjectEl =
        document.querySelector('h2[role="heading"]') ||
        document.querySelector(".hP");
      const subject = subjectEl ? subjectEl.innerText.trim() : "(no subject)";

      // Sender
      const fromEl =
        document.querySelector(".gD") || document.querySelector(".yX.xY .gD");
      const sender = fromEl
        ? fromEl.getAttribute("email") || fromEl.innerText.trim()
        : "(unknown)";

      // Body (prefer expanded readable text)
      const bodyEl =
        document.querySelector("div.a3s.aXjCH") ||
        document.querySelector(".ii.gt");
      const body = bodyEl ? bodyEl.innerText.trim() : "";

      // Extract URLs from DOM anchors found inside bodyEl
      let urls = [];
      if (bodyEl) {
        const anchors = bodyEl.querySelectorAll("a[href]");
        anchors.forEach((a) => {
          try {
            urls.push(a.href);
          } catch (e) {}
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

    // Blockchain information
    const blockchainData = result.blockchain_signals || {};
    const senderReputation = result.sender_reputation || {};
    const senderClassification = blockchainData.sender_classification || {};
    const blockchainWeight = result.blockchain_weight || 0;
    const blockchainAvailable = blockchainWeight > 0;
    const fromPreviousIncident = result.from_previous_incident || false;
    const forceLlmUsed = result.force_llm_used || false;

    let panel = document.getElementById("phish-analyzer-panel");
    if (!panel) {
      panel = document.createElement("div");
      panel.id = "phish-analyzer-panel";
      document.body.appendChild(panel);
    }

    // Build blockchain section with previous incident warning
    const blockchainSection = blockchainAvailable && fromPreviousIncident
      ? `
    <div style="margin-top:8px">
      <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:12px;margin-bottom:12px;">
        <div style="font-weight:600;font-size:13px;color:#856404;margin-bottom:6px;">⚠️ Based on Previous Incidents</div>
        <div style="font-size:12px;color:#856404;line-height:1.6;">
          This sender was previously classified as <strong>${senderClassification.classification || 'unknown'}</strong>.
          ${!forceLlmUsed ? 'If you believe this classification is incorrect, click "Run Fresh LLM Analysis" below.' : 'Fresh LLM analysis has been performed.'}
        </div>
      </div>
      <details ${forceLlmUsed ? '' : 'open'}>
        <summary style="cursor:pointer;font-weight:500;font-size:14px;">🔗 Sender Reputation</summary>
        <div style="margin-top:8px;color:#222;font-size:12px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span>Classification:</span>
            <span style="font-weight:bold;color:${
              senderClassification.classification === "spam" ? "#d93025" : "#137333"
            };">
              ${(senderClassification.classification || "unknown").toUpperCase()}
            </span>
          </div>
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span>Confidence:</span>
            <span style="font-weight:bold;">${((senderClassification.confidence || 0) * 100).toFixed(0)}%</span>
          </div>
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span>Reputation Score:</span>
            <span style="font-weight:bold;">${senderClassification.reputation_score || 50}/100</span>
          </div>
        </div>
      </details>
    </div>
  `
      : blockchainAvailable
      ? `
    <div style="margin-top:8px">
      <div style="font-size:12px;color:#666;">
        ✅ Blockchain reputation checked - no previous incidents found
      </div>
    </div>
  `
      : `
    <div style="margin-top:8px;color:#666;font-size:12px;">
      ⚠️ Blockchain not available - analysis based on ML/AI only
    </div>
  `;

    panel.innerHTML = `
    <div class="phish-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;padding-bottom:12px;border-bottom:2px solid #e8f0fe;">
      <div class="phish-title" style="font-size:20px;font-weight:700;color:#1976d2;">
        Email Phish Analyzer
      </div>
      <a id="phish-close" style="cursor:pointer;color:#666;font-size:28px;text-decoration:none;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:50%;" title="Close">✕</a>
    </div>
    
    <div class="phish-content-scrollable" style="max-height:calc(85vh - 80px);overflow-y:auto;overflow-x:hidden;padding-right:8px;">
      <div style="margin-bottom:16px;padding:12px;background:${
        riskClass === "phish-safe"
          ? "linear-gradient(135deg, #e6f4ea 0%, #d4ede0 100%)"
          : riskClass === "phish-suspicious"
          ? "linear-gradient(135deg, #fff4e5 0%, #ffe8cc 100%)"
          : "linear-gradient(135deg, #fde8e6 0%, #fcd3d0 100%)"
      };border-radius:8px;border-left:4px solid ${
        riskClass === "phish-safe"
          ? "#137333"
          : riskClass === "phish-suspicious"
          ? "#b26a00"
          : "#d93025"
      };">
        <div style="font-size:14px;font-weight:600;color:#444;margin-bottom:4px;">Risk Assessment:</div>
        <div style="font-size:24px;font-weight:bold;color:${
          riskClass === "phish-safe"
            ? "#137333"
            : riskClass === "phish-suspicious"
            ? "#b26a00"
            : "#d93025"
        };">
          ${riskLabel} (${
            riskClass === "phish-danger"
              ? (risk * 100).toFixed(0)  // For "Phishing", show risk as-is
              : ((1 - risk) * 100).toFixed(0)  // For "Safe" and "Suspicious", show confidence (100 - risk)
          }%)
        </div>
      </div>
      
      
      
      <div style="margin-top:16px;background:#f8f9fa;border-radius:8px;padding:12px;border:1px solid #e0e0e0;">
        <details open>
          <summary style="cursor:pointer;font-weight:600;font-size:15px;color:#1976d2;margin-bottom:12px;">🤖 AI Analysis & Actions</summary>
          
          <div style="background:white;padding:12px;border-radius:6px;margin-top:12px;border:1px solid #e8f0fe;">
            <div style="font-weight:600;font-size:13px;color:#444;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
              <span style="color:#1976d2;">💭</span> Reasoning:
            </div>
            <div id="phish-reasoning" style="color:#333;font-size:13px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word;max-width:100%;"></div>
          </div>
          
          <div style="background:white;padding:12px;border-radius:6px;margin-top:12px;border:1px solid #e8f0fe;">
            <div style="font-weight:600;font-size:13px;color:#444;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
              <span style="color:#1976d2;">✅</span> Recommended Actions:
            </div>
            <ol id="phish-actions" style="padding-left:24px;margin:0;color:#333;font-size:13px;line-height:1.8;"></ol>
          </div>
        </details>
      </div>
      
      <div style="margin-top:16px;border-top:2px solid #e8f0fe;padding-top:12px;">
        <div style="font-size:13px;color:#666;margin-bottom:8px;font-weight:600;">📊 Help improve accuracy:</div>
        <div style="display:flex;gap:10px;margin-bottom:${fromPreviousIncident && !forceLlmUsed ? '10px' : '0'};">
          <button id="feedback-safe" style="flex:1;padding:8px 12px;border:2px solid #137333;background:#e6f4ea;color:#137333;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;">✅ Safe</button>
          <button id="feedback-phishing" style="flex:1;padding:8px 12px;border:2px solid #d93025;background:#fde8e6;color:#d93025;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;">❌ Phishing</button>
        </div>
        ${fromPreviousIncident && !forceLlmUsed ? `
        <button id="run-llm-analysis" style="width:100%;padding:10px 12px;border:2px solid #1976d2;background:#e3f2fd;color:#1976d2;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;margin-top:8px;">
          🔄 Run Fresh LLM Analysis
        </button>
        ` : ''}
      </div>
    </div>
  `;

    // Insert full reasoning text (no trimming)
    const reasoningEl = panel.querySelector("#phish-reasoning");
    if (reasoningEl) {
      const fullReasoning = result.llm_reason || "No reasoning provided";
      reasoningEl.textContent = fullReasoning;
    }

    const closeBtn = panel.querySelector("#phish-close");
    closeBtn.onclick = () => {
      panel.style.animation = "phish-fadeout 0.2s ease";
      setTimeout(() => panel.remove(), 200);
    };

    // Make panel draggable by header
    const header = panel.querySelector(".phish-header");
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;

    header.style.cursor = "move";
    header.addEventListener("mousedown", dragStart);
    document.addEventListener("mousemove", drag);
    document.addEventListener("mouseup", dragEnd);

    function dragStart(e) {
      if (e.target.id === "phish-close") return; // Don't drag when clicking close
      initialX = e.clientX - panel.offsetLeft;
      initialY = e.clientY - panel.offsetTop;
      isDragging = true;
    }

    function drag(e) {
      if (isDragging) {
        e.preventDefault();
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;
        panel.style.left = currentX + "px";
        panel.style.top = currentY + "px";
        panel.style.right = "auto";
        panel.style.bottom = "auto";
      }
    }

    function dragEnd() {
      isDragging = false;
    }

    // Actions list - display full text without trimming
    const actionsEl = panel.querySelector("#phish-actions");
    if (actionsEl) {
      actionsEl.innerHTML = "";
      const actions = result.llm_actions || [];
      if (actions.length === 0) {
        const li = document.createElement("li");
        li.textContent = "No specific actions recommended";
        li.style.color = "#666";
        actionsEl.appendChild(li);
      } else {
        actions.forEach((action) => {
          const li = document.createElement("li");
          // Don't trim - show full action text
          const fullAction = action.replace(/^\s*\d+\.[\s-]*/, "");
          li.textContent = fullAction;
          li.style.marginBottom = "10px";
          li.style.lineHeight = "1.7";
          li.style.wordWrap = "break-word";
          actionsEl.appendChild(li);
        });
      }
    }

    // Feedback buttons
    const feedbackSafeBtn = panel.querySelector("#feedback-safe");
    const feedbackPhishingBtn = panel.querySelector("#feedback-phishing");
    const runLlmBtn = panel.querySelector("#run-llm-analysis");

    feedbackSafeBtn.onclick = () => submitFeedback(result, "ham");
    feedbackPhishingBtn.onclick = () => submitFeedback(result, "spam");
    
    // Run LLM Analysis button
    if (runLlmBtn) {
      runLlmBtn.onclick = () => runFreshLlmAnalysis();
    }

    // Store result for feedback
    panel.analysisResult = result;
  }

  // Function to run fresh LLM analysis (bypassing blockchain)
  async function runFreshLlmAnalysis() {
    const data = getGmailMessageData();
    if (!data) {
      alert("Could not extract email data. Please try again.");
      return;
    }
    
    // Show loading state
    const panel = document.getElementById("phish-analyzer-panel");
    if (panel) {
      const llmBtn = panel.querySelector("#run-llm-analysis");
      if (llmBtn) {
        llmBtn.disabled = true;
        llmBtn.innerHTML = `
          <span class="phish-spinner" style="display:inline-block;width:12px;height:12px;border:2px solid #1976d2;border-top:2px solid transparent;border-radius:50%;animation:phish-spin 1s linear infinite;margin-right:8px;"></span>
          Running LLM Analysis...
        `;
      }
    }
    
    showSpinner();
    
    // Add force_llm flag to data
    const dataWithForceLlm = { ...data, force_llm: true };
    
    // Send to background with force_llm flag
    chrome.runtime.sendMessage(
      { type: "analyze_email", payload: dataWithForceLlm },
      (resp) => {
        hideSpinner();
        if (chrome.runtime.lastError) {
          showOverlay({
            final_risk: 0,
            label: "Error",
            llm_reason: chrome.runtime.lastError.message,
            llm_actions: [],
          });
          return;
        }
        if (!resp || resp.error) {
          showOverlay({
            final_risk: 0,
            label: "Error",
            llm_reason: resp?.error || "unknown",
            llm_actions: [],
          });
          return;
        }
        // Show overlay with fresh LLM results
        showOverlay(resp.result || {});
      }
    );
  }

  // Function to submit user feedback to blockchain
  async function submitFeedback(analysisResult, classification) {
    try {
      const panel = document.getElementById("phish-analyzer-panel");
      let feedbackDiv = null;
      
      if (panel) {
        feedbackDiv =
          panel.querySelector(".feedback-buttons") ||
          panel.querySelector('[style*="Help improve accuracy"]')
            ?.parentElement;
      }
      
      // Immediately disable buttons to prevent double-clicks
      if (feedbackDiv) {
        const safeBtn = feedbackDiv.querySelector("#feedback-safe");
        const phishBtn = feedbackDiv.querySelector("#feedback-phishing");
        if (safeBtn) safeBtn.disabled = true;
        if (phishBtn) phishBtn.disabled = true;
      }
      
      // Helper function to update status
      const updateStatus = (emoji, message, color = "#666", showSpinner = false) => {
        if (feedbackDiv) {
          feedbackDiv.innerHTML = `
          <div style="font-size:13px;color:${color};text-align:center;padding:12px;background:#f8f9fa;border-radius:8px;border:1px solid #e0e0e0;">
            ${showSpinner ? `<span class="phish-spinner" style="display:inline-block;width:14px;height:14px;border:2px solid ${color};border-top:2px solid transparent;border-radius:50%;animation:phish-spin 1s linear infinite;margin-right:8px;vertical-align:middle;"></span>` : ''}
            <strong>${emoji} ${message}</strong>
          </div>
        `;
        }
      };
      
      // Step 1: Preparing data
      updateStatus("📦", "Preparing feedback data...", "#1976d2", true);
      await new Promise(resolve => setTimeout(resolve, 400));

      // Get user settings
      const settings = await new Promise((resolve) => {
        chrome.storage.local.get(["apiKey", "privacyMode"], resolve);
      });

      // Re-extract current email data to ensure we have fresh sender and URLs
      const currentEmailData = getGmailMessageData();
      
      // Prepare analysis result with all necessary data
      const analysisData = {
        ...analysisResult,
        sender: currentEmailData?.sender || analysisResult.sender || (analysisResult.details && analysisResult.details.sender),
        final_risk: analysisResult.final_risk || 0.5,
        details: {
          ...(analysisResult.details || {}),
          sender: currentEmailData?.sender || analysisResult.sender,
          urls: currentEmailData?.urls || (analysisResult.details && analysisResult.details.urls) || [],
          domains: (analysisResult.details && analysisResult.details.domains) || []
        }
      };

      // console.log("📤 Submitting feedback with data:", {
      //   sender: analysisData.sender,
      //   urlCount: analysisData.details.urls.length,
      //   domainCount: analysisData.details.domains.length,
      //   classification: classification
      // });

      // Step 2: Connecting to blockchain
      updateStatus("🔗", "Connecting to blockchain...", "#1976d2", true);
      await new Promise(resolve => setTimeout(resolve, 400));

      // Step 3: Submitting to blockchain
      updateStatus("⛓️", `Reporting sender as ${classification === 'spam' ? 'phishing' : 'safe'}...`, "#1976d2", true);

      // Submit feedback to blockchain via backend
      const response = await fetch(
        "http://127.0.0.1:8080/blockchain/bulk-report",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(settings.apiKey && { "x-api-key": settings.apiKey }),
          },
          body: JSON.stringify({
            analysis_result: analysisData,
            user_classification: classification,
            reason: `User feedback from Gmail extension - ${classification === 'spam' ? 'Phishing reported' : 'Safe email confirmed'}`,
          }),
        }
      );

      const result = await response.json();

      // Step 4: Processing result
      updateStatus("📊", "Processing response...", "#1976d2", true);
      await new Promise(resolve => setTimeout(resolve, 400));

      // Show feedback result
      const isSuccess = result.successful_reports > 0;
      const senderEmail = result.sender_reported || analysisData.sender || 'sender';
      
      if (isSuccess) {
        updateStatus(
          "✅", 
          `Success! Reported "${senderEmail}" as ${classification === 'spam' ? '🚫 Phishing' : '✅ Safe'}`, 
          "#137333", 
          false
        );

        // Auto-restore buttons after 3 seconds
        setTimeout(() => {
          if (feedbackDiv) {
            feedbackDiv.innerHTML = `
              <div style="font-size:13px;color:#666;margin-bottom:8px;font-weight:600;">📊 Help improve accuracy:</div>
              <div style="display:flex;gap:10px;">
                <button id="feedback-safe" style="flex:1;padding:8px 12px;border:2px solid #137333;background:#e6f4ea;color:#137333;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;">✅ Safe</button>
                <button id="feedback-phishing" style="flex:1;padding:8px 12px;border:2px solid #d93025;background:#fde8e6;color:#d93025;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;">❌ Phishing</button>
              </div>
            `;
            
            // Re-attach handlers
            const newSafeBtn = feedbackDiv.querySelector("#feedback-safe");
            const newPhishingBtn = feedbackDiv.querySelector("#feedback-phishing");
            if (newSafeBtn) newSafeBtn.onclick = () => submitFeedback(analysisResult, "ham");
            if (newPhishingBtn) newPhishingBtn.onclick = () => submitFeedback(analysisResult, "spam");
          }
        }, 3000);
      } else {
        updateStatus(
          "❌", 
          `Failed: ${result.error || 'Unknown error'}`, 
          "#d93025", 
          false
        );

        // Auto-restore buttons after 3 seconds
        setTimeout(() => {
          if (feedbackDiv) {
            feedbackDiv.innerHTML = `
              <div style="font-size:13px;color:#666;margin-bottom:8px;font-weight:600;">📊 Help improve accuracy:</div>
              <div style="display:flex;gap:10px;">
                <button id="feedback-safe" style="flex:1;padding:8px 12px;border:2px solid #137333;background:#e6f4ea;color:#137333;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;">✅ Safe</button>
                <button id="feedback-phishing" style="flex:1;padding:8px 12px;border:2px solid #d93025;background:#fde8e6;color:#d93025;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;">❌ Phishing</button>
              </div>
            `;
            
            // Re-attach handlers
            const newSafeBtn = feedbackDiv.querySelector("#feedback-safe");
            const newPhishingBtn = feedbackDiv.querySelector("#feedback-phishing");
            if (newSafeBtn) newSafeBtn.onclick = () => submitFeedback(analysisResult, "ham");
            if (newPhishingBtn) newPhishingBtn.onclick = () => submitFeedback(analysisResult, "spam");
          }
        }, 3000);
      }
    } catch (error) {
      // console.error("Failed to submit feedback:", error);

      // Show error
      const panel = document.getElementById("phish-analyzer-panel");
      if (panel) {
        const feedbackDiv =
          panel.querySelector(".feedback-buttons") ||
          panel.querySelector('[style*="Preparing feedback"]')?.parentElement ||
          panel.querySelector('[style*="Connecting to blockchain"]')?.parentElement ||
          panel.querySelector('[style*="Reporting sender"]')?.parentElement ||
          panel.querySelector('[style*="Processing response"]')?.parentElement;
        if (feedbackDiv) {
          feedbackDiv.innerHTML = `
          <div style="font-size:13px;color:#d93025;text-align:center;padding:12px;background:#fde8e6;border-radius:8px;border:1px solid #d93025;">
            <strong>❌ Connection Error</strong><br>
            <span style="font-size:11px;">Could not connect to backend. Please ensure the server is running.</span>
          </div>
        `;
        
          // Auto-restore buttons after 3 seconds
          setTimeout(() => {
            if (feedbackDiv) {
              feedbackDiv.innerHTML = `
                <div style="font-size:13px;color:#666;margin-bottom:8px;font-weight:600;">📊 Help improve accuracy:</div>
                <div style="display:flex;gap:10px;">
                  <button id="feedback-safe" style="flex:1;padding:8px 12px;border:2px solid #137333;background:#e6f4ea;color:#137333;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;">✅ Safe</button>
                  <button id="feedback-phishing" style="flex:1;padding:8px 12px;border:2px solid #d93025;background:#fde8e6;color:#d93025;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;">❌ Phishing</button>
                </div>
              `;
              
              // Re-attach handlers
              const newSafeBtn = feedbackDiv.querySelector("#feedback-safe");
              const newPhishingBtn = feedbackDiv.querySelector("#feedback-phishing");
              if (newSafeBtn) newSafeBtn.onclick = () => submitFeedback(analysisResult, "ham");
              if (newPhishingBtn) newPhishingBtn.onclick = () => submitFeedback(analysisResult, "spam");
            }
          }, 3000);
        }
      }
    }
  }

  // Show spinner while background analysis runs (with min display time)
  let spinnerTimeout = null;
  function showSpinner() {
    let spinner = document.getElementById("phish-analyzer-spinner");
    if (spinner) return;
    const s = document.createElement("div");
    s.id = "phish-analyzer-spinner";
    s.style.position = "fixed";
    s.style.right = "16px";
    s.style.bottom = "24px";
    s.style.zIndex = 2147483646;
    s.style.padding = "10px";
    s.style.background = "#fff";
    s.style.border = "1px solid #ddd";
    s.style.borderRadius = "8px";
    s.innerHTML =
      '<span class="phish-spinner" style="display:inline-block;width:18px;height:18px;border:3px solid #ccc;border-top:3px solid #333;border-radius:50%;animation:phish-spin 1s linear infinite;margin-right:8px;vertical-align:middle"></span>Analyzing email...';
    document.body.appendChild(s);
    // Add spinner CSS if not present
    if (!document.getElementById("phish-spinner-style")) {
      const style = document.createElement("style");
      style.id = "phish-spinner-style";
      style.innerHTML = `@keyframes phish-spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}`;
      document.head.appendChild(style);
    }
    // Ensure spinner stays at least 800ms
    spinnerTimeout = Date.now();
  }
  function hideSpinner() {
    const s = document.getElementById("phish-analyzer-spinner");
    if (!s) return;
    const elapsed = Date.now() - (spinnerTimeout || 0);
    if (elapsed < 800) {
      setTimeout(() => {
        if (s) s.remove();
      }, 800 - elapsed);
    } else {
      s.remove();
    }
  }

  // When user opens an email or uses extension action, extract and send to background
  async function analyzeCurrentEmail() {
    const data = getGmailMessageData();
    if (!data) {
      alert(
        "Could not extract email data. Please open an email and try again."
      );
      return;
    }
    showSpinner();
    // send to background (service worker) to forward to backend
    chrome.runtime.sendMessage(
      { type: "analyze_email", payload: data },
      (resp) => {
        hideSpinner();
        if (chrome.runtime.lastError) {
          showOverlay({
            final_risk: 0,
            label: "Error",
            llm_reason: chrome.runtime.lastError.message,
            llm_actions: [],
          });
          return;
        }
        if (!resp || resp.error) {
          showOverlay({
            final_risk: 0,
            label: "Error",
            llm_reason: resp?.error || "unknown",
            llm_actions: [],
          });
          return;
        }
        // show overlay with results
        showOverlay(resp.result || {});
      }
    );
  }

  // Add a small analyze button inside Gmail toolbar for convenience (idempotent)
  function attachAnalyzeButton() {
    // Try multiple selectors for Gmail toolbar
    const toolbars = [
      ...document.querySelectorAll('div[aria-label="More"]'),
      ...document.querySelectorAll("div.aU"),
      ...document.querySelectorAll('div[role="toolbar"]'),
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
    if (document.getElementById("phish-float-btn")) return;
    const floatBtn = document.createElement("button");
    floatBtn.id = "phish-float-btn";
    floatBtn.innerText = "Analyze";
    floatBtn.style.position = "fixed";
    floatBtn.style.right = "24px";
    floatBtn.style.bottom = "100px";
    floatBtn.style.zIndex = 2147483647;
    floatBtn.style.background = "#1976d2";
    floatBtn.style.color = "#fff";
    floatBtn.style.border = "none";
    floatBtn.style.borderRadius = "24px";
    floatBtn.style.padding = "12px 24px";
    floatBtn.style.boxShadow = "0 2px 8px rgba(0,0,0,0.18)";
    floatBtn.style.fontSize = "16px";
    floatBtn.style.cursor = "pointer";
    floatBtn.onclick = analyzeCurrentEmail;
    document.body.appendChild(floatBtn);
    // }
  }

  // Attempt to auto analyze when the DOM stabilizes (user opens mail)
  let lastHash = "";
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
