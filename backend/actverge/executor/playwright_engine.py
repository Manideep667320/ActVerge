import asyncio
import base64
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from actverge.core.config import settings

logger = logging.getLogger("actverge.playwright_engine")

class PlaywrightEngine:
    """
    Real Playwright Browser Automation & Observation Engine.
    Executes real browser actions in headed or headless Chromium,
    intercepts live CDP network/console/AOM events, and captures
    real post-action multi-modal evidence.
    """

    def __init__(self, headless: Optional[bool] = None):
        self.headless = headless if headless is not None else settings.PLAYWRIGHT_HEADLESS

    async def execute_task_steps(
        self,
        task: str,
        actions: List[Dict[str, Any]],
        initial_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a sequence of browser actions on a live Chromium instance.
        Returns captured multi-modal evidence (DOM, screenshot, console logs, network events, AOM).
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            logger.warning(f"Playwright package not available: {e}")
            return {"success": False, "error": "Playwright is not installed"}

        console_logs: List[Dict[str, Any]] = []
        network_events: List[Dict[str, Any]] = []
        executed_trace: List[Dict[str, Any]] = []

        now = datetime.utcnow().isoformat()
        logger.info(f"Starting Playwright session (headless={self.headless}) for task: '{task[:50]}'")

        try:
            async with async_playwright() as p:
                browser = None
                try:
                    browser = await p.chromium.launch(
                        channel="msedge",
                        headless=self.headless,
                        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
                    )
                except Exception as edge_err:
                    logger.info(f"Edge channel launch failed ({edge_err}); attempting default chromium launch")
                    browser = await p.chromium.launch(
                        headless=self.headless,
                        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
                    )
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
                )
                page = await context.new_page()

                # Wire CDP Event Listeners
                page.on("console", lambda msg: console_logs.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": msg.type.upper() if msg.type != "log" else "INFO",
                    "text": msg.text[:300],
                    "source": "browser_console"
                }))

                page.on("request", lambda req: network_events.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": req.method,
                    "url": req.url[:150],
                    "resource_type": req.resource_type,
                    "status": 0
                }))

                page.on("response", lambda res: network_events.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": res.request.method,
                    "url": res.url[:150],
                    "status": res.status,
                    "content_type": res.headers.get("content-type", "text/plain")[:50]
                }))

                # Step through action sequence
                for step in actions:
                    action_type = step.get("action", "").lower()
                    target = step.get("target") or ""
                    value = step.get("value")
                    step_now = datetime.utcnow().isoformat()
                    step_result = "executed"

                    try:
                        if action_type == "navigate":
                            url_to_go = target if target.startswith("http") else f"https://{target}"
                            await page.goto(url_to_go, wait_until="domcontentloaded", timeout=12000)
                            step_result = f"Navigated to {page.url}"

                        elif action_type == "fill":
                            if target:
                                await page.fill(target, str(value or ""), timeout=5000)
                                step_result = f"Filled '{target}' with value"
                            else:
                                step_result = "Target selector omitted"

                        elif action_type == "press_key":
                            key = str(value or "Enter")
                            if target:
                                await page.press(target, key, timeout=5000)
                            else:
                                await page.keyboard.press(key)
                            step_result = f"Pressed key '{key}'"

                        elif action_type == "click":
                            if target:
                                await page.click(target, timeout=5000)
                                step_result = f"Clicked '{target}'"
                            else:
                                step_result = "Click target omitted"

                        elif action_type == "hover":
                            if target:
                                await page.hover(target, timeout=5000)
                                step_result = f"Hovered over '{target}'"

                        elif action_type == "select":
                            if target:
                                await page.select_option(target, value=str(value), timeout=5000)
                                step_result = f"Selected option '{value}' on '{target}'"

                        elif action_type == "scroll":
                            await page.evaluate("window.scrollBy(0, 400)")
                            step_result = "Scrolled viewport down 400px"

                        elif action_type == "wait":
                            # Parse timeout ms e.g. "2000ms" or 2000
                            ms = 1500
                            if value:
                                match = re.search(r"(\d+)", str(value))
                                if match:
                                    ms = min(int(match.group(1)), 5000)
                            await page.wait_for_timeout(ms)
                            step_result = f"Waited {ms}ms"

                        elif action_type == "screenshot":
                            step_result = "Captured viewport frame"

                        elif action_type == "observe":
                            step_result = f"Observed page state at {page.url}"

                    except Exception as step_err:
                        logger.warning(f"Playwright step {step.get('step')} ({action_type}) failed: {step_err}")
                        step_result = f"Failed: {str(step_err)[:100]}"

                    executed_trace.append({
                        "step": step.get("step", len(executed_trace) + 1),
                        "action": action_type,
                        "target": target,
                        "value": value,
                        "result": step_result,
                        "timestamp": step_now
                    })

                # Allow dynamic animations or network idle to settle
                await page.wait_for_timeout(800)

                # Capture post-action state
                page_title = await page.title()
                final_url = page.url
                raw_html = await page.content()

                # Clean DOM summary (first 5000 chars of body)
                body_match = re.search(r"<body[^>]*>(.*?)</body>", raw_html, re.DOTALL | re.IGNORECASE)
                dom_summary = (body_match.group(0)[:4000] + "...") if body_match else raw_html[:4000]

                # Capture high-fidelity viewport screenshot
                img_bytes = await page.screenshot(type="png", full_page=False)
                screenshot_data_uri = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"

                # Capture accessibility tree
                try:
                    aom = await page.accessibility.snapshot()
                except Exception:
                    aom = {"role": "WebArea", "name": page_title}

                await browser.close()

                return {
                    "success": True,
                    "target_url": final_url,
                    "page_title": page_title,
                    "dom_summary": dom_summary,
                    "screenshot_data_uri": screenshot_data_uri,
                    "accessibility_tree": aom or {"role": "WebArea", "name": page_title},
                    "console_logs": console_logs,
                    "network_events": network_events,
                    "action_trace": executed_trace
                }

        except Exception as e:
            logger.error(f"Playwright execution error: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def is_available() -> bool:
        """Returns True if Playwright is importable in the current environment."""
        try:
            import playwright
            return True
        except ImportError:
            return False
