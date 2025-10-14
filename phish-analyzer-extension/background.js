const FIXED_BACKEND_URL = "http://127.0.0.1:8080/analyze";

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "analyze_email") {
    handleAnalyze(msg.payload)
      .then((result) => sendResponse({ result }))
      .catch((err) => sendResponse({ error: err.message }));
    return true; // keep channel open
  }
});

async function handleAnalyze(payload) {
  const storage = await chrome.storage.local.get(["apiKey", "sendFullBody"]);
  const apiKey = storage.apiKey || "";
  const sendFullBody =
    storage.sendFullBody === undefined ? true : storage.sendFullBody;

  const reqBody = {
    sender: payload.sender,
    subject: payload.subject,
    body: sendFullBody ? payload.body : "",
    urls: payload.urls || [],
    privacy_minimized: !sendFullBody,
  };

  const resp = await fetch(FIXED_BACKEND_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify(reqBody),
  });
  if (!resp.ok) throw new Error("Backend error: " + resp.statusText);
  const data = await resp.json();

  const result = {
    final_risk: data.final_risk,
    llm_reason: data.llm_reason || "",
    llm_actions: data.llm_actions || data.actions || [],
  };
  result.label =
    result.final_risk < 0.3
      ? "Safe"
      : result.final_risk < 0.6
      ? "Suspicious"
      : "Likely Phishing";
  return result;
}
