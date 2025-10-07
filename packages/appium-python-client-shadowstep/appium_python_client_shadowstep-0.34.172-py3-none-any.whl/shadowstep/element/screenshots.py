"""Element screenshots module for Shadowstep framework.

This module provides screenshot functionality for elements,
including base64 encoding, PNG format, and file saving capabilities.
"""
import logging
import time
import traceback
from typing import TYPE_CHECKING

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)

from shadowstep.decorators.decorators import log_debug
from shadowstep.exceptions.shadowstep_exceptions import ShadowstepElementException

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.element.utilities import ElementUtilities
    from shadowstep.locator import LocatorConverter
    from shadowstep.shadowstep import Shadowstep


class ElementScreenshots:
    """Element screenshots handler for Shadowstep framework."""

    def __init__(self, element: "Element") -> None:
        """Initialize ElementScreenshots.

        Args:
            element: The element to take screenshots from.

        """
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def screenshot_as_base64(self) -> str:
        """Get the screenshot of the current element as a base64 encoded string.

        Returns:
            str: Base64-encoded screenshot string.

        """
        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()

                current_element = self.element.get_native()

                return current_element.screenshot_as_base64  # noqa: TRY300

            except NoSuchDriverException as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to get screenshot_as_base64 within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def screenshot_as_png(self) -> bytes:
        """Get the screenshot of the current element as binary data.

        Returns:
            bytes: PNG-encoded screenshot bytes.

        """
        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()

                current_element = self.element.get_native()

                return current_element.screenshot_as_png  # noqa: TRY300

            except NoSuchDriverException as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to get screenshot_as_png within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )

    @log_debug()
    def save_screenshot(self, filename: str) -> bool:
        """Save a screenshot of the current element to a PNG image file.

        Args:
            filename: The full path to save the screenshot. Should end with `.png`.

        Returns:
            True if successful, False otherwise.

        """
        start_time = time.time()

        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()

                current_element = self.element.get_native()

                return current_element.screenshot(filename)  # type: ignore[reportUnknownMemberType]

            except NoSuchDriverException as error:  # noqa: PERF203
                self.element.utilities.handle_driver_error(error)
            except InvalidSessionIdException as error:
                self.element.utilities.handle_driver_error(error)
            except AttributeError as error:
                self.element.utilities.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException\nRe-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except OSError:
                self.logger.exception("IOError while saving screenshot to %s", filename)
                return False
            except WebDriverException as error:
                self.element.utilities.handle_driver_error(error)

        raise ShadowstepElementException(
            msg=f"Failed to save screenshot to {filename} within {self.element.timeout=}",
            stacktrace=traceback.format_stack(),
        )
