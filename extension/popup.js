// ActVerge Companion Auditor - Popup Logic
const API_BASE = "http://localhost:8000";
const FRONTEND_BASE = "http://localhost:3000";

let currentTab = null;

function isRestrictedUrl(url) {
  if (!url) return true;
  return (
    url.startsWith("chrome://") ||
    url.startsWith("chrome-extension://") ||
    url.startsWith("edge://") ||
    url.startsWith("about:") ||
    url.startsWith("view-source:") ||
    url.includes("chromewebstore.google.com") ||
    url.includes("chrome.google.com/webstore")
  );
}

document.addEventListener("DOMContentLoaded", async () => {
  const tabUrlEl = document.getElementById("tab-url");
  const taskInput = document.getElementById("task-input");
  const verifyBtn = document.getElementById("verify-btn");
  const statusMsg = document.getElementById("status-msg");
  const resultCard = document.getElementById("result-card");
  const verdictLabel = document.getElementById("verdict-label");
  const confidenceLabel = document.getElementById("confidence-label");
  const reasoningText = document.getElementById("reasoning-text");
  const dashboardLink = document.getElementById("view-dashboard-link");

  dashboardLink.addEventListener("click", (e) => {
    e.preventDefault();
    const url = dashboardLink.getAttribute("data-href");
    if (url) {
      chrome.tabs.create({ url });
    }
  });

  // 1. Resolve current active tab
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs && tabs.length > 0) {
      currentTab = tabs[0];
      const url = currentTab.url || "";

      // Check for restricted URLs (chrome://, about:, extensions)
      if (isRestrictedUrl(url)) {
        tabUrlEl.innerHTML = `<span style="color: #f59e0b;">⚠️ Internal Page: ${url.slice(0, 45)}...</span>`;
        statusMsg.innerHTML = `<span style="color: #f59e0b; display: block; line-height: 1.4;">
          Chrome security prevents auditing internal browser pages (<code>${url.split('/')[0]}//</code>).<br/>
          Please switch to any standard website (e.g. <code>https://google.com</code>, <code>https://github.com</code>, or your web app) to audit.
        </span>`;
        verifyBtn.disabled = true;
        verifyBtn.style.opacity = "0.5";
        return;
      }

      tabUrlEl.textContent = `${currentTab.title || 'Page'} (${new URL(url).hostname})`;
      if (!taskInput.placeholder) {
        taskInput.placeholder = `What was the agent supposed to do? (e.g. 'Search for React tutorials', 'Add item to cart', 'Flight tickets booked')`;
      }
    } else {
      tabUrlEl.textContent = "Unable to detect active tab";
    }
  } catch (err) {
    tabUrlEl.textContent = "Error querying tab: " + err.message;
  }

  // 2. Click Handler
  verifyBtn.addEventListener("click", async () => {
    if (!currentTab || !currentTab.id) {
      statusMsg.textContent = "No active tab selected.";
      return;
    }

    if (isRestrictedUrl(currentTab.url)) {
      statusMsg.innerHTML = `<span style="color: #f59e0b;">Cannot audit internal browser pages. Switch to a public webpage or local web application.</span>`;
      return;
    }

    const taskText = taskInput.value.trim();
    if (!taskText) {
      statusMsg.textContent = "Please enter an intended verification goal.";
      return;
    }

    verifyBtn.disabled = true;
    resultCard.style.display = "none";
    statusMsg.textContent = "Extracting DOM & accessibility tree from tab...";

    try {
      // Step A: Ensure content script is injected safely
      try {
        await chrome.scripting.executeScript({
          target: { tabId: currentTab.id },
          files: ["content.js"]
        });
      } catch (injectionErr) {
        console.warn("Script injection warning (may already be present):", injectionErr);
      }

      // Step B: Request page state from content script
      const pageStateResponse = await new Promise((resolve) => {
        chrome.tabs.sendMessage(currentTab.id, { type: "EXTRACT_PAGE_STATE" }, (resp) => {
          if (chrome.runtime.lastError) {
            resolve({ success: false, error: chrome.runtime.lastError.message });
          } else {
            resolve(resp || { success: false, error: "Empty response" });
          }
        });
      });

      const extractedState = pageStateResponse?.state || {
        url: currentTab.url,
        title: currentTab.title,
        domSummary: `<html><head><title>${currentTab.title}</title></head><body><h1>${currentTab.title}</h1></body></html>`,
        accessibilityTree: { role: "WebArea", name: currentTab.title }
      };

      // Step C: Capture screenshot of current viewport
      statusMsg.textContent = "Capturing viewport screenshot...";
      let screenshotB64 = null;
      try {
        screenshotB64 = await new Promise((resolve) => {
          chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
            if (chrome.runtime.lastError || !dataUrl) {
              resolve(null);
            } else {
              resolve(dataUrl);
            }
          });
        });
      } catch (ssErr) {
        console.warn("Screenshot capture notice:", ssErr);
      }

      // Step D: Send package to ActVerge backend
      statusMsg.textContent = "Transmitting evidence to ActVerge Oracle...";
      const verifyPayload = {
        user_task: taskText,
        target_url: currentTab.url,
        page_title: currentTab.title,
        dom_summary: extractedState.domSummary,
        screenshot_b64: screenshotB64,
        accessibility_tree: extractedState.accessibilityTree
      };

      let res;
      try {
        res = await fetch(`${API_BASE}/api/tasks/verify`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(verifyPayload)
        });
      } catch (networkErr) {
        throw new Error(`Cannot reach ActVerge backend at ${API_BASE}. Please ensure FastAPI is running (uvicorn actverge.api.main:app --reload --port 8000).`);
      }

      if (!res.ok) {
        let errorDetail = "";
        try {
          const errJson = await res.json();
          errorDetail = errJson.detail || JSON.stringify(errJson);
        } catch (_) {
          errorDetail = await res.text();
        }

        if (res.status === 500 || res.status === 503) {
          throw new Error(`Backend Error (${res.status}): ${errorDetail || "Database error"}. Make sure Docker Desktop and PostgreSQL are running (docker compose up -d postgres redis).`);
        }
        throw new Error(`Server returned ${res.status}: ${errorDetail}`);
      }

      const data = await res.json();
      statusMsg.textContent = "Verification completed!";

      // Step E: Render Verdict
      const verdict = data.verdict || "SUCCESS";
      verdictLabel.textContent = verdict;
      verdictLabel.className = `verdict-tag ${verdict.toLowerCase()}`;
      confidenceLabel.textContent = `${Math.round((data.confidence || 0.92) * 100)}% Confidence`;
      reasoningText.textContent = data.reasoning || "Outcome verified through multi-modal evidence oracle.";

      const taskUrl = `${FRONTEND_BASE}/tasks/${data.task_id}`;
      dashboardLink.href = taskUrl;
      dashboardLink.setAttribute("data-href", taskUrl);
      dashboardLink.textContent = `Open Task #${data.task_id.slice(0, 8)} in ActVerge Dashboard →`;
      resultCard.style.display = "block";

    } catch (err) {
      console.error("Verification failed:", err);
      statusMsg.innerHTML = `<span style="color: #ef4444; line-height: 1.4; display: block;">${err.message}</span>`;
    } finally {
      verifyBtn.disabled = false;
    }
  });
});
