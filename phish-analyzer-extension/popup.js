document.addEventListener("DOMContentLoaded", async () => {
  // Load existing settings
  const settings = await chrome.storage.local.get([
    "apiKey",
    "sendFullBody",
    "enableBlockchain",
  ]);
  document.getElementById("apiKey").value = settings.apiKey || "";
  document.getElementById("sendFullBody").checked =
    settings.sendFullBody === undefined ? true : settings.sendFullBody;
  document.getElementById("enableBlockchain").checked =
    settings.enableBlockchain === undefined ? true : settings.enableBlockchain;

  // Check blockchain status on load
  checkBlockchainStatus();

  // Save preferences
  document.getElementById("save").onclick = async () => {
    const apiKey = document.getElementById("apiKey").value;
    const sendFullBody = document.getElementById("sendFullBody").checked;
    const enableBlockchain =
      document.getElementById("enableBlockchain").checked;

    await chrome.storage.local.set({ apiKey, sendFullBody, enableBlockchain });
    document.getElementById("status").innerText = "✅ Settings saved!";
    setTimeout(() => (document.getElementById("status").innerText = ""), 2000);
  };

  // Refresh blockchain status
  document.getElementById("refreshStatus").onclick = () => {
    checkBlockchainStatus();
  };
});

async function checkBlockchainStatus() {
  const statusElement = document.getElementById("blockchainStatus");
  const detailsElement = document.getElementById("blockchainDetails");

  // Show loading state
  statusElement.innerHTML = `
    <div style="display: flex; align-items: center;">
      <span class="status-indicator status-unknown"></span>
      <span>Checking connection...</span>
    </div>
  `;
  detailsElement.textContent = "Connecting to backend...";

  try {
    // Get API key for authentication
    const settings = await chrome.storage.local.get(["apiKey"]);

    // Check blockchain status via backend
    const response = await fetch("http://localhost:8080/blockchain/status", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...(settings.apiKey && { "x-api-key": settings.apiKey }),
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const status = await response.json();

    // Update UI based on status
    if (status.connected) {
      statusElement.innerHTML = `
        <div style="display: flex; align-items: center;">
          <span class="status-indicator status-connected"></span>
          <span>Connected to blockchain</span>
        </div>
      `;

      detailsElement.innerHTML = `
        <div>Network ID: ${status.network_id || "Unknown"}</div>
        <div>Contract: ${
          status.contract_address ? "✅ Deployed" : "❌ Not deployed"
        }</div>
        <div>Account: ${
          status.account_address ? "✅ Configured" : "❌ Not configured"
        }</div>
      `;
    } else {
      statusElement.innerHTML = `
        <div style="display: flex; align-items: center;">
          <span class="status-indicator status-disconnected"></span>
          <span>Blockchain offline</span>
        </div>
      `;

      detailsElement.innerHTML = `
        <div>Provider: ${status.provider_url || "Not configured"}</div>
        <div>ML/AI analysis only</div>
      `;
    }
  } catch (error) {
    console.error("Failed to check blockchain status:", error);

    statusElement.innerHTML = `
      <div style="display: flex; align-items: center;">
        <span class="status-indicator status-disconnected"></span>
        <span>Backend unavailable</span>
      </div>
    `;

    detailsElement.innerHTML = `
      <div>Error: ${error.message}</div>
      <div>Check if backend is running on port 8080</div>
    `;
  }
}
