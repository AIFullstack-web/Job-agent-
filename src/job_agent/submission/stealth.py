from __future__ import annotations

import random
import time
from dataclasses import dataclass

from job_agent.schemas.fill_plan import FillPlan


@dataclass(slots=True)
class StealthExecutor:
    cdp_url: str
    headless: bool = False

    def submit(self, fill_plan: FillPlan) -> None:
        """
        Executes the browser submission flow with UC mode and human mimicry.

        Requires runtime dependencies:
        - seleniumbase
        - browser-use
        """
        sb = self._build_uc_driver()
        self._connect_browser_use_over_cdp()
        self._navigate(sb, fill_plan.job_url)
        self._maybe_handle_turnstile(sb)
        self._semantic_fill(sb, fill_plan)

    def _build_uc_driver(self):
        from seleniumbase import SB

        return SB(uc=True, headless=self.headless)

    def _connect_browser_use_over_cdp(self) -> None:
        from browser_use import Browser

        Browser.connect_over_cdp(self.cdp_url)

    def _navigate(self, sb, url: str) -> None:
        sb.open(url)
        self._human_pause(0.8, 1.9)

    def _maybe_handle_turnstile(self, sb) -> None:
        sb.uc_gui_click_captcha()
        self._human_pause(0.7, 1.4)

    def _semantic_fill(self, sb, fill_plan: FillPlan) -> None:
        for action in fill_plan.actions:
            self._non_linear_mouse_move()
            selector = f"label:contains('{action.label}')"
            sb.click(selector)
            self._type_with_human_delay(sb, action.value)
            self._human_pause(0.1, 0.5)

    def _type_with_human_delay(self, sb, text: str) -> None:
        for ch in text:
            sb.send_keys(ch)
            time.sleep(random.uniform(0.05, 0.2))

    def _non_linear_mouse_move(self) -> None:
        # Placeholder hook for richer trajectories.
        self._human_pause(0.02, 0.08)

    @staticmethod
    def _human_pause(minimum: float, maximum: float) -> None:
        time.sleep(random.uniform(minimum, maximum))
