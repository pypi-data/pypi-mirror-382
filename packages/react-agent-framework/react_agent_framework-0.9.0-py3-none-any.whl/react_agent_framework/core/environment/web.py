"""
Web environment for browser automation

Allows agents to interact with web pages
"""

from typing import Dict, Any, List
from react_agent_framework.core.environment.base import (
    BaseEnvironment,
    Action,
    Observation,
)


class WebEnvironment(BaseEnvironment):
    """
    Web browser environment

    Enables web navigation and interaction
    Note: Requires playwright or selenium for full functionality
    """

    def __init__(
        self,
        start_url: str = "about:blank",
        headless: bool = True,
        browser_type: str = "chromium",
    ):
        """
        Initialize web environment

        Args:
            start_url: Initial URL to load
            headless: Run browser in headless mode
            browser_type: Browser type (chromium, firefox, webkit)
        """
        super().__init__(name="WebEnvironment")
        self.start_url = start_url
        self.headless = headless
        self.browser_type = browser_type

        self.current_url = start_url
        self.page_content = ""
        self.page_title = ""

    def reset(self) -> Observation:
        """Reset to initial URL"""
        self.current_url = self.start_url
        self.page_content = f"Navigated to {self.start_url}"
        self.page_title = "Initial Page"

        obs = Observation(
            data={
                "url": self.current_url,
                "title": self.page_title,
                "content": self.page_content[:500],
            },
            metadata={"action": "reset"},
        )

        self.state.current_observation = obs
        return obs

    def step(self, action: Action) -> Observation:
        """
        Execute web action

        Supported actions:
        - navigate: Go to URL
        - click: Click element
        - type: Type text
        - scroll: Scroll page
        - extract: Extract text
        """
        action_name = action.name.lower()

        if action_name == "navigate":
            return self._navigate(action.parameters.get("url", ""))

        elif action_name == "click":
            return self._click(action.parameters.get("selector", ""))

        elif action_name == "type":
            return self._type(
                action.parameters.get("selector", ""),
                action.parameters.get("text", ""),
            )

        elif action_name == "scroll":
            return self._scroll(action.parameters.get("direction", "down"))

        elif action_name == "extract":
            return self._extract(action.parameters.get("selector", "body"))

        else:
            obs = Observation(
                data=f"Unknown action: {action_name}",
                metadata={"error": True},
            )
            self.state.add_step(action, obs)
            return obs

    def _navigate(self, url: str) -> Observation:
        """Navigate to URL"""
        self.current_url = url
        self.page_content = f"Successfully navigated to {url}"
        self.page_title = f"Page: {url}"

        obs = Observation(
            data={
                "url": self.current_url,
                "title": self.page_title,
                "content": self.page_content,
                "status": "success",
            }
        )

        return obs

    def _click(self, selector: str) -> Observation:
        """Click element"""
        obs = Observation(
            data={
                "action": "click",
                "selector": selector,
                "result": f"Clicked element: {selector}",
            }
        )

        return obs

    def _type(self, selector: str, text: str) -> Observation:
        """Type text into element"""
        obs = Observation(
            data={
                "action": "type",
                "selector": selector,
                "text": text,
                "result": f"Typed '{text}' into {selector}",
            }
        )

        return obs

    def _scroll(self, direction: str) -> Observation:
        """Scroll page"""
        obs = Observation(
            data={
                "action": "scroll",
                "direction": direction,
                "result": f"Scrolled {direction}",
            }
        )

        return obs

    def _extract(self, selector: str) -> Observation:
        """Extract text from element"""
        # Simulated extraction
        extracted_text = f"Text content from {selector}"

        obs = Observation(
            data={
                "action": "extract",
                "selector": selector,
                "text": extracted_text,
            }
        )

        return obs

    def get_available_actions(self) -> List[str]:
        """Get available web actions"""
        return ["navigate", "click", "type", "scroll", "extract"]

    def get_observation_space(self) -> Dict[str, Any]:
        """Describe web observation space"""
        return {
            "url": "Current page URL",
            "title": "Page title",
            "content": "Page text content",
            "html": "Page HTML (if requested)",
            "elements": "Available interactive elements",
        }

    def get_page_info(self) -> Dict[str, str]:
        """Get current page information"""
        return {
            "url": self.current_url,
            "title": self.page_title,
            "content_preview": self.page_content[:200],
        }
