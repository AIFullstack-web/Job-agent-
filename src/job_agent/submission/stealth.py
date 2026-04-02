from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass

from job_agent.schemas.fill_plan import FillPlan

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class StealthExecutor:
    cdp_url: str
    headless: bool = False

    def submit(self, fill_plan: FillPlan) -> None:
        """Execute browser submission flow with UC mode and human mimicry."""
        from seleniumbase import SB

        self._connect_browser_use_over_cdp()
        with SB(uc=True, headless=self.headless) as sb:
            self._navigate(sb, fill_plan.job_url)
            self._maybe_handle_turnstile(sb)
            self._semantic_fill(sb, fill_plan)
            if fill_plan.submit_after_fill:
                self._submit_form(sb)

    def _connect_browser_use_over_cdp(self) -> None:
        from browser_use import Browser

        Browser.connect_over_cdp(self.cdp_url)

    def _navigate(self, sb, url: str) -> None:
        logger.info("Navigating to %s", url)
        sb.open(url)
        self._human_pause(0.8, 1.9)

    def _maybe_handle_turnstile(self, sb) -> None:
        try:
            sb.uc_gui_click_captcha()
            self._human_pause(0.7, 1.4)
        except Exception:
            logger.info("No interactive captcha click needed")

    def _semantic_fill(self, sb, fill_plan: FillPlan) -> None:
        for action in fill_plan.actions:
            self._non_linear_mouse_move()
            self._fill_action(sb, action.label, action.value, action.field_type)
            self._human_pause(0.1, 0.5)

    def _fill_action(self, sb, label: str, value: str, field_type: str) -> None:
        xpath_base = (
            f"//label[contains(normalize-space(), '{label}')]/"
            "following::input[1] | //label[contains(normalize-space(), '{label}')]/following::textarea[1]"
        )
        if field_type in {"text", "textarea", "date"}:
            sb.type(xpath_base, "")
            self._type_with_human_delay(sb, value)
        elif field_type == "select":
            sb.select_option_by_text(xpath_base, value)
        elif field_type == "file":
            sb.choose_file(xpath_base, value)
        elif field_type in {"checkbox", "radio"}:
            if str(value).lower() in {"true", "yes", "1"}:
                sb.click(xpath_base)

    def _submit_form(self, sb) -> None:
        sb.click("button[type='submit'], input[type='submit']")
        self._human_pause(0.8, 1.6)

    def _type_with_human_delay(self, sb, text: str) -> None:
        for ch in text:
            sb.send_keys(ch)
            time.sleep(random.uniform(0.05, 0.2))

    def _non_linear_mouse_move(self) -> None:
        self._human_pause(0.02, 0.08)

    @staticmethod
    def _human_pause(minimum: float, maximum: float) -> None:
        time.sleep(random.uniform(minimum, maximum))
