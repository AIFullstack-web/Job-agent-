const DEFAULT_CONFIG = {
  apiBase: "http://127.0.0.1:8000",
  apiToken: "change-me"
};

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.set(DEFAULT_CONFIG);
});

chrome.action.onClicked.addListener(async (tab) => {
  const cfg = await chrome.storage.sync.get(["apiBase", "apiToken"]);
  const apiBase = cfg.apiBase || DEFAULT_CONFIG.apiBase;
  const apiToken = cfg.apiToken || DEFAULT_CONFIG.apiToken;

  if (!tab.url) return;

  await fetch(`${apiBase}/ingest/job-url`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Token": apiToken
    },
    body: JSON.stringify({ url: tab.url })
  });
});
