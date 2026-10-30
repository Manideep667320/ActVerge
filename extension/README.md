# ActVerge Companion Auditor (Chrome Extension)

[![Manifest V3](https://img.shields.io/badge/Chrome%20Extension-Manifest%20V3-4285F4?logo=googlechrome&logoColor=white)](https://developer.chrome.com/docs/extensions/mv3/intro/)
[![ActVerge Oracle](https://img.shields.io/badge/ActVerge-Oracle%20Compatible-06b6d4)](http://localhost:3000)

A non-invasive Manifest V3 companion extension for ActVerge that turns any active Chrome tab into a verifiable digital state. It serves as an independent, multi-modal oracle for **external browser agents** (Gemini in Google Workspace, Claude Computer Use, OpenAI Operator, Browser-Use) and human digital workflows.

---

## 🌟 Key Features

1. **One-Click Ground-Truth Extraction**:
   - Captures clean semantic DOM summaries (headings, inputs with values, button labels, alerts, card listings).
   - Generates an accessibility hierarchy (AOM approximation) to evaluate screen-reader visible landmarks.
   - Captures high-resolution viewport screenshots.
2. **Intent-Aware Outcome Verification**:
   - Transmits multi-modal evidence directly to the ActVerge backend (`POST /api/tasks/verify`).
   - Evaluates whether an agent genuinely accomplished the task or merely hallucinated success.
   - Distinguishes **Creator / Authoring** tasks (e.g. building a form with Gemini) from **Respondent / Submission** tasks.
3. **Instant Visual Feedback**:
   - Displays real-time verdict (`SUCCESS`, `PARTIAL`, `FAILED`), confidence score (0-100%), and factual reasoning citing specific DOM elements.
   - Provides a direct link to open the task in the ActVerge Next.js Dashboard (`http://localhost:3000/tasks/{id}`).

---

## 🛠️ Installation Instructions

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable the **Developer mode** toggle in the top-right corner.
3. Click **Load unpacked** in the top-left corner.
4. Select the `extension` directory from this repository:
   ```
   C:\Users\manid\Desktop\ActVerge\extension
   ```
5. Pin the **ActVerge Auditor** icon to your Chrome toolbar.

---

## 🚀 How to Use

1. Ensure the ActVerge backend is running:
   ```powershell
   cd backend
   uvicorn actverge.api.main:app --port 8000 --reload
   ```
2. In Chrome, open any web application where an AI agent or user is performing work (e.g., Google Forms, GitHub, Jira, Amazon).
3. Click the **ActVerge Auditor** icon in your toolbar.
4. Enter the intended task description (e.g., *"Create a 3-question Customer Feedback Form in Google Forms using Gemini"*).
5. Click **Audit & Verify Tab**.
6. Review the verdict and click **Open Full Evidence in ActVerge Dashboard →** to inspect the live DOM snapshot and network logs.

---

## 🧪 Benchmark Test Scenarios

| Scenario | Webpage URL | Goal Description | Expected Verdict |
| :--- | :--- | :--- | :---: |
| **1. Genuine Success** | `https://playwright.dev/python/docs/intro` | *"Find the Playwright Python installation command"* | **`SUCCESS`** (95%) |
| **2. Hallucination Intercepted** | `https://github.com` | *"Book a one-way flight from New York to Tokyo"* | **`FAILED`** (100%) |
| **3. Unsubmitted Draft** | `https://www.google.com` (Type query in input, don't press Enter) | *"Search for mechanical keyboards and view listings"* | **`PARTIAL`** (90%) |

---

## 🔒 Security & Privacy
- **Restricted URL Guard**: Automatically prevents script injection on internal browser URLs (`chrome://`, `chrome-extension://`, `about:`).
- **Ephemeral Audits**: Transmits DOM and screenshot evidence solely to your local ActVerge server (`localhost:8000`).
