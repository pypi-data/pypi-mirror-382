# Copyright 2025 Amazon Inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from playwright.sync_api import Page

from nova_act.tools.browser.default.dom_actuation.scroll_events import get_after_scroll_events
from nova_act.tools.browser.default.util.bbox_parser import bounding_box_to_point, parse_bbox_string
from nova_act.tools.browser.default.util.dispatch_dom_events import dispatch_event_sequence
from nova_act.tools.browser.default.util.element_helpers import get_element_at_point, is_pdf_page, locate_element
from nova_act.tools.browser.interface.types.dimensions_dict import DimensionsDict
from nova_act.util.common_js_expressions import Expressions
from nova_act.util.logging import setup_logging

_LOGGER = setup_logging(__name__)


def get_target_bbox_dimensions(bounding_box: str | None) -> DimensionsDict | None:
    if bounding_box is None:
        return None
    bbox_dict = parse_bbox_string(bounding_box)

    dimensions: DimensionsDict = {
        "width": int(abs(bbox_dict["left"] - bbox_dict["right"])),
        "height": int(abs(bbox_dict["top"] - bbox_dict["bottom"])),
    }
    return dimensions


def get_scroll_element_dimensions(page: Page, bounding_box: str | None = None) -> DimensionsDict:
    # No bounding box means we want to scroll the window
    if bounding_box is None:
        dimensions: DimensionsDict = page.evaluate(
            """() => {
            return {
                width: document.documentElement.clientWidth,
                height: document.documentElement.clientHeight,
            }
            }"""
        )
        return dimensions

    bbox_dict = parse_bbox_string(bounding_box)
    point = bounding_box_to_point(bbox_dict)
    # The javascript code below does the following:
    # 1. gets all html elements at the given point
    # 2. Iterates through all elements
    # 3. Verifies if element is scrollable by attempting to scroll the element and checking
    # if the scroll value has changed (canScroll()).
    # 4. Returns the first element that is scrollable, otherwise returns the dimensions of
    # the page.
    dimensions = page.evaluate(
        """
        ([x, y]) => {
            const elems = document.elementsFromPoint(x, y);
            if (elems.length === 0) return null;
            function canScroll(el, scrollAxis) {
                if (0 === el[scrollAxis]) {
                    el[scrollAxis] = 1;
                    if (1 === el[scrollAxis]) {
                        el[scrollAxis] = 0;
                        return true;
                    }
                } else {
                    return true;
                }
                return false;
            }

            function isScrollableX(el) {
                return (el.scrollWidth > el.clientWidth) && canScroll(el, 'scrollLeft');
            }

            function isScrollableY(el) {
                return (el.scrollHeight > el.clientHeight) && canScroll(el, 'scrollTop');
            }

            function isScrollable(el) {
                return isScrollableX(el) || isScrollableY(el);
            }
            for (let elem of elems) {
                if (elem.tagName.toLowerCase() === 'body' || elem.tagName.toLowerCase() === 'html') {
                    continue;
                }
                if (elem.clientWidth > 0 && elem.clientHeight > 0 && isScrollable(elem)) {
                    return {
                        width: elem.clientWidth,
                        height: elem.clientHeight,
                    }
                }
            }
            return {
                width: document.documentElement.clientWidth,
                height: document.documentElement.clientHeight,
            }
        }
        """,
        [point["x"], point["y"]],
    )

    if dimensions is None:
        raise ValueError(f"Could not find element at point {point}.")

    return dimensions


def scroll(delta: float, direction: str, page: Page) -> None:
    if direction == "up":
        page.mouse.wheel(0, -delta)
    elif direction == "down":
        page.mouse.wheel(0, delta)
    elif direction == "left":
        page.mouse.wheel(-delta, 0)
    elif direction == "right":
        page.mouse.wheel(delta, 0)


def is_bounding_box_entire_page(bounding_box: str, visible_area_dimensions: DimensionsDict) -> bool:
    """Check if the bounding box is within 5 pixels of the entire page"""

    FULL_PAGE_PIXEL_THRESHOLD = 5

    bbox_dict = parse_bbox_string(bounding_box)
    return (
        bbox_dict["left"] <= FULL_PAGE_PIXEL_THRESHOLD
        and bbox_dict["top"] <= FULL_PAGE_PIXEL_THRESHOLD
        and bbox_dict["right"] >= visible_area_dimensions["width"] - FULL_PAGE_PIXEL_THRESHOLD
        and bbox_dict["bottom"] >= visible_area_dimensions["height"] - FULL_PAGE_PIXEL_THRESHOLD
    )


def agent_scroll(
    page: Page,
    direction: str,
    bounding_box: str | None = None,
    value: float | None = None,
) -> None:
    visible_area_dimensions = page.evaluate(Expressions.GET_VIEWPORT_SIZE.value)

    dimensions: DimensionsDict = {
        "width": visible_area_dimensions["width"],
        "height": visible_area_dimensions["height"],
    }
    bounding_box_entire_page: bool = False
    if bounding_box:
        bounding_box_entire_page = is_bounding_box_entire_page(bounding_box, visible_area_dimensions)

    if bounding_box and not bounding_box_entire_page:
        scroll_element_dimensions = get_scroll_element_dimensions(page, bounding_box)
        target_bbox_dimensions = get_target_bbox_dimensions(bounding_box)
        dimensions = scroll_element_dimensions

        # Compare with visible_area_dimensions
        dimensions["width"] = min(dimensions["width"], visible_area_dimensions["width"])
        dimensions["height"] = min(dimensions["height"], visible_area_dimensions["height"])

        # Compare with target_bbox_dimensions if it exists
        if target_bbox_dimensions is not None:
            dimensions["width"] = min(dimensions["width"], target_bbox_dimensions["width"])
            dimensions["height"] = min(dimensions["height"], target_bbox_dimensions["height"])

    delta = value
    if delta is None:
        if direction == "up" or direction == "down":
            delta = dimensions["height"] * 0.75
        elif direction == "left" or direction == "right":
            delta = dimensions["width"] * 0.75
        else:
            raise ValueError(f"Invalid direction {direction}")

    if bounding_box and not bounding_box_entire_page:
        bbox_dict = parse_bbox_string(bounding_box)
        point = bounding_box_to_point(bbox_dict)
        page.mouse.move(point["x"], point["y"])
        if is_pdf_page(page):
            # First click to focus the pdf.
            page.mouse.click(point["x"], point["y"])

    scroll(delta, direction, page)

    if bounding_box and not bounding_box_entire_page:
        bbox_dict = parse_bbox_string(bounding_box)

        try:
            point = bounding_box_to_point(bbox_dict)
            element_info = get_element_at_point(page, point["x"], point["y"])
            if element_info is None:
                return

            element = locate_element(element_info, page)

            after_scroll_events = get_after_scroll_events(point)

            dispatch_event_sequence(element, after_scroll_events)
        except Exception as e:
            _LOGGER.debug(f"Error dispatching after scroll events: {e}")
            # Catch all exceptions when dispatching after scroll events so react loop does not stop
            return
