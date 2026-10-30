// ActVerge Companion Auditor Content Script
// Extracts live page DOM structure, interactive state, and accessibility tree

(function () {
  // Capture unhandled page errors if possible
  const capturedErrors = [];
  window.addEventListener("error", (e) => {
    capturedErrors.push({
      level: "ERROR",
      message: `${e.message} at ${e.filename}:${e.lineno}`,
      timestamp: new Date().toISOString()
    });
  });

  // Listen for extraction requests from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "EXTRACT_PAGE_STATE") {
      try {
        const state = extractPageState();
        sendResponse({ success: true, state });
      } catch (err) {
        sendResponse({ success: false, error: err.toString() });
      }
    }
    return true; // Keep message channel open for async response
  });

  function extractPageState() {
    const url = window.location.href;
    const title = document.title || "";
    
    // Extract key headings
    const headings = Array.from(document.querySelectorAll("h1, h2, h3, h4"))
      .slice(0, 20)
      .map(h => `<${h.tagName.toLowerCase()}>${h.innerText.trim().slice(0, 100)}</${h.tagName.toLowerCase()}>`)
      .join("\n");

    // Extract interactive form controls & current values
    const inputs = Array.from(document.querySelectorAll("input, textarea, select"))
      .slice(0, 30)
      .map(el => {
        const type = el.getAttribute("type") || "text";
        const name = el.getAttribute("name") || el.getAttribute("id") || el.getAttribute("aria-label") || "";
        const val = el.value || el.placeholder || "";
        return `<${el.tagName.toLowerCase()} type="${type}" name="${name}" value="${val.slice(0, 80)}"/>`;
      })
      .join("\n");

    // Extract clickable buttons & actions
    const buttons = Array.from(document.querySelectorAll("button, a[role='button'], input[type='submit']"))
      .slice(0, 25)
      .map(b => `<button aria-label="${b.getAttribute('aria-label') || ''}">${b.innerText.trim().slice(0, 60)}</button>`)
      .join("\n");

    // Extract alerts, notices, toasts, confirmation banners
    const alerts = Array.from(document.querySelectorAll("[role='alert'], [role='status'], .alert, .notice, .success, .error, .toast, .banner, .badge"))
      .slice(0, 10)
      .map(a => `<div class="status-indicator">${a.innerText.trim().slice(0, 200)}</div>`)
      .join("\n");

    // Extract article or list item previews (e.g. search results, repo items, flight cards)
    const listItems = Array.from(document.querySelectorAll("article, .item, [role='listitem'], li, .result, .card"))
      .slice(0, 15)
      .map(item => `<div class="item-summary">${item.innerText.replace(/\s+/g, " ").trim().slice(0, 150)}</div>`)
      .join("\n");

    // Clean body text preview (up to 4000 characters of meaningful content)
    const textPreview = (document.body.innerText || "").replace(/\s+/g, " ").trim().slice(0, 4000);

    const domSummary = `
<main data-url="${url}">
  <header>
    <title>${title}</title>
  </header>
  <section class="status-alerts">
    ${alerts || "<!-- No active alerts or confirmations -->"}
  </section>
  <section class="headings">
    ${headings}
  </section>
  <section class="interactive-controls">
    ${inputs}
    ${buttons}
  </section>
  <section class="key-items-and-results">
    ${listItems || "<!-- No list items or cards detected -->"}
  </section>
  <section class="body-text-content">
    <p>${textPreview}</p>
  </section>
</main>
`.trim();

    // Accessibility tree approximation
    const accessibilityTree = {
      role: "WebArea",
      name: title,
      children: [
        {
          role: "heading",
          name: document.querySelector("h1")?.innerText?.trim() || title,
          level: 1
        },
        ...Array.from(document.querySelectorAll("button, a[href], input"))
          .slice(0, 15)
          .map(el => ({
            role: el.tagName === "BUTTON" ? "button" : (el.tagName === "INPUT" ? "textbox" : "link"),
            name: el.innerText?.trim() || el.getAttribute("aria-label") || el.getAttribute("placeholder") || "Interactive Item"
          }))
      ]
    };

    // Storage summary
    let storageKeys = [];
    try {
      storageKeys = Object.keys(localStorage).slice(0, 20);
    } catch (_) {}

    return {
      url,
      title,
      domSummary,
      accessibilityTree,
      storageKeyCount: storageKeys.length,
      storageKeys,
      capturedErrors
    };
  }
})();
