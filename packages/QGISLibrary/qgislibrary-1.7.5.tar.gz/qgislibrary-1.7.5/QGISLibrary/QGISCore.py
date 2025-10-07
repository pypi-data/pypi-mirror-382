from time import sleep
from typing import Any
from pywinauto import mouse
from pywinauto.keyboard import send_keys
from pyautogui import position
from pywinauto.application import Application
import logging
# from pywinauto.timings import Timings

# Timings.window_find_timeout = 60
logging.disable(logging.CRITICAL) if False else logging.disable(logging.NOTSET)


class QGISBase:
    @staticmethod
    def start_qgis(qgis_filepath: str, qgis_profile: str = 'default') -> None:
        """
        Starts the QGIS application with the specified profile.

        == Arguments ==
        - ``qgis_filepath``: Path to the QGIS executable.
        - ``qgis_profile``: Name of the QGIS profile to use (default 'default).

        == Example ==
        | Start QGIS | C:/Program Files/QGIS/bin/qgis.exe |

        == Returns ==
        None
        """
        global app
        app = Application(backend='uia').start(cmd_line=f'{qgis_filepath} --profile {qgis_profile}',
                                               timeout=60)
        logging.info(f'QGIS started ({qgis_filepath} --profile {qgis_profile})')

    @staticmethod
    def connect_qgis(qgis_filepath: str) -> None:
        """
        Connects to an existing QGIS application process.

        == Arguments ==
        - ``qgis_filepath``: Path to the QGIS executable.

        == Example ==
        | Connect QGIS | C:/Program Files/QGIS/bin/qgis.exe |

        == Returns ==
        None
        """
        global app
        app = Application(backend='uia').connect(path=qgis_filepath, timeout=60)
        logging.info('QGIS connected')

    @staticmethod
    def kill_qgis() -> None:
        """
        Kills the QGIS application process.

        == Arguments ==
        None

        == Example ==
        | Kill QGIS |

        == Returns ==
        None
        """
        app.kill()
        logging.info('QGIS killed')

    @staticmethod
    def main_window() -> Any:
        """
        Gets the main window of the QGIS application.

        == Arguments ==
        None

        == Example ==
        | ${main_window} | Main Window |

        == Returns ==
        Main window locator object.
        """
        main_window = QGISLocator.get_window(app, title_re='.*QGIS.*', found_index=0)
        QGISAction.set_focus_locator(main_window)
        QGISAction.maximize_window(main_window)
        return main_window


class QGISDrawBox:
    @staticmethod
    def draw_box_green(locator: Any, colour: str | int = 'green', thickness: int = 4) -> None:
        """
        Draws a green outline box around the specified locator.

        == Arguments ==
        - ``locator``: Locator object.
        - ``colour``: Colour name or code (default 'green').
        - ``thickness``: Thickness of the outline (default 4).

        == Example ==
        | Draw Box Green | ${locator} |

        == Returns ==
        None
        """
        locator.draw_outline(colour, thickness)

    @staticmethod
    def draw_box_blue(locator: Any, colour: str | int = 'blue', thickness: int = 4) -> None:
        """
        Draws a blue outline box around the specified locator.

        == Arguments ==
        - ``locator``: Locator object.
        - ``colour``: Colour name or code (default 'blue').
        - ``thickness``: Thickness of the outline (default 4).

        == Example ==
        | Draw Box Blue | ${locator} |

        == Returns ==
        None
        """
        locator.draw_outline(colour, thickness)

    @staticmethod
    def draw_box_orange(locator: Any, colour: str | int = 42215, thickness: int = 4) -> None:
        """
        Draws an orange outline box around the specified locator.

        == Arguments ==
        - ``locator``: Locator object.
        - ``colour``: Colour name or code (default 42215).
        - ``thickness``: Thickness of the outline (default 4).

        == Example ==
        | Draw Box Orange | ${locator} |

        == Returns ==
        None
        """
        locator.draw_outline(colour, thickness)


class QGISAction(QGISDrawBox):
    @staticmethod
    def set_focus_locator(locator: Any, sleep_time: int = 0) -> None:
        """
        Sets focus to the specified locator.

        == Arguments ==
        - ``locator``: Locator object.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Set Focus Locator | ${locator} | sleep_time=1 |

        == Returns ==
        None
        """
        QGISDrawBox.draw_box_blue(locator)
        locator.set_focus()
        sleep(sleep_time)
        logging.info(f'{locator.criteria} set focus')

    @staticmethod
    def maximize_window(locator: Any) -> None:
        """
        Maximizes the window represented by the locator.

        == Arguments ==
        - ``locator``: Window locator object.

        == Example ==
        | Maximize Window | ${window_locator} |

        == Returns ==
        None
        """
        if not locator.is_maximized():
            maximize_button = QGISLocator.get_locator_by_parent(locator, title='Maksymalizuj',
                                                                control_type='Button')
            QGISAction.mouse_click_locator(maximize_button)
            logging.info(f'{locator.criteria} maximized')

    @staticmethod
    def mouse_get_position() -> tuple:
        """
        Gets the current mouse position.

        == Arguments ==
        None

        == Example ==
        | ${x} | ${y} | Mouse Get Position |

        == Returns ==
        Tuple of (x, y) coordinates.
        """
        x, y = position()
        logging.info(f'Mouse position X: {x}, Y: {y} get')
        return x, y

    @staticmethod
    def mouse_click_locator(locator: Any, sleep_time: int = 0) -> None:
        """
        Performs a left mouse click on the specified locator.

        == Arguments ==
        - ``locator``: Locator object.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Mouse Click Locator | ${locator} | sleep_time=1 |

        == Returns ==
        None
        """
        QGISDrawBox.draw_box_blue(locator)
        locator.click_input()
        sleep(sleep_time)
        try:
            logging.info(f'{locator.criteria} left clicked, slept {sleep_time} second(s)')
        except AttributeError:
            logging.info(f'{locator.element_info} left clicked, slept {sleep_time} second(s)')

    @staticmethod
    def mouse_right_click_locator(locator: Any, sleep_time: int = 0) -> None:
        """
        Performs a right mouse click on the specified locator.

        == Arguments ==
        - ``locator``: Locator object.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Mouse Right Click Locator | ${locator} | sleep_time=1 |

        == Returns ==
        None
        """
        QGISDrawBox.draw_box_blue(locator)
        locator.right_click_input()
        sleep(sleep_time)
        try:
            logging.info(f'{locator.criteria} right clicked, slept {sleep_time} second(s)')
        except AttributeError:
            logging.info(f'{locator.element_info} right clicked, slept {sleep_time} second(s)')

    @staticmethod
    def mouse_click_expand_locator(locator: Any, sleep_time: int = 0) -> None:
        """
        Performs a mouse click on the expand arrow for the specified locator.

        == Arguments ==
        - ``locator``: Locator object.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Mouse Click Expand Locator | ${locator} | sleep_time=1 |

        == Returns ==
        None
        """
        QGISDrawBox.draw_box_blue(locator)
        rectangle = locator.rectangle()
        x = rectangle.left + (rectangle.width() // 2) + 15
        y = rectangle.top + (rectangle.height() // 2)
        mouse.click(coords=(x, y))
        sleep(sleep_time)
        logging.info(f'{locator.criteria} expand clicked, slept {sleep_time} second(s)')

    @staticmethod
    def mouse_click_coords(X: int, Y: int, button: str = 'left', sleep_time: int = 0) -> None:
        """
        Performs a mouse click at the specified coordinates.

        == Arguments ==
        - ``X``: X coordinate.
        - ``Y``: Y coordinate.
        - ``button``: Mouse button ('left', 'right', etc.). Default 'left'.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Mouse Click Coords | 100 | 200 | button=left | sleep_time=1 |

        == Returns ==
        None
        """
        mouse.click(coords=(X, Y), button=button)
        sleep(sleep_time)
        logging.info(f'screen coords X: {X}, Y: {Y} {button} clicked, slept {sleep_time} second(s)')

    @staticmethod
    def mouse_press_coords(X: int, Y: int, button: str = 'left', sleep_time: int = 0) -> None:
        """
        Presses the mouse button at the specified coordinates.

        == Arguments ==
        - ``X``: X coordinate.
        - ``Y``: Y coordinate.
        - ``button``: Mouse button ('left', 'right', etc.). Default 'left'.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Mouse Press Coords | 100 | 200 | button=left | sleep_time=1 |

        == Returns ==
        None
        """
        mouse.press(coords=(X, Y), button=button)
        sleep(sleep_time)
        logging.info(f'screen coords X: {X}, Y: {Y} {button} pressed, slept {sleep_time} second(s)')

    @staticmethod
    def mouse_release_coords(X: int, Y: int, button: str = 'left', sleep_time: int = 0) -> None:
        """
        Releases the mouse button at the specified coordinates.

        == Arguments ==
        - ``X``: X coordinate.
        - ``Y``: Y coordinate.
        - ``button``: Mouse button ('left', 'right', etc.). Default 'left'.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Mouse Release Coords | 100 | 200 | button=left | sleep_time=1 |

        == Returns ==
        None
        """
        mouse.release(coords=(X, Y), button=button)
        sleep(sleep_time)
        logging.info(f'screen coords X: {X}, Y: {Y} {button} released, slept {sleep_time} second(s)')

    @staticmethod
    def mouse_scroll_coords(X: int, Y: int, wheel_distance: int = 1, sleep_time: int = 0) -> None:
        """
        Scrolls the mouse wheel at the specified coordinates.

        == Arguments ==
        - ``X``: X coordinate.
        - ``Y``: Y coordinate.
        - ``wheel_distance``: Distance to scroll the wheel (default 1).
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Mouse Scroll Coords | 100 | 200 | wheel_distance=2 | sleep_time=1 |

        == Returns ==
        None
        """
        mouse.scroll(coords=(X, Y), wheel_dist=wheel_distance)
        sleep(sleep_time)
        logging.info(f'screen coords X: {X}, Y: {Y}, {wheel_distance} scrolled, slept {sleep_time} second(s)')

    @staticmethod
    def select_item_locator(locator: Any, item: Any, sleep_time: int = 0) -> None:
        """
        Selects an item in a locator (e.g., dropdown or list).

        == Arguments ==
        - ``locator``: Locator object.
        - ``item``: Item to select.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Select Item Locator | ${locator} | ${item} | sleep_time=1 |

        == Returns ==
        None
        """
        QGISDrawBox.draw_box_blue(locator)
        locator.select(item)
        sleep(sleep_time)
        logging.info(f'{locator.criteria} selected with {item}, slept {sleep_time} second(s)')

    @staticmethod
    def type_keys_locator(locator: Any, keys: str, sleep_time: int = 0) -> None:
        """
        Types keys into a locator (e.g., text field).

        == Arguments ==
        - ``locator``: Locator object.
        - ``keys``: Keys to type.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Type Keys Locator | ${locator} | text to type | sleep_time=1 |

        == Returns ==
        None
        """
        QGISDrawBox.draw_box_blue(locator)
        locator.type_keys(keys)
        sleep(sleep_time)
        logging.info(f'{locator.criteria} typed keys: {keys}, slept {sleep_time} second(s)')

    @staticmethod
    def send_keys(keys: str, sleep_time: int = 0) -> None:
        """
        Sends keyboard keys globally.

        == Arguments ==
        - ``keys``: Keys to send.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Send Keys | text to type | sleep_time=1 |

        == Returns ==
        None
        """
        send_keys(keys)
        sleep(sleep_time)
        logging.info(f'keyboard sent keys: {keys}, slept {sleep_time} second(s)')

    @staticmethod
    def clear_type_keys_enter_locator(locator: Any, keys: str, sleep_time: int = 0) -> None:
        """
        Clears a locator, types keys, and presses ENTER.

        == Arguments ==
        - ``locator``: Locator object.
        - ``keys``: Keys to type.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Clear Type Keys Enter Locator | ${locator} | text to type | sleep_time=1 |

        == Returns ==
        None
        """
        QGISDrawBox.draw_box_blue(locator)
        locator.type_keys('^a{DEL}')
        locator.type_keys(keys)
        locator.type_keys('{ENTER}')
        sleep(sleep_time)
        logging.info(f'clear + {locator.criteria} typed keys: {keys} + ENTER, slept {sleep_time} second(s)')

    @staticmethod
    def clear_type_keys_locator(locator: Any, keys: str, sleep_time: int = 0) -> None:
        """
        Clears a locator and types keys.

        == Arguments ==
        - ``locator``: Locator object.
        - ``keys``: Keys to type.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Clear Type Keys Locator | ${locator} | text to type | sleep_time=1 |

        == Returns ==
        None
        """
        QGISDrawBox.draw_box_blue(locator)
        locator.type_keys('^a{DEL}')
        locator.type_keys(keys)
        sleep(sleep_time)
        logging.info(f'clear + {locator.criteria} typed keys: {keys}, slept {sleep_time} second(s)')

    @staticmethod
    def move_mouse_locator(locator: Any, sleep_time: float = 0.5) -> None:
        """
        Moves the mouse to the center of a locator.

        == Arguments ==
        - ``locator``: Locator object.
        - ``sleep_time``: Time to sleep after action (default 0.5).

        == Example ==
        | Move Mouse Locator | ${locator} | sleep_time=1 |

        == Returns ==
        None
        """
        mouse.move(coords=locator.rectangle().mid_point())
        sleep(sleep_time)
        logging.info(f'{locator.criteria} mouse moved, slept {sleep_time} second(s)')

    @staticmethod
    def move_mouse_coords(X: int, Y: int, sleep_time: int = 0) -> None:
        """
        Moves the mouse to the specified coordinates.

        == Arguments ==
        - ``X``: X coordinate.
        - ``Y``: Y coordinate.
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Move Mouse Coords | 100 | 200 | sleep_time=1 |

        == Returns ==
        None
        """
        mouse.move(coords=(X, Y))
        sleep(sleep_time)
        logging.info(f'screen coords X: {X}, Y: {Y} mouse moved, slept {sleep_time} second(s)')


class QGISLocator(QGISDrawBox):
    @staticmethod
    def get_window(app: Any, **kwargs: Any) -> Any:
        """
        Finds a window in the QGIS application using provided criteria.

        == Arguments ==
        - ``app``: Application object.
        - ``**kwargs``: Criteria for locating the window (e.g., title, title_re, control_type, etc.).

        == Example ==
        | ${window} | Get Window | ${app} | title_re=.*QGIS.* |

        == Returns ==
        Window locator object.
        """
        window = app.window(**kwargs)
        window.wait('exists visible', timeout=60)
        logging.info(f'{window.criteria} get')
        QGISDrawBox.draw_box_green(window)
        return window

    @staticmethod
    def get_locator_by_parent(parent: Any, **kwargs: Any) -> Any:
        """
        Finds a child UI element (locator) inside a parent window/control.

        == Arguments ==
        - ``parent``: Parent locator (e.g., main window or container).
        - ``**kwargs``: Criteria for locating the child element. Supported keys:

          - ``title``: Exact title/name of the control.
          - ``title_re``: Regex pattern for the title.
          - ``control_type``: UI Automation control type (e.g., ``Edit``, ``Button``).
          - ``auto_id``: Automation ID (from Inspect.exe, only in UIA backend).
          - ``class_name``: Win32 class name of the control.
          - ``class_name_re``: Regex for class name.
          - ``process``: Process ID to narrow down control search.
          - ``enabled_only``: If True (default), only enabled controls are matched.
          - ``visible_only``: If True (default), only visible controls are matched.
          - ``found_index``: Zero-based index in case of multiple matches.
          - ``ctrl_index``: Index used in win32 backend (alternative to ``found_index``).
          - ``handle``: Window handle (HWND, integer).
          - ``rich_text``: If True, identifies RichEdit controls (mainly win32).
          - ``backend``: Either ``uia`` or ``win32`` – normally specified at app level.
          - ``depth``: Max search depth; defaults vary (esp. in recursive search).
          - ``top_level_only``: If True, restricts to top-level windows.
          - ``control_id``: Win32 control ID (not UIA).
          - ``best_match``: Internal use — usually inferred from ``title``.
          - ``predicate_func``: Custom function to filter controls; receives an ElementInfo object.

        == Example ==
        | ${button} | Get Locator By Parent | ${main_window} | title=OK |
        | ${button} | Get Locator By Parent | ${main_window} | title=Open | control_type=Button |

        == Returns ==
        Locator object representing the child window/control.
        """
        locator = parent.child_window(**kwargs)
        logging.info(f'{locator.criteria} get')
        QGISDrawBox.draw_box_green(locator)
        return locator

    @staticmethod
    def get_locator_by_path(path: str) -> Any:
        """
        Gets a locator by a given path.

        == Arguments ==
        - ``path``: Path string to the locator.

        == Example ==
        | ${locator} | Get Locator By Path | path=some/path/string |

        == Returns ==
        Locator object representing the path.
        """
        locator = path
        logging.info(f'{locator.criteria} get')
        QGISDrawBox.draw_box_green(locator)
        return locator

    @staticmethod
    def get_item(locator: Any, item: Any, exact: bool = False) -> Any:
        """
        Gets an item from a locator, optionally using exact matching.

        == Arguments ==
        - ``locator``: Locator object (e.g., list, dropdown).
        - ``item``: Item to retrieve.
        - ``exact``: If True, matches item exactly (default False).

        == Example ==
        | ${item_locator} | Get Item | ${locator} | ${item} | exact=True |

        == Returns ==
        Item locator object.
        """
        item = locator.get_item(item, exact=exact)
        try:
            logging.info(f'{item.criteria} get')
        except AttributeError:
            logging.info(f'{item.element_info} get')
        QGISDrawBox.draw_box_green(item)
        return item

    @staticmethod
    def get_locator_exists(locator: Any) -> bool:
        """
        Checks if the locator exists.

        == Arguments ==
        - ``locator``: Locator object.

        == Example ==
        | ${exists} | Get Locator Exists | ${locator} |

        == Returns ==
        Boolean indicating existence.
        """
        logging.info(f'{locator.criteria} get locator exists')
        QGISDrawBox.draw_box_orange(locator)
        return locator.exists()

    @staticmethod
    def get_locator_is_enabled(locator: Any) -> bool:
        """
        Checks if the locator is enabled.

        == Arguments ==
        - ``locator``: Locator object.

        == Example ==
        | ${enabled} | Get Locator Is Enabled | ${locator} |

        == Returns ==
        Boolean indicating if enabled.
        """
        logging.info(f'{locator.criteria} get locator is enabled')
        QGISDrawBox.draw_box_orange(locator)
        return locator.is_enabled()

    @staticmethod
    def get_locator_is_active(locator: Any) -> bool:
        """
        Checks if the locator is active.

        == Arguments ==
        - ``locator``: Locator object.

        == Example ==
        | ${active} | Get Locator Is Active | ${locator} |

        == Returns ==
        Boolean indicating if active.
        """
        logging.info(f'{locator.criteria} get locator is active')
        QGISDrawBox.draw_box_orange(locator)
        return locator.is_active()

    @staticmethod
    def get_locator_is_readonly(locator: Any) -> bool:
        """
        Checks if the locator is read-only.

        == Arguments ==
        - ``locator``: Locator object.

        == Example ==
        | ${readonly} | Get Locator Is Readonly | ${locator} |

        == Returns ==
        Boolean indicating if read-only.
        """
        logging.info(f'{locator.criteria} get locator is readonly')
        QGISDrawBox.draw_box_orange(locator)
        return locator.legacy_properties().get('IsReadOnly', False)

    @staticmethod
    def get_locator_is_visible(locator: Any) -> bool:
        """
        Checks if the locator is visible.

        == Arguments ==
        - ``locator``: Locator object.

        == Example ==
        | ${visible} | Get Locator Is Visible | ${locator} |

        == Returns ==
        Boolean indicating if visible.
        """
        logging.info(f'{locator.criteria} get locator is visible')
        QGISDrawBox.draw_box_orange(locator)
        return locator.is_visible()

    @staticmethod
    def get_locator_texts(locator: Any) -> str | list:
        """
        Gets the text(s) from a locator.

        == Arguments ==
        - ``locator``: Locator object.

        == Example ==
        | ${texts} | Get Locator Texts | ${locator} |

        == Returns ==
        Text(s) as string or list.
        """
        logging.info(f'{locator.criteria} get locator texts')
        QGISDrawBox.draw_box_orange(locator)
        return locator.texts()

    @staticmethod
    def get_selected_text(locator: Any) -> str | list:
        """
        Gets the selected text from a locator.

        == Arguments ==
        - ``locator``: Locator object.

        == Example ==
        | ${selected_text} | Get Selected Text | ${locator} |

        == Returns ==
        Selected text as string or list.
        """
        logging.info(f'{locator.criteria} get locator selected text')
        QGISDrawBox.draw_box_orange(locator)
        return locator.selected_text()
