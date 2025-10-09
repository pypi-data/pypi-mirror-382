"""
Functions for logging and other small actions within the console.\n
----------------------------------------------------------------------------------------------------------
You can also use special formatting codes directly inside the log message to change their appearance.
For more detailed information about formatting codes, see the the `format_codes` module documentation.
"""

from .base.consts import COLOR, CHARS, ANSI
from .format_codes import FormatCodes, _COMPILED as _FC_COMPILED
from .string import String
from .color import Color, Rgba, Hexa

from typing import Generator, TypedDict, Callable, Optional, Literal, Mapping, Pattern, TypeVar, TextIO, Any, overload, cast, Protocol
from prompt_toolkit.key_binding import KeyPressEvent, KeyBindings
from prompt_toolkit.validation import ValidationError, Validator
from prompt_toolkit.styles import Style
from contextlib import contextmanager
from prompt_toolkit.keys import Keys
import prompt_toolkit as _pt
import keyboard as _keyboard
import getpass as _getpass
import shutil as _shutil
import sys as _sys
import os as _os
import re as _re
import io as _io


_COMPILED: dict[str, Pattern] = {  # PRECOMPILE REGULAR EXPRESSIONS
    "hr": _re.compile(r"(?i)\{hr\}"),
    "hr_no_nl": _re.compile(r"(?i)(?<!\n){hr}(?!\n)"),
    "hr_r_nl": _re.compile(r"(?i)(?<!\n){hr}(?=\n)"),
    "hr_l_nl": _re.compile(r"(?i)(?<=\n){hr}(?!\n)"),
    "label": _re.compile(r"(?i)\{(?:label|l)\}"),
    "bar": _re.compile(r"(?i)\{(?:bar|b)\}"),
    "current": _re.compile(r"(?i)\{(?:current|c)\}"),
    "total": _re.compile(r"(?i)\{(?:total|t)\}"),
    "percentage": _re.compile(r"(?i)\{(?:percentage|percent|p)\}"),
}


class _ConsoleWidth:

    def __get__(self, obj, owner=None):
        try:
            return _os.get_terminal_size().columns
        except OSError:
            return 80


class _ConsoleHeight:

    def __get__(self, obj, owner=None):
        try:
            return _os.get_terminal_size().lines
        except OSError:
            return 24


class _ConsoleSize:

    def __get__(self, obj, owner=None):
        try:
            size = _os.get_terminal_size()
            return (size.columns, size.lines)
        except OSError:
            return (80, 24)


class _ConsoleUser:

    def __get__(self, obj, owner=None):
        return _os.getenv("USER") or _os.getenv("USERNAME") or _getpass.getuser()


class _ArgConfigWithDefault(TypedDict):
    flags: list[str] | tuple[str, ...]
    default: Any


class ArgResult:
    """Represents the result of a parsed command-line argument and contains the following attributes:
    - `exists` -⠀if the argument was found or not
    - `value` -⠀the value given with the found argument\n
    --------------------------------------------------------------------------------------------------------
    When the `ArgResult` instance is accessed as a boolean it will correspond to the `exists` attribute."""

    def __init__(self, exists: bool, value: Any | list[Any]):
        self.exists: bool = exists
        """Whether the argument was found or not."""
        self.value: Any = value
        """The value given with the found argument."""

    def __bool__(self):
        return self.exists


class Args:
    """Container for parsed command-line arguments, allowing attribute-style access.
    For example, if an argument `foo` was parsed, it can be accessed via `args.foo`.
    Each such attribute (e.g. `args.foo`) is an instance of `ArgResult`."""

    def __init__(self, **kwargs: dict[str, Any | list[Any]]):
        for alias_name, data_dict in kwargs.items():
            if not alias_name.isidentifier():
                raise TypeError(f"Argument alias '{alias_name}' is invalid. It must be a valid Python variable name.")
            setattr(self, alias_name, ArgResult(exists=cast(bool, data_dict["exists"]), value=data_dict["value"]))

    def __len__(self):
        return len(vars(self))

    def __contains__(self, key):
        return hasattr(self, key)

    def __getattr__(self, name: str) -> ArgResult:
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.__iter__())[key]
        return getattr(self, key)

    def __iter__(self):
        for key, value in vars(self).items():
            yield (key, {"exists": value.exists, "value": value.value})

    def dict(self) -> dict[str, dict[str, Any]]:
        """Returns the arguments as a dictionary."""
        return {k: {"exists": v.exists, "value": v.value} for k, v in vars(self).items()}

    def keys(self):
        """Returns the argument aliases as `dict_keys([...])`."""
        return vars(self).keys()

    def values(self):
        """Returns the argument results as `dict_values([...])`."""
        return vars(self).values()

    def items(self):
        """Yields tuples of `(alias, {'exists': bool, 'value': Any})`."""
        for key, value in self.__iter__():
            yield (key, value)


class Console:

    w: int = _ConsoleWidth()  # type: ignore[assignment]
    """The width of the console in characters."""
    h: int = _ConsoleHeight()  # type: ignore[assignment]
    """The height of the console in lines."""
    wh: tuple[int, int] = _ConsoleSize()  # type: ignore[assignment]
    """A tuple with the width and height of the console in characters and lines."""
    usr: str = _ConsoleUser()  # type: ignore[assignment]
    """The name of the current user."""

    @staticmethod
    def get_args(
        find_args: Mapping[
            str,
            list[str] | tuple[str, ...] | _ArgConfigWithDefault | Literal["before", "after"],
        ],
        allow_spaces: bool = False
    ) -> Args:
        """Will search for the specified arguments in the command line
        arguments and return the results as a special `Args` object.\n
        ----------------------------------------------------------------
        The `find_args` dictionary can have the following structures for each alias:
        1. Simple list/tuple of flags (when no default value is needed):
           ```python
           "alias_name": ["-f", "--flag"]
           ```
        2. Dictionary with 'flags' and optional 'default':
           ```python
           "alias_name": {
               "flags": ["-f", "--flag"],
               "default": "some_value"  # Optional
           }
           ```
        3. Positional argument collection (string value):
           ```python
           "alias_name": "before"  # Collects non-flagged args before first flag
           "alias_name": "after"   # Collects non-flagged args after last flag
           ```
        Example `find_args`:
        ```python
        find_args={
            "text": "before",           # Positional args before flags
            "arg1": {                   # With default
                "flags": ["-a1", "--arg1"],
                "default": "default_val"
            },
            "arg2": ("-a2", "--arg2"),  # Without default (original format)
            "arg3": ["-a3"],            # Without default (list format)
            "arg4": {                   # Flag with default True
                "flags": ["-f"],
                "default": True
            }
        }
        ```
        If the script is called via the command line:\n
        `python script.py Hello World -a1 "value1" --arg2 -f`\n
        ...it would return an `Args` object where:
        - `args.text.exists` is `True`, `args.text.value` is `["Hello", "World"]`
        - `args.arg1.exists` is `True`, `args.arg1.value` is `"value1"`
        - `args.arg2.exists` is `True`, `args.arg2.value` is `True` (flag present without value)
        - `args.arg3.exists` is `False`, `args.arg3.value` is `None` (not present, no default)
        - `args.arg4.exists` is `True`, `args.arg4.value` is `True` (flag present, overrides default)
        - If an arg defined in `find_args` is *not* present in the command line:
            - `exists` will be `False`
            - `value` will be the specified `default` value, or `None` if no default was specified.\n
        ----------------------------------------------------------------
        For positional arguments:
        - `"before"`: Collects all non-flagged arguments that appear before the first flag
        - `"after"`: Collects all non-flagged arguments that appear after the last flag's value
        ----------------------------------------------------------------
        Normally if `allow_spaces` is false, it will take a space as
        the end of an args value. If it is true, it will take spaces as
        part of the value up until the next arg-flag is found.
        (Multiple spaces will become one space in the value.)"""
        args = _sys.argv[1:]
        args_len = len(args)
        arg_lookup = {}
        results = {}
        positional_configs = {}
        before_count = 0
        after_count = 0

        # PARSE "find_args" CONFIGURATION
        for alias, config in find_args.items():
            flags = None
            default_value = None

            if isinstance(config, str):
                # HANDLE POSITIONAL ARGUMENT COLLECTION
                if config not in ("before", "after"):
                    raise ValueError(
                        f"Invalid positional argument type '{config}' for alias '{alias}'. Must be 'before' or 'after'."
                    )
                if config == "before":
                    before_count += 1
                    if before_count > 1:
                        raise ValueError("Only one alias can have the value 'before' for positional argument collection.")
                elif config == "after":
                    after_count += 1
                    if after_count > 1:
                        raise ValueError("Only one alias can have the value 'after' for positional argument collection.")
                positional_configs[alias] = config
                results[alias] = {"exists": False, "value": []}
            elif isinstance(config, (list, tuple)):
                flags = config
                results[alias] = {"exists": False, "value": default_value}
            elif isinstance(config, dict):
                if "flags" not in config:
                    raise ValueError(f"Invalid configuration for alias '{alias}'. Dictionary must contain a 'flags' key.")
                if "default" not in config:
                    raise ValueError(
                        f"Invalid configuration for alias '{alias}'. Dictionary must contain a 'default' key. Use a simple list/tuple if no default value is needed."
                    )
                flags, default_value = config["flags"], config["default"]
                if not isinstance(flags, (list, tuple)):
                    raise ValueError(f"Invalid 'flags' for alias '{alias}'. Must be a list or tuple.")
                results[alias] = {"exists": False, "value": default_value}
            else:
                raise TypeError(
                    f"Invalid configuration type for alias '{alias}'. Must be a list, tuple, dict or literal 'before' / 'after'."
                )

            # BUILD FLAG LOOKUP FOR NON-POSITIONAL ARGUMENTS
            if flags is not None:
                for flag in flags:
                    if flag in arg_lookup:
                        raise ValueError(
                            f"Duplicate flag '{flag}' found. It's assigned to both '{arg_lookup[flag]}' and '{alias}'."
                        )
                    arg_lookup[flag] = alias

        # FIND POSITIONS OF FIRST AND LAST FLAGS FOR POSITIONAL ARGUMENT COLLECTION
        first_flag_pos = None
        last_flag_with_value_pos = None

        for i, arg in enumerate(args):
            if arg in arg_lookup:
                if first_flag_pos is None:
                    first_flag_pos = i
                # CHECK IF THIS FLAG HAS A VALUE FOLLOWING IT
                flag_has_value = (i + 1 < args_len and args[i + 1] not in arg_lookup)
                if flag_has_value:
                    if not allow_spaces:
                        last_flag_with_value_pos = i + 1
                    else:
                        # FIND THE END OF THE MULTI-WORD VALUE
                        j = i + 1
                        while j < args_len and args[j] not in arg_lookup:
                            j += 1
                        last_flag_with_value_pos = j - 1

        # COLLECT "before" POSITIONAL ARGUMENTS
        for alias, pos_type in positional_configs.items():
            if pos_type == "before":
                before_args = []
                end_pos = first_flag_pos if first_flag_pos is not None else args_len
                for i in range(end_pos):
                    if args[i] not in arg_lookup:
                        before_args.append(String.to_type(args[i]))
                if before_args:
                    results[alias]["value"] = before_args
                    results[alias]["exists"] = len(before_args) > 0

        # PROCESS FLAGGED ARGUMENTS
        i = 0
        while i < args_len:
            arg = args[i]
            alias = arg_lookup.get(arg)
            if alias:
                results[alias]["exists"] = True
                value_found_after_flag = False
                if i + 1 < args_len and args[i + 1] not in arg_lookup:
                    if not allow_spaces:
                        results[alias]["value"] = String.to_type(args[i + 1])
                        i += 1
                        value_found_after_flag = True
                    else:
                        value_parts = []
                        j = i + 1
                        while j < args_len and args[j] not in arg_lookup:
                            value_parts.append(args[j])
                            j += 1
                        if value_parts:
                            results[alias]["value"] = String.to_type(" ".join(value_parts))
                            i = j - 1
                            value_found_after_flag = True
                if not value_found_after_flag:
                    results[alias]["value"] = None
            i += 1

        # COLLECT "after" POSITIONAL ARGUMENTS
        for alias, pos_type in positional_configs.items():
            if pos_type == "after":
                after_args = []
                start_pos = (last_flag_with_value_pos + 1) if last_flag_with_value_pos is not None else 0
                # IF NO FLAGS WERE FOUND WITH VALUES, START AFTER THE LAST FLAG
                if last_flag_with_value_pos is None and first_flag_pos is not None:
                    # FIND THE LAST FLAG POSITION
                    last_flag_pos = None
                    for i, arg in enumerate(args):
                        if arg in arg_lookup:
                            last_flag_pos = i
                    if last_flag_pos is not None:
                        start_pos = last_flag_pos + 1

                for i in range(start_pos, args_len):
                    if args[i] not in arg_lookup:
                        after_args.append(String.to_type(args[i]))

                if after_args:
                    results[alias]["value"] = after_args
                    results[alias]["exists"] = len(after_args) > 0

        return Args(**results)

    @staticmethod
    def pause_exit(
        prompt: object = "",
        pause: bool = True,
        exit: bool = False,
        exit_code: int = 0,
        reset_ansi: bool = False,
    ) -> None:
        """Will print the `prompt` and then pause the program if `pause` is
        true and after the pause, exit the program if `exit` is set true."""
        FormatCodes.print(prompt, end="", flush=True)
        if reset_ansi:
            FormatCodes.print("[_]", end="")
        if pause:
            _keyboard.read_key(suppress=True)
        if exit:
            _sys.exit(exit_code)

    @staticmethod
    def cls() -> None:
        """Will clear the console in addition to completely resetting the ANSI formats."""
        if _shutil.which("cls"):
            _os.system("cls")
        elif _shutil.which("clear"):
            _os.system("clear")
        print("\033[0m", end="", flush=True)

    @staticmethod
    def log(
        title: Optional[str] = None,
        prompt: object = "",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        title_bg_color: Optional[Rgba | Hexa] = None,
        default_color: Optional[Rgba | Hexa] = None,
        tab_size: int = 8,
        title_px: int = 1,
        title_mx: int = 2,
    ) -> None:
        """Prints a nicely formatted log message.\n
        -------------------------------------------------------------------------------------------
        - `title` -⠀the title of the log message (e.g. `DEBUG`, `WARN`, `FAIL`, etc.)
        - `prompt` -⠀the log message
        - `format_linebreaks` -⠀whether to format (indent after) the line breaks or not
        - `start` -⠀something to print before the log is printed
        - `end` -⠀something to print after the log is printed (e.g. `\\n`)
        - `title_bg_color` -⠀the background color of the `title`
        - `default_color` -⠀the default text color of the `prompt`
        - `tab_size` -⠀the tab size used for the log (default is 8 like console tabs)
        - `title_px` -⠀the horizontal padding (in chars) to the title (if `title_bg_color` is set)
        - `title_mx` -⠀the horizontal margin (in chars) to the title\n
        -------------------------------------------------------------------------------------------
        The log message can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `format_codes` module documentation."""
        has_title_bg = title_bg_color is not None and Color.is_valid(title_bg_color)
        title = "" if title is None else title.strip().upper()
        title_fg = Color.text_color_for_on_bg(
            Color.to_hexa(title_bg_color)  # type: ignore[assignment]
        ) if has_title_bg else "_color"
        px, mx = (" " * title_px) if has_title_bg else "", " " * title_mx
        tab = " " * (tab_size - 1 - ((len(mx) + (title_len := len(title) + 2 * len(px))) % tab_size))
        if format_linebreaks:
            clean_prompt, removals = FormatCodes.remove_formatting(str(prompt), get_removals=True, _ignore_linebreaks=True)
            prompt_lst = (
                String.split_count(l, Console.w - (title_len + len(tab) + 2 * len(mx))) for l in str(clean_prompt).splitlines()
            )
            prompt_lst = (
                item for lst in prompt_lst for item in ([""] if lst == [] else (lst if isinstance(lst, list) else [lst]))
            )
            prompt = f"\n{mx}{' ' * title_len}{mx}{tab}".join(
                Console.__add_back_removed_parts(list(prompt_lst), cast(tuple[tuple[int, str], ...], removals))
            )
        if title == "":
            FormatCodes.print(
                f'{start}  {f"[{default_color}]" if default_color else ""}{prompt}[_]',
                default_color=default_color,
                end=end,
            )
        else:
            FormatCodes.print(
                f"{start}{mx}[bold][{title_fg}]{f'[BG:{title_bg_color}]' if title_bg_color else ''}{px}{title}{px}[_]{mx}"
                + f"{tab}{f'[{default_color}]' if default_color else ''}{prompt}[_]",
                default_color=default_color,
                end=end,
            )

    @staticmethod
    def __add_back_removed_parts(split_string: list[str], removals: tuple[tuple[int, str], ...]) -> list[str]:
        """Adds back the removed parts into the split string parts at their original positions."""
        lengths, cumulative_pos = [len(s) for s in split_string], [0]
        for length in lengths:
            cumulative_pos.append(cumulative_pos[-1] + length)
        result, offset_adjusts = split_string.copy(), [0] * len(split_string)
        last_idx, total_length = len(split_string) - 1, cumulative_pos[-1]

        def find_string_part(pos: int) -> int:
            left, right = 0, len(cumulative_pos) - 1
            while left < right:
                mid = (left + right) // 2
                if cumulative_pos[mid] <= pos < cumulative_pos[mid + 1]:
                    return mid
                elif pos < cumulative_pos[mid]:
                    right = mid
                else:
                    left = mid + 1
            return left

        for pos, removal in removals:
            if pos >= total_length:
                result[last_idx] = result[last_idx] + removal
                continue
            i = find_string_part(pos)
            adjusted_pos = (pos - cumulative_pos[i]) + offset_adjusts[i]
            parts = [result[i][:adjusted_pos], removal, result[i][adjusted_pos:]]
            result[i] = "".join(parts)
            offset_adjusts[i] += len(removal)
        return result

    @staticmethod
    def debug(
        prompt: object = "Point in program reached.",
        active: bool = True,
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = False,
        exit_code: int = 0,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `DEBUG` log message with the options to pause
        at the message and exit the program after the message was printed.
        If `active` is false, no debug message will be printed."""
        if active:
            Console.log("DEBUG", prompt, format_linebreaks, start, end, COLOR.YELLOW, default_color)
            Console.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @staticmethod
    def info(
        prompt: object = "Program running.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = False,
        exit_code: int = 0,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `INFO` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("INFO", prompt, format_linebreaks, start, end, COLOR.BLUE, default_color)
        Console.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @staticmethod
    def done(
        prompt: object = "Program finished.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = False,
        exit_code: int = 0,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `DONE` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("DONE", prompt, format_linebreaks, start, end, COLOR.TEAL, default_color)
        Console.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @staticmethod
    def warn(
        prompt: object = "Important message.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = False,
        exit_code: int = 1,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `WARN` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("WARN", prompt, format_linebreaks, start, end, COLOR.ORANGE, default_color)
        Console.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @staticmethod
    def fail(
        prompt: object = "Program error.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = True,
        exit_code: int = 1,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `FAIL` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("FAIL", prompt, format_linebreaks, start, end, COLOR.RED, default_color)
        Console.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @staticmethod
    def exit(
        prompt: object = "Program ended.",
        format_linebreaks: bool = True,
        start: str = "",
        end: str = "\n",
        default_color: Optional[Rgba | Hexa] = None,
        pause: bool = False,
        exit: bool = True,
        exit_code: int = 0,
        reset_ansi: bool = True,
    ) -> None:
        """A preset for `log()`: `EXIT` log message with the options to pause
        at the message and exit the program after the message was printed."""
        Console.log("EXIT", prompt, format_linebreaks, start, end, COLOR.MAGENTA, default_color)
        Console.pause_exit("", pause=pause, exit=exit, exit_code=exit_code, reset_ansi=reset_ansi)

    @staticmethod
    def log_box_filled(
        *values: object,
        start: str = "",
        end: str = "\n",
        box_bg_color: str | Rgba | Hexa = "green",
        default_color: Optional[Rgba | Hexa] = None,
        w_padding: int = 2,
        w_full: bool = False,
        indent: int = 0,
    ) -> None:
        """Will print a box with a colored background, containing a formatted log message:
        - `*values` -⠀the box content (each value is on a new line)
        - `start` -⠀something to print before the log box is printed (e.g. `\\n`)
        - `end` -⠀something to print after the log box is printed (e.g. `\\n`)
        - `box_bg_color` -⠀the background color of the box
        - `default_color` -⠀the default text color of the `*values`
        - `w_padding` -⠀the horizontal padding (in chars) to the box content
        - `w_full` -⠀whether to make the box be the full console width or not
        - `indent` -⠀the indentation of the box (in chars)\n
        -----------------------------------------------------------------------------------
        The box content can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `format_codes` module documentation."""
        lines, unfmt_lines, max_line_len = Console.__prepare_log_box(values, default_color)
        pad_w_full = (Console.w - (max_line_len + (2 * w_padding))) if w_full else 0
        if box_bg_color is not None and Color.is_valid(box_bg_color):
            box_bg_color = Color.to_hexa(box_bg_color)
        spaces_l = " " * indent
        lines = [
            f"{spaces_l}[bg:{box_bg_color}]{' ' * w_padding}"
            + _FC_COMPILED["formatting"].sub(lambda m: f"{m.group(0)}[bg:{box_bg_color}]", line) +
            (" " * ((w_padding + max_line_len - len(unfmt)) + pad_w_full)) + "[*]" for line, unfmt in zip(lines, unfmt_lines)
        ]
        pady = " " * (Console.w if w_full else max_line_len + (2 * w_padding))
        FormatCodes.print(
            f"{start}{spaces_l}[bg:{box_bg_color}]{pady}[*]\n" + "\n".join(lines)
            + f"\n{spaces_l}[bg:{box_bg_color}]{pady}[_]",
            default_color=default_color or "#000",
            sep="\n",
            end=end,
        )

    @staticmethod
    def log_box_bordered(
        *values: object,
        start: str = "",
        end: str = "\n",
        border_type: Literal["standard", "rounded", "strong", "double"] = "rounded",
        border_style: str | Rgba | Hexa = f"dim|{COLOR.GRAY}",
        default_color: Optional[Rgba | Hexa] = None,
        w_padding: int = 1,
        w_full: bool = False,
        indent: int = 0,
        _border_chars: Optional[tuple[str, str, str, str, str, str, str, str, str, str, str]] = None,
    ) -> None:
        """Will print a bordered box, containing a formatted log message:
        - `*values` -⠀the box content (each value is on a new line)
        - `start` -⠀something to print before the log box is printed (e.g. `\\n`)
        - `end` -⠀something to print after the log box is printed (e.g. `\\n`)
        - `border_type` -⠀one of the predefined border character sets
        - `border_style` -⠀the style of the border (special formatting codes)
        - `default_color` -⠀the default text color of the `*values`
        - `w_padding` -⠀the horizontal padding (in chars) to the box content
        - `w_full` -⠀whether to make the box be the full console width or not
        - `indent` -⠀the indentation of the box (in chars)
        - `_border_chars` -⠀define your own border characters set (overwrites `border_type`)\n
        ---------------------------------------------------------------------------------------------
        You can insert horizontal rules to split the box content by using `{hr}` in the `*values`.\n
        ---------------------------------------------------------------------------------------------
        The box content can be formatted with special formatting codes. For more detailed
        information about formatting codes, see `format_codes` module documentation.\n
        ---------------------------------------------------------------------------------------------
        The `border_type` can be one of the following:
        - `"standard" = ('┌', '─', '┐', '│', '┘', '─', '└', '│', '├', '─', '┤')`
        - `"rounded" = ('╭', '─', '╮', '│', '╯', '─', '╰', '│', '├', '─', '┤')`
        - `"strong" = ('┏', '━', '┓', '┃', '┛', '━', '┗', '┃', '┣', '━', '┫')`
        - `"double" = ('╔', '═', '╗', '║', '╝', '═', '╚', '║', '╠', '═', '╣')`\n
        The order of the characters is always:
        1. top-left corner
        2. top border
        3. top-right corner
        4. right border
        5. bottom-right corner
        6. bottom border
        7. bottom-left corner
        8. left border
        9. left horizontal rule connector
        10. horizontal rule
        11. right horizontal rule connector"""
        borders = {
            "standard": ('┌', '─', '┐', '│', '┘', '─', '└', '│', '├', '─', '┤'),
            "rounded": ('╭', '─', '╮', '│', '╯', '─', '╰', '│', '├', '─', '┤'),
            "strong": ('┏', '━', '┓', '┃', '┛', '━', '┗', '┃', '┣', '━', '┫'),
            "double": ('╔', '═', '╗', '║', '╝', '═', '╚', '║', '╠', '═', '╣'),
        }
        border_chars = borders.get(border_type, borders["standard"]) if _border_chars is None else _border_chars
        lines, unfmt_lines, max_line_len = Console.__prepare_log_box(values, default_color, has_rules=True)
        pad_w_full = (Console.w - (max_line_len + (2 * w_padding)) - (len(border_chars[1] * 2))) if w_full else 0
        if border_style is not None and Color.is_valid(border_style):
            border_style = Color.to_hexa(border_style)
        spaces_l = " " * indent
        border_l = f"[{border_style}]{border_chars[7]}[*]"
        border_r = f"[{border_style}]{border_chars[3]}[_]"
        border_t = f"{spaces_l}[{border_style}]{border_chars[0]}{border_chars[1] * (Console.w - (len(border_chars[1] * 2)) if w_full else max_line_len + (2 * w_padding))}{border_chars[2]}[_]"
        border_b = f"{spaces_l}[{border_style}]{border_chars[6]}{border_chars[5] * (Console.w - (len(border_chars[5] * 2)) if w_full else max_line_len + (2 * w_padding))}{border_chars[4]}[_]"
        h_rule = f"{spaces_l}[{border_style}]{border_chars[8]}{border_chars[9] * (Console.w - (len(border_chars[9] * 2)) if w_full else max_line_len + (2 * w_padding))}{border_chars[10]}[_]"
        lines = [
            h_rule if _COMPILED["hr"].match(line) else f"{spaces_l}{border_l}{' ' * w_padding}{line}[_]" + " " *
            ((w_padding + max_line_len - len(unfmt)) + pad_w_full) + border_r for line, unfmt in zip(lines, unfmt_lines)
        ]
        FormatCodes.print(
            f"{start}{border_t}[_]\n" + "\n".join(lines) + f"\n{border_b}[_]",
            default_color=default_color,
            sep="\n",
            end=end,
        )

    @staticmethod
    def __prepare_log_box(
        values: tuple[object, ...],
        default_color: Optional[Rgba | Hexa] = None,
        has_rules: bool = False,
    ) -> tuple[list[str], list[tuple[str, tuple[tuple[int, str], ...]]], int]:
        """Prepares the log box content and returns it along with the max line length."""
        if has_rules:
            lines = []
            for val in values:
                val_str, result_parts, current_pos = str(val), [], 0
                for match in _COMPILED["hr"].finditer(val_str):
                    start, end = match.span()
                    should_split_before = start > 0 and val_str[start - 1] != '\n'
                    should_split_after = end < len(val_str) and val_str[end] != '\n'

                    if should_split_before:
                        if start > current_pos:
                            result_parts.append(val_str[current_pos:start])
                        if should_split_after:
                            result_parts.append(match.group())
                            current_pos = end
                        else:
                            current_pos = start
                    else:
                        if should_split_after:
                            result_parts.append(val_str[current_pos:end])
                            current_pos = end

                if current_pos < len(val_str):
                    result_parts.append(val_str[current_pos:])

                if not result_parts:
                    result_parts.append(val_str)

                for part in result_parts:
                    lines.extend(part.splitlines())
        else:
            lines = [line for val in values for line in str(val).splitlines()]

        unfmt_lines = [FormatCodes.remove_formatting(line, default_color) for line in lines]
        max_line_len = max(len(line) for line in unfmt_lines)
        return lines, cast(list[tuple[str, tuple[tuple[int, str], ...]]], unfmt_lines), max_line_len

    @staticmethod
    def confirm(
        prompt: object = "Do you want to continue?",
        start="",
        end="",
        default_color: Optional[Rgba | Hexa] = None,
        default_is_yes: bool = True,
    ) -> bool:
        """Ask a yes/no question.\n
        ---------------------------------------------------------------------------------------
        - `prompt` -⠀the input prompt
        - `start` -⠀something to print before the input
        - `end` -⠀something to print after the input (e.g. `\\n`)
        - `default_color` -⠀the default text color of the `prompt`
        - `default_is_yes` -⠀the default answer if the user just presses enter
        ---------------------------------------------------------------------------------------
        The prompt can be formatted with special formatting codes. For more detailed
        information about formatting codes, see the `format_codes` module documentation."""
        confirmed = input(
            FormatCodes.to_ansi(
                f'{start}{str(prompt)} [_|dim](({"Y" if default_is_yes else "y"}/{"n" if default_is_yes else "N"}): )',
                default_color=default_color,
            )
        ).strip().lower() in (("", "y", "yes") if default_is_yes else ("y", "yes"))
        if end:
            FormatCodes.print(end, end="")
        return confirmed

    @staticmethod
    def multiline_input(
        prompt: object = "",
        start="",
        end="\n",
        default_color: Optional[Rgba | Hexa] = None,
        show_keybindings=True,
        input_prefix=" ⮡ ",
        reset_ansi=True,
    ) -> str:
        """An input where users can write (and paste) text over multiple lines.\n
        ---------------------------------------------------------------------------------------
        - `prompt` -⠀the input prompt
        - `start` -⠀something to print before the input
        - `end` -⠀something to print after the input (e.g. `\\n`)
        - `default_color` -⠀the default text color of the `prompt`
        - `show_keybindings` -⠀whether to show the special keybindings or not
        - `input_prefix` -⠀the prefix of the input line
        - `reset_ansi` -⠀whether to reset the ANSI codes after the input or not
        ---------------------------------------------------------------------------------------
        The input prompt can be formatted with special formatting codes. For more detailed
        information about formatting codes, see the `format_codes` module documentation."""
        kb = KeyBindings()

        @kb.add("c-d", eager=True)  # CTRL+D
        def _(event):
            event.app.exit(result=event.app.current_buffer.document.text)

        FormatCodes.print(start + str(prompt), default_color=default_color)
        if show_keybindings:
            FormatCodes.print("[dim][[b](CTRL+D)[dim] : end of input][_dim]")
        input_string = _pt.prompt(input_prefix, multiline=True, wrap_lines=True, key_bindings=kb)
        FormatCodes.print("[_]" if reset_ansi else "", end=end[1:] if end.startswith("\n") else end)
        return input_string

    T = TypeVar("T")

    @staticmethod
    def input(
        prompt: object = "",
        start="",
        end="",
        default_color: Optional[Rgba | Hexa] = None,
        placeholder: Optional[str] = None,
        mask_char: Optional[str] = None,
        min_len: Optional[int] = None,
        max_len: Optional[int] = None,
        allowed_chars: str = CHARS.ALL,  # type: ignore[assignment]
        allow_paste: bool = True,
        validator: Optional[Callable[[str], Optional[str]]] = None,
        default_val: Optional[T] = None,
        output_type: type[T] = str,  # type: ignore[assignment]
    ) -> T:
        """Acts like a standard Python `input()` a bunch of cool extra features.\n
        ------------------------------------------------------------------------------------
        - `prompt` -⠀the input prompt
        - `start` -⠀something to print before the input
        - `end` -⠀something to print after the input (e.g. `\\n`)
        - `default_color` -⠀the default text color of the `prompt`
        - `placeholder` -⠀a placeholder text that is shown when the input is empty
        - `mask_char` -⠀if set, the input will be masked with this character
        - `min_len` -⠀the minimum length of the input (required to submit)
        - `max_len` -⠀the maximum length of the input (can't write further if reached)
        - `allowed_chars` -⠀a string of characters that are allowed to be inputted
          (default allows all characters)
        - `allow_paste` -⠀whether to allow pasting text into the input or not
        - `validator` -⠀a function that takes the input string and returns a string error
          message if invalid, or nothing if valid
        - `default_val` -⠀the default value to return if the input is empty
        - `output_type` -⠀the type (class) to convert the input to before returning it\n
        ------------------------------------------------------------------------------------
        The input prompt can be formatted with special formatting codes. For more detailed
        information about formatting codes, see the `format_codes` module documentation."""
        result_text = ""
        tried_pasting = False
        filtered_chars = set()
        has_default = default_val is not None

        class InputValidator(Validator):

            def validate(self, document) -> None:
                text_to_validate = result_text if mask_char else document.text
                if min_len and len(text_to_validate) < min_len:
                    raise ValidationError(message="", cursor_position=len(document.text))
                if validator and validator(text_to_validate) not in ("", None):
                    raise ValidationError(message="", cursor_position=len(document.text))

        def bottom_toolbar() -> _pt.formatted_text.ANSI:
            nonlocal tried_pasting
            try:
                if mask_char:
                    text_to_check = result_text
                else:
                    app = _pt.application.get_app()
                    text_to_check = app.current_buffer.text
                toolbar_msgs = []
                if max_len and len(text_to_check) > max_len:
                    toolbar_msgs.append("[b|#FFF|bg:red]( Text too long! )")
                if validator and text_to_check and (validation_error_msg := validator(text_to_check)) not in ("", None):
                    toolbar_msgs.append(f"[b|#000|bg:br:red] {validation_error_msg} [_bg]")
                if filtered_chars:
                    plural = "" if len(char_list := "".join(sorted(filtered_chars))) == 1 else "s"
                    toolbar_msgs.append(f"[b|#000|bg:yellow]( Char{plural} '{char_list}' not allowed )")
                    filtered_chars.clear()
                if min_len and len(text_to_check) < min_len:
                    toolbar_msgs.append(f"[b|#000|bg:yellow]( Need {min_len - len(text_to_check)} more chars )")
                if tried_pasting:
                    toolbar_msgs.append("[b|#000|bg:br:yellow]( Pasting disabled )")
                    tried_pasting = False
                if max_len and len(text_to_check) == max_len:
                    toolbar_msgs.append("[b|#000|bg:br:yellow]( Maximum length reached )")
                return _pt.formatted_text.ANSI(FormatCodes.to_ansi(" ".join(toolbar_msgs)))
            except Exception:
                return _pt.formatted_text.ANSI("")

        def process_insert_text(text: str) -> tuple[str, set[str]]:
            removed_chars = set()
            if not text:
                return "", removed_chars
            processed_text = "".join(c for c in text if ord(c) >= 32)
            if allowed_chars != CHARS.ALL:
                filtered_text = ""
                for char in processed_text:
                    if char in allowed_chars:
                        filtered_text += char
                    else:
                        removed_chars.add(char)
                processed_text = filtered_text
            if max_len:
                if (remaining_space := max_len - len(result_text)) > 0:
                    if len(processed_text) > remaining_space:
                        processed_text = processed_text[:remaining_space]
                else:
                    processed_text = ""
            return processed_text, removed_chars

        def insert_text_event(event: KeyPressEvent) -> None:
            nonlocal result_text, filtered_chars
            try:
                if not (insert_text := event.data):
                    return
                buffer = event.app.current_buffer
                cursor_pos = buffer.cursor_position
                insert_text, filtered_chars = process_insert_text(insert_text)
                if insert_text:
                    result_text = result_text[:cursor_pos] + insert_text + result_text[cursor_pos:]
                    if mask_char:
                        buffer.insert_text(mask_char[0] * len(insert_text))
                    else:
                        buffer.insert_text(insert_text)
            except Exception:
                pass

        def remove_text_event(event: KeyPressEvent, is_backspace: bool = False) -> None:
            nonlocal result_text
            try:
                buffer = event.app.current_buffer
                cursor_pos = buffer.cursor_position
                has_selection = buffer.selection_state is not None
                if has_selection:
                    start, end = buffer.document.selection_range()
                    result_text = result_text[:start] + result_text[end:]
                    buffer.cursor_position = start
                    buffer.delete(end - start)
                else:
                    if is_backspace:
                        if cursor_pos > 0:
                            result_text = result_text[:cursor_pos - 1] + result_text[cursor_pos:]
                            buffer.delete_before_cursor(1)
                    else:
                        if cursor_pos < len(result_text):
                            result_text = result_text[:cursor_pos] + result_text[cursor_pos + 1:]
                            buffer.delete(1)
            except Exception:
                pass

        kb = KeyBindings()

        @kb.add(Keys.Delete)
        def _(event: KeyPressEvent) -> None:
            remove_text_event(event)

        @kb.add(Keys.Backspace)
        def _(event: KeyPressEvent) -> None:
            remove_text_event(event, is_backspace=True)

        @kb.add(Keys.ControlA)
        def _(event: KeyPressEvent) -> None:
            buffer = event.app.current_buffer
            buffer.cursor_position = 0
            buffer.start_selection()
            buffer.cursor_position = len(buffer.text)

        @kb.add(Keys.BracketedPaste)
        def _(event: KeyPressEvent) -> None:
            if allow_paste:
                insert_text_event(event)
            else:
                nonlocal tried_pasting
                tried_pasting = True

        @kb.add(Keys.Any)
        def _(event: KeyPressEvent) -> None:
            insert_text_event(event)

        custom_style = Style.from_dict({'bottom-toolbar': 'noreverse'})
        session = _pt.PromptSession(
            message=_pt.formatted_text.ANSI(FormatCodes.to_ansi(str(prompt), default_color=default_color)),
            validator=InputValidator(),
            validate_while_typing=True,
            key_bindings=kb,
            bottom_toolbar=bottom_toolbar,
            placeholder=_pt.formatted_text.ANSI(FormatCodes.to_ansi(f"[i|br:black]{placeholder}[_i|_c]"))
            if placeholder else "",
            style=custom_style,
        )
        FormatCodes.print(start, end="")
        session.prompt()
        FormatCodes.print(end, end="")

        if result_text in ("", None):
            if has_default:
                return default_val
            result_text = ""

        if output_type == str:
            return result_text  # type: ignore[return-value]
        else:
            try:
                return output_type(result_text)  # type: ignore[call-arg]
            except (ValueError, TypeError):
                if has_default:
                    return default_val
                raise


class _ProgressUpdater(Protocol):
    """Protocol for progress update function with proper type hints."""

    @overload
    def __call__(self, current: int) -> None:
        """Update the current progress value."""
        ...

    @overload
    def __call__(self, current: int, label: str) -> None:
        """Update both current progress value and label."""
        ...

    @overload
    def __call__(self, *, label: str) -> None:
        """Update the progress label only (keyword-only)."""
        ...


class ProgressBar:
    """A console progress bar with smooth transitions and customizable appearance.\n
    -------------------------------------------------------------------------------------------------
    - `min_width` -⠀the min width of the progress bar in chars
    - `max_width` -⠀the max width of the progress bar in chars
    - `bar_format` -⠀the format string used to render the progress bar, containing placeholders:
      * `{label}` `{l}`
      * `{bar}` `{b}`
      * `{current}` `{c}`
      * `{total}` `{t}`
      * `{percentage}` `{percent}` `{p}`
    - `limited_bar_format` -⠀a simplified format string used when the console width is too small
    - `chars` -⠀a tuple of characters ordered from full to empty progress<br>
      The first character represents completely filled sections, intermediate
      characters create smooth transitions, and the last character represents
      empty sections. Default is a set of Unicode block characters.
    --------------------------------------------------------------------------------------------------
    The bar format (also limited) can additionally be formatted with special formatting codes. For
    more detailed information about formatting codes, see the `format_codes` module documentation."""

    def __init__(
        self,
        min_width: int = 10,
        max_width: int = 50,
        bar_format: str = "{l} |{b}| [b]({c})/{t} [dim](([i]({p}%)))",
        limited_bar_format: str = "|{b}|",
        chars: tuple[str, ...] = ("█", "▉", "▊", "▋", "▌", "▍", "▎", "▏", " "),
    ):
        self.active: bool = False
        """Whether the progress bar is currently active (intercepting stdout) or not."""
        self.min_width: int
        """The min width of the progress bar in chars."""
        self.max_width: int
        """The max width of the progress bar in chars."""
        self.bar_format: str
        """The format string used to render the progress bar."""
        self.limited_bar_format: str
        """The simplified format string used when the console width is too small."""
        self.chars: tuple[str, ...]
        """A tuple of characters ordered from full to empty progress."""

        self.set_width(min_width, max_width)
        self.set_bar_format(bar_format, limited_bar_format)
        self.set_chars(chars)

        self._buffer: list[str] = []
        self._original_stdout: Optional[TextIO] = None
        self._current_progress_str: str = ""
        self._last_line_len: int = 0

    def set_width(self, min_width: Optional[int] = None, max_width: Optional[int] = None) -> None:
        """Set the width of the progress bar.\n
        --------------------------------------------------------------
        - `min_width` -⠀the min width of the progress bar in chars
        - `max_width` -⠀the max width of the progress bar in chars"""
        if min_width is not None:
            if min_width < 1:
                raise ValueError("Minimum width must be at least 1.")
            self.min_width = max(1, min_width)
        if max_width is not None:
            if max_width < 1:
                raise ValueError("Maximum width must be at least 1.")
            self.max_width = max(self.min_width, max_width)

    def set_bar_format(self, bar_format: Optional[str] = None, limited_bar_format: Optional[str] = None) -> None:
        """Set the format string used to render the progress bar.\n
        --------------------------------------------------------------------------------------------------
        - `bar_format` -⠀the format string used to render the progress bar, containing placeholders:
          * `{label}` `{l}`
          * `{bar}` `{b}`
          * `{current}` `{c}`
          * `{total}` `{t}`
          * `{percentage}` `{percent}` `{p}`
        - `limited_bar_format` -⠀a simplified format string used when the console width is too small
        --------------------------------------------------------------------------------------------------
        The bar format (also limited) can additionally be formatted with special formatting codes. For
        more detailed information about formatting codes, see the `format_codes` module documentation."""
        if bar_format is not None:
            if not _COMPILED["bar"].search(bar_format):
                raise ValueError("'bar_format' must contain the '{bar}' or '{b}' placeholder.")
            self.bar_format = bar_format
        if limited_bar_format is not None:
            if not _COMPILED["bar"].search(limited_bar_format):
                raise ValueError("'limited_bar_format' must contain the '{bar}' or '{b}' placeholder.")
            self.limited_bar_format = limited_bar_format

    def set_chars(self, chars: tuple[str, ...]) -> None:
        """Set the characters used to render the progress bar.\n
        --------------------------------------------------------------------------
        - `chars` -⠀a tuple of characters ordered from full to empty progress<br>
          The first character represents completely filled sections, intermediate
          characters create smooth transitions, and the last character represents
          empty sections. If None, uses default Unicode block characters."""
        if len(chars) < 2:
            raise ValueError("'chars' must contain at least two characters (full and empty).")
        if not all(len(c) == 1 for c in chars if isinstance(c, str)):
            raise ValueError("All 'chars' items must be single-character strings.")
        self.chars = chars

    def show_progress(self, current: int, total: int, label: Optional[str] = None) -> None:
        """Show or update the progress bar.\n
        -------------------------------------------------------------------------------------------
        - `current` -⠀the current progress value (below `0` or greater than `total` hides the bar)
        - `total` -⠀the total value representing 100% progress (must be greater than `0`)
        - `label` -⠀an optional label which is inserted at the `{label}` or `{l}` placeholder"""
        if total <= 0:
            raise ValueError("Total must be greater than 0.")

        try:
            if not self.active:
                self._start_intercepting()
            self._flush_buffer()
            self._draw_progress_bar(current, total, label or "")
            if current < 0 or current > total:
                self.hide_progress()
        except Exception:
            self._emergency_cleanup()
            raise

    def hide_progress(self) -> None:
        """Hide the progress bar and restore normal console output."""
        if self.active:
            self._clear_progress_line()
            self._stop_intercepting()

    @contextmanager
    def progress_context(self, total: int, label: Optional[str] = None) -> Generator[_ProgressUpdater, None, None]:
        """Context manager for automatic cleanup. Returns a function to update progress.\n
        ----------------------------------------------------------------------------------------------------
        - `total` -⠀the total value representing 100% progress (must be greater than `0`)
        - `label` -⠀an optional label which is inserted at the `{label}` or `{l}` placeholder
        ----------------------------------------------------------------------------------------------------
        The returned callable accepts keyword arguments. At least one of these parameters must be provided:
        - `current` -⠀update the current progress value
        - `label` -⠀update the progress label\n

        Example usage:
        ```python
        with ProgressBar().progress_context(500, "Loading...") as update_progress:
            update_progress(0)  # Show empty bar at start

            for i in range(400):
                # Do some work...
                update_progress(i)  # Update progress

            update_progress(label="Finalizing...")  # Update label

            for i in range(400, 500):
                # Do some work...
                update_progress(i, f"Finalizing ({i})")  # Update both
        ```"""
        current_progress = 0
        current_label = label

        try:

            def update_progress(*args, **kwargs) -> None:  # TYPE HINTS DEFINED IN '_ProgressUpdater' PROTOCOL
                """Update the progress bar's current value and/or label."""
                nonlocal current_progress, current_label
                current = label = None

                if len(args) > 2:
                    raise TypeError(f"update_progress() takes at most 2 positional arguments ({len(args)} given)")
                elif len(args) >= 1:
                    current = args[0]
                    if len(args) >= 2:
                        label = args[1]

                if "current" in kwargs:
                    if current is not None:
                        raise TypeError("update_progress() got multiple values for argument 'current'")
                    current = kwargs["current"]
                if "label" in kwargs:
                    if label is not None:
                        raise TypeError("update_progress() got multiple values for argument 'label'")
                    label = kwargs["label"]

                if unexpected := set(kwargs.keys()) - {"current", "label"}:
                    raise TypeError(f"update_progress() got unexpected keyword argument(s): {', '.join(unexpected)}")

                if current is None and label is None:
                    raise TypeError("At least one of 'current' or 'label' must be provided")

                if current is not None:
                    current_progress = current
                if label is not None:
                    current_label = label

                self.show_progress(current_progress, total, current_label)

            yield update_progress
        except Exception:
            self._emergency_cleanup()
            raise
        finally:
            self.hide_progress()

    def _start_intercepting(self) -> None:
        self.active = True
        self._original_stdout = _sys.stdout
        _sys.stdout = _InterceptedOutput(self)

    def _stop_intercepting(self) -> None:
        if self._original_stdout:
            _sys.stdout = self._original_stdout
            self._original_stdout = None
        self.active = False
        self._buffer.clear()
        self._last_line_len = 0
        self._current_progress_str = ""

    def _emergency_cleanup(self) -> None:
        """Emergency cleanup to restore stdout in case of exceptions."""
        try:
            self._stop_intercepting()
        except Exception:
            pass

    def _flush_buffer(self) -> None:
        if self._buffer and self._original_stdout:
            self._clear_progress_line()
            for content in self._buffer:
                self._original_stdout.write(content)
                self._original_stdout.flush()
            self._buffer.clear()

    def _draw_progress_bar(self, current: int, total: int, label: Optional[str] = None) -> None:
        if total <= 0 or not self._original_stdout:
            return
        percentage = min(100, (current / total) * 100)
        formatted, bar_width = self._get_formatted_info_and_bar_width(self.bar_format, current, total, percentage, label)
        if bar_width < self.min_width:
            formatted, bar_width = self._get_formatted_info_and_bar_width(
                self.limited_bar_format, current, total, percentage, label
            )
        bar = self._create_bar(current, total, max(1, bar_width)) + "[*]"
        progress_text = _COMPILED["bar"].sub(FormatCodes.to_ansi(bar), formatted)
        self._current_progress_str = progress_text
        self._last_line_len = len(progress_text)
        self._original_stdout.write(f"\r{progress_text}")
        self._original_stdout.flush()

    def _get_formatted_info_and_bar_width(
        self,
        bar_format: str,
        current: int,
        total: int,
        percentage: float,
        label: Optional[str] = None,
    ) -> tuple[str, int]:
        formatted = _COMPILED["label"].sub(label or "", bar_format)
        formatted = _COMPILED["current"].sub(str(current), formatted)
        formatted = _COMPILED["total"].sub(str(total), formatted)
        formatted = _COMPILED["percentage"].sub(f"{percentage:.1f}", formatted)
        formatted = FormatCodes.to_ansi(formatted)
        bar_space = Console.w - len(FormatCodes.remove_ansi(_COMPILED["bar"].sub("", formatted)))
        bar_width = min(bar_space, self.max_width) if bar_space > 0 else 0
        return formatted, bar_width

    def _create_bar(self, current: int, total: int, bar_width: int) -> str:
        progress = current / total if total > 0 else 0
        bar = []

        for i in range(bar_width):
            pos_progress = (i + 1) / bar_width
            if progress >= pos_progress:
                bar.append(self.chars[0])
            elif progress >= pos_progress - (1 / bar_width):
                remainder = (progress - (pos_progress - (1 / bar_width))) * bar_width
                char_idx = len(self.chars) - 1 - min(int(remainder * len(self.chars)), len(self.chars) - 1)
                bar.append(self.chars[char_idx])
            else:
                bar.append(self.chars[-1])
        return "".join(bar)

    def _clear_progress_line(self) -> None:
        if self._last_line_len > 0 and self._original_stdout:
            self._original_stdout.write(f"{ANSI.CHAR}[2K\r")
            self._original_stdout.flush()

    def _redraw_progress_bar(self) -> None:
        if self._current_progress_str and self._original_stdout:
            self._original_stdout.write(f"{self._current_progress_str}")
            self._original_stdout.flush()


class _InterceptedOutput(_io.StringIO):
    """Custom StringIO that captures output and stores it in the progress bar buffer."""

    def __init__(self, progress_bar: ProgressBar):
        super().__init__()
        self.progress_bar = progress_bar

    def write(self, content: str) -> int:
        try:
            if content and content != "\r":
                self.progress_bar._buffer.append(content)
            return len(content)
        except Exception:
            self.progress_bar._emergency_cleanup()
            raise

    def flush(self) -> None:
        try:
            if self.progress_bar.active and self.progress_bar._buffer:
                self.progress_bar._flush_buffer()
                self.progress_bar._redraw_progress_bar()
        except Exception:
            self.progress_bar._emergency_cleanup()
            raise
