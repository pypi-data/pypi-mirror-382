"""
SPF / Styled Printing and Feedback
----------------------------------

Lightweight styling library to style/color text and dataframe
output for the terminal, Jupyter Notebook and API.

Style text using XML-like tags like <red>, <bold>, <underline>, etc.
These will then be converted to ANSI escape codes for terminal output,
to basic HTML for Jupyter Notebooks, and stripped out for API output.

Dataframes are displayed and paginated and with opinionated styling in
the terminal.

Both the main module and the table submodule have three core methods:

print()
    Print the styled text/table to the terminal or Jupyter Notebook cell.

produce()
    Return the styled text/table.

result()
    Print in terminal mode, return as Markdown/df in notebook mode and as
    plain text/JSON in api mode. This is useful for functions which may be
    called from either a script, Notebook or API.


Usage:

    import spf

    # Set the mode
    # (optional, Notebook is auto-detected by default)
    # ---
    spf.set_mode("api") # terminal, notebook, api


    # ------------------------------------
    # Styling text
    # ------------------------------------


    # Simple styled print
    # ---
    spf("<cyan>Hello <bold>World</bold></cyan>")


    # Success, warning and error messages
    # ---
    spf.success("Hello World") # green
    spf.warning("Hello World") # yellow
    spf.error("Hello World")   # red


    # Returning styled text
    # ---
    x = spf.produce("Hello <bold>World</bold>")
    print(x)


    # ------------------------------------
    # Tables
    # ------------------------------------


    # Print paginated table data
    # ---
    spf.table(df)

    # Return table data for further processing
    # ---
    x = spf.table.produce(df)
    print(x)


    # ------------------------------------
    # Returning results
    # ------------------------------------


    def get_text():
        text = ...
        return spf.result(text)

    def get_data():
        df = ...
        return spf.table.result(df)


Under the hood:

    The style_parser module takes care of parsing xml tags into ANSI
    escape codes, which lets us print different colors in the CLI.
    It also takes care of some extra layout fluff, like padding,
    indentation, etc. The main functions are style() and print_s()
    which return & print styled text respectively. Please refer to
    the style_parser documentation for more details on how to style text.
"""

# pylint: disable=missing-function-docstring

# Std
import sys
import math
import shutil
from typing import Literal

# 3rd party
import pandas
from tabulate import tabulate
from IPython.display import Markdown, display, clear_output

# Local
from .style_parser import style, print_s, strip_tags, tags_to_markdown


# ------------------------------------
# Typing
# ------------------------------------


class Mode:
    """
    Styling mode.

    terminal: Use ANSI chars for terminal
    notebook: Use basic HTML for Jupyter Notebook
    api:      Plain text for API returns
    """

    TERMINAL: str = "terminal"
    NOTEBOOK: str = "notebook"
    API: str = "api"


StatusTp = Literal["error", "warning", "success"] | None
MsgTp = str | list[str]


# ------------------------------------
# Main class
# ------------------------------------


class SPF:
    """
    Main class to handle styled printing and table display.
    """

    _instance = None
    _initialized = False
    max_print_width = 120

    # ------------------------------------
    # region - Public
    # ------------------------------------

    def __new__(cls):
        """
        Control singleton instance creation.
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, mode: Mode | None = None):
        # Prevent re-initialization of singleton
        if self._initialized:
            return
        self._initialized = True

        # Register sub-classes
        self.table = self.Table(self)
        self.util = self.Util(self)

        # Set or detect mode
        if mode is not None:
            self.mode = mode
        elif self.util.nb_mode():
            self.mode = Mode.NOTEBOOK
        else:
            self.mode = Mode.TERMINAL

    def __call__(self, msg, status: StatusTp = None, **kwargs):
        """
        Print styled text.
        """
        return self.print(msg, status, **kwargs)

    def set_mode(self, mode: Mode):
        """
        Set the styling mode.
        """
        if mode in (Mode.TERMINAL, Mode.NOTEBOOK, Mode.API):
            self.mode = mode
        else:
            raise ValueError(f"Invalid mode '{mode}'")

    def print(self, msg, status: StatusTp = None, **kwargs):
        """
        Print styled text.

        Called via __call__, not used directly.
        """
        output = self._render(msg, status, **kwargs)
        if self.mode == Mode.NOTEBOOK:
            display(output)
        else:
            print(output)

    def produce(self, msg, status: StatusTp = None, **kwargs):
        """
        Return styled text.
        """
        output = self._render(msg, status, **kwargs)
        return output

    def result(self, msg, status: StatusTp = None, **kwargs):
        """
        Return or print the result of a function.

        Modes:
            terminal       --> print output
            notebook       --> return output
            api            --> return output

        Jupyter Notebooks print the returned value by default,
        unless it's stored in a variable. Plain mode is assumed
        to be for an API call, hence we return.
        """
        output = self._render(msg, status, **kwargs)
        if self.mode == Mode.TERMINAL:
            print(output)
        else:
            return output

    def success(self, msg, **kwargs):
        """
        Print styled text, preformatted as a success message.
        """
        if isinstance(msg, list) and len(msg) > 0:
            msg[0] = f"✅ {msg[0]}"
        elif isinstance(msg, str):
            msg = f"✅ {msg}"
        self.print(msg, "success", **kwargs)

    def warning(self, msg, **kwargs):
        """
        Print styled text, preformatted as a warning message.
        """
        if isinstance(msg, list) and len(msg) > 0:
            msg[0] = f"⚠️  {msg[0]}"
        elif isinstance(msg, str):
            msg = f"⚠️  {msg}"
        self.print(msg, "warning", **kwargs)

    def error(self, msg, **kwargs):
        """
        Print styled text, preformatted as an error message.
        """
        if isinstance(msg, list) and len(msg) > 0:
            msg[0] = f"❌ {msg[0]}"
        elif isinstance(msg, str):
            msg = f"❌ {msg}"
        self.print(msg, "error", **kwargs)

    # endregion
    # ------------------------------------
    # region - Rendering
    # ------------------------------------

    def _render(self, msg: MsgTp, status: StatusTp = None, **kwargs):
        """
        Render styled text according to the relevant mode.
        """
        if self.mode == Mode.TERMINAL:
            return self.__render_terminal(msg, status, **kwargs)
        elif self.mode == Mode.NOTEBOOK:
            return self.__render_notebook(msg, status)
        elif self.mode == Mode.API:
            return self.__render_plain(msg)

    def __render_terminal(self, msg: MsgTp, status: StatusTp = None, **kwargs) -> str:
        msg: str = self._preformat(msg, status)
        return style(msg, **kwargs)

    def __render_notebook(self, msg: MsgTp, status: StatusTp = None) -> Markdown:
        msg: str = self._preformat(msg, status)
        return Markdown(tags_to_markdown(msg))

    def __render_plain(self, msg: MsgTp, status: StatusTp = None) -> str:
        msg = strip_tags(msg)
        msg: str = self._preformat_plain(msg, status)
        return msg

    def _preformat(self, msg: MsgTp, status: StatusTp = None) -> str:
        """
        Pre-format text with xml tags for terminal/Jupyter output.

        When the message is a list of strings, the first string either
        remains untouched or gets wrapped in the appropriate status tag
        (when specified) while all subsequent strings get wrapped in <soft>
        """
        if isinstance(msg, list):
            msg = "\n".join(
                [
                    (
                        f"<soft>{string}</soft>"
                        if i > 0
                        else (f"<{status}>{string}</{status}>" if status else string)
                    )
                    for i, string in enumerate(msg)
                ]
            )
        else:
            msg = f"<{status}>{msg}</{status}>" if status else msg

        return msg

    def _preformat_plain(self, msg: MsgTp, status: StatusTp = None) -> str:
        """
        Pre-format text for plain output.

        When the message is a list of strings, they get joined with linebreaks.
        When a status is specified, the first line gets prefixed with the status
        in uppercase.
        """
        if isinstance(msg, list):
            msg = "\n".join(msg)
        return f"{status.upper()}: {msg}"

    # endregion
    # ------------------------------------
    # region - Tables
    # ------------------------------------

    class Table:
        """
        Sub-class to handle dataframe printing & producing.
        """

        def __init__(self, parent):
            self.parent = parent

        def __call__(self, *args, **kwargs):
            """
            Print a table.
            """
            self.print(*args, **kwargs)

        def print(self, df, footnote=None, show_index=False):
            """
            Print a table.
            Modes:
                terminal       --> print interactive paginated table
                notebook       --> display dataframe
                api            --> print api dataframe
            """
            if df.empty:
                self.parent.error("No data to display")
                return

            # Prep
            df = self._prep(df, show_index)
            footnote = f"<soft>{footnote}</soft>" if footnote else None

            # Terminal -> Print interactive paginated table
            if self.parent.mode == Mode.TERMINAL:
                lines_header, lines_body = self._format(df)
                self._print_paginated(lines_header, lines_body, exit_msg=footnote)

            # Notebook -> Display dataframe
            elif self.parent.mode == Mode.NOTEBOOK:
                self._format(df)
                display(df)
                if footnote:
                    display(Markdown(tags_to_markdown(footnote)))

            # API -> Nothing to print
            elif self.parent.mode == Mode.API:
                # print(df.data.to_string())
                pass

        def produce(self, df, show_index=False):
            """
            Return a table.

            Modes:
                terminal       --> return tabulate table
                notebook       --> return dataframe
                api           --> return dict
            """
            if df.empty:
                return None

            # Prep
            df = self._prep(df, show_index)

            # Terminal -> return tabulate table
            if self.parent.mode == Mode.TERMINAL:
                lines_header, lines_body = self._format(df)
                table_tabulate = "\n".join(lines_header + lines_body)
                return table_tabulate

            # Notebook -> return dataframe
            elif self.parent.mode == Mode.NOTEBOOK:
                self._format(df)
                return df

            # Plain -> return dict
            elif self.parent.mode == Mode.API:
                return df.to_dict(orient="records")

        def result(self, df, footnote=None, show_index=False):
            """
            Return or print the table result of a function.

            Modes:
                terminal --> print output
                notebook --> return output
                api      --> return output

            Jupyter Notebooks print the returned value by default,
            unless it's stored in a variable. API mode is assumed
            to be for an API call, hence we return.
            """
            if self.parent.mode == Mode.TERMINAL:
                self.print(df, footnote, show_index)
            else:
                return self.produce(df, show_index)

        def _prep(self, df, show_index=False):
            """
            Prepare dataframe for display.
            """

            # Ensure df is a dataframe styler object
            if hasattr(df, "style"):
                df = df.style

            # Hide index column by default
            if not show_index:
                df.hide(axis="index")

            return df

        def _format(self, df):
            """
            Format data for terminal.
            """
            if self.parent.mode == Mode.NOTEBOOK:
                pandas.set_option("display.max_colwidth", None)
            elif self.parent.mode == Mode.TERMINAL:
                lines_header, lines_body = self._format_terminal(df)
                return lines_header, lines_body

        def _format_terminal(self, df):
            """
            Format data for terminal.
            """

            # Check if table has headers and measure its lineheight
            has_headers = False
            header_height = 0
            if len(df.columns) > 0:
                has_headers = isinstance(df.columns[0], str)
                if has_headers:
                    for column in df.columns:
                        height = len(column.splitlines())
                        if height > header_height:
                            header_height = height

            # Remove the default numeric header when no columns are set
            tabulate_headers = "keys" if has_headers else []

            # Convert dataframe to tabulate table
            table_tabulate = tabulate(
                df.data,
                headers=tabulate_headers,
                tablefmt="simple",
                showindex=False,
                numalign="right",
            )

            # Separate header from body so header can be repeated
            output_lines = table_tabulate.split("\n")
            lines_header = output_lines[: header_height + 1]
            lines_body = output_lines[header_height + 1 :]

            # Color separator(s) yellow
            sep_top = lines_header[len(lines_header) - 1]
            sep_top = style(f"<yellow>{sep_top}</yellow>", nowrap=True)
            lines_header = lines_header[:-1] + [sep_top]
            if not has_headers:
                sep_btm = lines_body[len(lines_body) - 1]
                sep_btm = style(f"<yellow>{sep_btm}</yellow>", nowrap=True)
                lines_body = lines_body[:-1] + [sep_btm]

            # Crop table if it's wider than the terminal
            max_row_length = max(
                list(map(lambda row: len(row), table_tabulate.splitlines()))
            )
            cli_width = self.parent.util.get_print_width(full=True)
            if max_row_length > cli_width:
                for i, line in enumerate(table_tabulate.splitlines()):
                    if i == 1:
                        table_tabulate = table_tabulate.replace(line, line[:cli_width])
                    elif len(line) > cli_width:
                        # Update with reset ANSI code \u001b[0m for color tags which may be found later
                        table_tabulate = table_tabulate.replace(
                            line, line[: cli_width - 3] + "...\u001b[0m"
                        )

            return lines_header, lines_body

        def _print_paginated(self, lines_header, lines_body, exit_msg=None):
            """
            Print an interactive, paginated table in the terminal.
            """

            table_tabulate = "\n".join(lines_header + lines_body)

            # Calculate table width
            table_width = 0
            output_lines = table_tabulate.split("\n")
            for line in output_lines:
                if len(line) > table_width:
                    table_width = len(line)

            # Print one page at a time
            row_cursor = 0
            skip = 0
            print("")  # Padding on top
            while row_cursor < len(output_lines):
                # Minus 3 lines for bottom ellipsis, separator and pagination
                max_rows = shutil.get_terminal_size().lines - len(lines_header) - 3

                # Print header + separator
                if row_cursor == 0:
                    row_cursor += len(lines_header)
                else:
                    print("")
                print("\n".join(lines_header))

                # Print body
                i = 0
                while i < max_rows and row_cursor < len(output_lines):
                    print(lines_body[skip + i])
                    i = i + 1
                    row_cursor = row_cursor + 1
                skip = skip + i

                # Print pagination
                if row_cursor < len(output_lines):
                    total_pages = math.ceil(len(output_lines) / max_rows)
                    page = math.floor(row_cursor / max_rows)

                    try:
                        print("...")
                        self.parent.util.separator("yellow", table_width)
                        input(
                            style(
                                f"<yellow>Page {page}/{total_pages}</yellow> - Press <reverse> ENTER </reverse> to load the next page, or <reverse> ctrl+C </reverse> to exit."
                            )
                        )

                        # (wait for input...)

                        self.parent.util.remove_lines(3)
                    except KeyboardInterrupt:
                        print()  # Start a new line
                        self.parent.util.remove_lines(2)
                        if exit_msg:
                            print_s("\n" + exit_msg)
                        return

                # Print exit message
                else:
                    if exit_msg:
                        print_s("\n" + exit_msg)

            print("")  # Padding on bottom

    # endregion
    # ------------------------------------
    # region - Util
    # ------------------------------------

    class Util:
        """
        Utility functions.
        """

        def __init__(self, parent):
            self.parent = parent

        def get_print_width(self, full=False):
            """
            Returns the available print width of the terminal,
            or a fixed value of 120 for notebook/api modes.
            """
            # Notebook - fixed value
            if self.parent.mode == Mode.NOTEBOOK or self.parent.mode == Mode.API:
                return 120
            else:
                try:
                    # Terminal -- Full width
                    if full:
                        return shutil.get_terminal_size().columns

                    # Terminal -- Capped print width
                    else:
                        # We return the terminal width -10 so there's always room for
                        # output with edge (5 chars) and some padding on the right.
                        return min(
                            shutil.get_terminal_size().columns - 10,
                            self.parent.max_print_width,
                        )
                except Exception:  # pylint: disable=broad-exception-caught
                    return self.parent.max_print_width

        def separator(self, style_tag=None, width=None):
            """
            returns a terminal-wide separator.
            """

            if self.parent.mode == Mode.TERMINAL:
                cli_width = self.get_print_width(full=True)
                width = cli_width if not width or cli_width < width else width
                line_str = f"{'-' * width}"
                line_str = (
                    f"<{style_tag}>{line_str}</{style_tag}>" if style_tag else line_str
                )
                return self.parent.produce(line_str, nowrap=True)

        def remove_lines(self, count=1):
            """
            Remove the last printed line(s) from the CLI.
            """
            # Jupyter
            # We can't clear a single line, only the entire cell output
            if self.parent.mode == Mode.NOTEBOOK:
                clear_output(wait=True)

            # Terminal
            else:
                while count > 0:
                    count -= 1
                    sys.stdout.write("\033[F")  # Move the cursor up one line
                    sys.stdout.write("\033[K")  # Clear the line
                    sys.stdout.flush()  # Flush the output buffer

        def nb_mode(self) -> bool:
            """
            Checks if the script is running inside a Jupyter Notebook or Lab.
            """
            try:
                # Import the kernel app, which is unique to Jupyter
                from IPython import get_ipython

                # Check for the presence of the 'IPKernelApp' class
                if "IPKernelApp" in get_ipython().config:
                    return True
                else:
                    return False
            except (ImportError, AttributeError):
                # The above will fail if get_ipython is not available or not a kernel
                return False

    # endregion
    # ------------------------------------
