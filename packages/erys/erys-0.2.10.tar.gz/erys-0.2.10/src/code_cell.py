# Copyright 2025 Nathnael (Nati) Bekele
#
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

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import var, reactive
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll
from textual.widgets import Static, Label, ContentSwitcher, Pretty
from textual.events import Key, DescendantBlur, Click

import re
import tempfile
import webbrowser
import base64
from io import BytesIO
from PIL import Image
from rich.text import Text
from typing import Any
from enum import Enum

from .cell import (
    CopyTextArea,
    SplitTextArea,
    Cell,
    StaticBtn,
    COLLAPSED_COLOR,
    EXPANDED_COLOR,
)


class OutputCollapseLabel(Label):
    """Custom label to use as the collapse button for the output of a code cell."""

    collapsed = var(False, init=False)  # keep track of collapse state

    def __init__(self, parent: "CodeCell", collapsed: bool = False, id: str = "") -> None:
        super().__init__("\n┃", id=id)
        self.collapsed = collapsed
        self.parent_cell = parent

    def on_click(self) -> None:
        """Toggle the collapsed state on clicks."""
        self.collapsed = not self.collapsed

    def watch_collapsed(self, collapsed: bool) -> None:
        """Watched method to switch the content from the outputs to the collapsed label.

        Args:
            collapsed: updated collapsed state.
        """
        if collapsed:
            self.parent_cell.output_box.styles.offset = 0, -1
            self.parent_cell.output_switcher.current = "collapsed-output"
            self.styles.color = COLLAPSED_COLOR
        else:
            self.parent_cell.output_box.styles.offset = 0, 0
            self.parent_cell.output_switcher.current = "outputs"
            self.styles.color = EXPANDED_COLOR


class ExecStatus(Enum):
    """Status for code cell execution."""

    IDLE = 0
    QUEUED = 1
    RUNNING = 2
    ERROR = 3


class RunLabel(Label):
    """Custom label used as button for running/interrupting code cell."""

    status: var[ExecStatus] = var(ExecStatus.IDLE, init=False)
    glyphs = {
        ExecStatus.IDLE: "▶",
        ExecStatus.ERROR: "[red 50%]▶[/]",
        ExecStatus.RUNNING: "□",
        ExecStatus.QUEUED: "..",
    }  # glyphs representing running state
    toolips = {
        ExecStatus.IDLE: "Idle: Run",
        ExecStatus.ERROR: "Error: Run",
        ExecStatus.RUNNING: "Running: Interrupt",
        ExecStatus.QUEUED: "Queued: Interrupt",
    }

    def __init__(self, code_cell: CodeCell, id: str = "") -> None:
        super().__init__(self.glyphs[ExecStatus.IDLE], id=id)
        self.tooltip = self.toolips[ExecStatus.IDLE]
        self.code_cell = code_cell

    async def on_click(self) -> None:
        """Button to run or interrupt code cell."""

        if self.status in [ExecStatus.IDLE, ExecStatus.ERROR]:
            await self.code_cell.run_cell()
        elif self.status in [ExecStatus.RUNNING, ExecStatus.QUEUED]:
            self.code_cell.interrupt_cell()

    def watch_status(self, status: ExecStatus) -> None:
        """Watcher method to update the glyph and the tooltip depending on running state.

        Args:
            status: the current execution status for the code cell
        """
        self.update(self.glyphs[status])
        self.tooltip = self.toolips[status]


class CodeArea(SplitTextArea):
    """Widget used for editing code. Inherits from the SplitTextArea."""

    closing_map = {"{": "}", "(": ")", "[": "]", "'": "'", '"': '"'}

    def on_key(self, event: Key) -> None:
        """Key press event handler to close brackets and quotes.

        Args:
            event: Key press event.
        """
        if event.key == "ctrl+r":
            event.stop()
            assert isinstance(self.parent_cell, CodeCell);
            if self.parent_cell.status in [ExecStatus.IDLE, ExecStatus.ERROR]:
                self.run_worker(self.parent_cell.run_cell)
        elif event.character in self.closing_map:
            self.insert(f"{event.character}{self.closing_map[event.character]}")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
            return

        super().on_key(event)


class OutputJson(HorizontalGroup):
    """Widget for displaying application/json output_type."""

    can_focus = True  # Make the widget focusable

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.output_text = OutputText(str(self.data), id="plain-json")

    def compose(self) -> ComposeResult:
        """Composed of
        - Content switcher (initial=pretty-json)
            - Pretty (id=pretty-json)
            - CopyTextArea (id=plain-json)
        """
        self.switcher = ContentSwitcher(initial="pretty-json")
        with self.switcher:
            yield Pretty(self.data, id="pretty-json")
            yield self.output_text

    def _on_focus(self, event) -> None:
        """Switch to plain-json when focusing on widget."""
        self.switcher.current = "plain-json"

    def on_descendant_blur(self, event: DescendantBlur) -> None:
        """Switch to pretty-json when bluring away from descendants."""
        self.switcher.current = "pretty-json"

    def _on_blur(self, event) -> None:
        """Swtich to the pretty-json when bluring away from widget unless new focused widget is
        the plain-json.
        """
        if not self.app.focused or self.app.focused != self.output_text:
            self.switcher.current = "pretty-json"


class OutputText(CopyTextArea):
    """Widget for displaying stream/plain error outputs"""

    read_only = reactive(True)  # make text area read only

    def _on_focus(self, event) -> None:
        """Add border when focused."""
        self.styles.border = "solid", "gray"

    def _on_blur(self, event) -> None:
        """Remove border when focused."""
        self.styles.border = None


class OutputImage(HorizontalGroup):
    """Widget for displaying image/png output for code cells."""

    can_focus = True

    def __init__(self, base64_data: str, metadata: dict[str, int]) -> None:
        super().__init__()
        # image from kernel is returned as a base64 encoded data
        self.base64_data = base64_data
        self.decoded = BytesIO(base64.b64decode(base64_data))
        self.image = Image.open(self.decoded)

        self.display_img_btn = StaticBtn(
            content="🖼 Img", id="display-img-btn"
        ).with_tooltip("Press to display image")

    def compose(self) -> ComposeResult:
        """Composed with:
        - HorizontalGroup
            - ImageStaticBtn (id=display-img-btn)
        """
        yield self.display_img_btn

    def on_click(self, event: Click):
        """Method to display the image when `StaticBtn` is clicked. Called from `StaticBtn` when it
        is clicked.

        Args:
            event: the original click event from the `StaticBtn`.
        """
        if event.widget == self.display_img_btn:
            self.image.show()
            event.stop()


class OutputHTML(HorizontalGroup):
    """Widget for displaying html output for code cells."""

    can_focus = True

    def __init__(self, data: list[str] | str) -> None:
        super().__init__()
        # image from kernel is returned as a base64 encoded data
        if isinstance(data, list):
            self.data = "".join(data)
        else:
            self.data = data

        self.display_img_btn = StaticBtn(
            content="🖼 HTML", id="display-html-btn"
        ).with_tooltip("Press to display image")

    def compose(self) -> ComposeResult:
        """Composed with:
        - HorizontalGroup
            - ImageStaticBtn (id=display-html-btn)
        """
        yield self.display_img_btn

    def on_click(self, event: Click):
        """Method to display html when `StaticBtn` is clicked. Called from `StaticBtn` when it
        is clicked.

        Args:
            event: the original click event from the `StaticBtn`.
        """
        if event.widget == self.display_img_btn:
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
                f.write(self.data)
                url = "file://" + f.name

            # Open in default browser
            webbrowser.open(url)
            event.stop()


class OutputAnsi(VerticalScroll):
    """Widget for displaying ansi output for code cells."""

    can_focus = True  # make widget focusable

    def __init__(self, ansi_string: list[str] | str) -> None:
        super().__init__()
        if isinstance(ansi_string, list):
            text = "\n".join(ansi_string)
        else:
            text = ansi_string

        self.plain_string = self.remove_ansi(text)  # remove the ansi
        self.pretty_string = Text.from_ansi(text)  # convert ansi to markup

        self.static_output = Static(content=self.pretty_string, id="pretty-output")
        self.text_output = OutputText(text=self.plain_string, id="plain-output")

    def compose(self) -> ComposeResult:
        """Composed of
        - HorizontalGroup
            - Content switcher (initial=pretty-output)
                - Pretty (id=pretty-output)
                - CopyTextArea (id=plain-output)
        """
        self.switcher = ContentSwitcher(initial="pretty-output")
        with self.switcher:
            yield self.static_output
            yield self.text_output

    def _on_focus(self, event) -> None:
        """Switch to plain-output when focusing on widget."""
        self.switcher.current = "plain-output"

    def on_descendant_blur(self, event: DescendantBlur) -> None:
        """Switch to pretty-output when bluring away from descendants."""
        self.switcher.current = "pretty-output"

    def _on_blur(self, event) -> None:
        """Swtich to the pretty-output when bluring away from widget unless new focused
        widget is the plain-output.
        """
        if not self.app.focused or self.app.focused != self.text_output:
            self.switcher.current = "pretty-output"

    def remove_ansi(self, ansi_escaped_string: str) -> str:
        """Returns the strings with ansi escapes removed using regex. Used to remove color from
        code execution outputs.

        Args:
            ansi_escaped_string: input string containing ansi escapes.

        Returns: string without ansi escapes.
        """
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        return ansi_escape.sub("", ansi_escaped_string)


class CodeCell(Cell):
    """Widget to contain code cells in a notebook"""

    BINDINGS = [
        ("ctrl+r", "run_cell", "Run Cell"),
    ]
    exec_count: var[int | None] = var(None, init=False)
    # Reactive to keep track of the execution count
    cell_type = "code"

    def __init__(
        self,
        notebook,
        source: str = "",
        outputs: list[dict[str, Any]] = [],
        exec_count: int | None = None,
        metadata: dict[str, Any] = {},
        cell_id: str | None = None,
        language: str = "Python",
    ) -> None:
        super().__init__(notebook, source, language, metadata, cell_id)
        self.outputs: list[dict[str, Any]] = outputs
        self.exec_count = exec_count
        self.switcher = ContentSwitcher(id="collapse-content", initial="text")

        self.run_label = RunLabel(self, id="run-button")
        self.exec_count_display = Static(f"[{self.exec_count or ' '}]", id="exec-count")

        self.input_text = CodeArea._code_editor(
            self,
            self.source,
            language=self._language.lower(),
            id="text",
            soft_wrap=True,
            theme="vscode_dark",
        )

        self.output_collapse_btn = OutputCollapseLabel(
            self,
            id="output-collapse-button"
        ).with_tooltip("Collapse Output")

        self.outputs_group = VerticalGroup(id="outputs")
        self.output_switcher = ContentSwitcher(id="collapse-outputs", initial="outputs")
        self.output_box = HorizontalGroup(id="output-section")

    def compose(self) -> ComposeResult:
        """Compose with:
        - VerticalGroup
            - HorziontalGroup
                - HorizontalGroup (id=code-sidebar)
                    - CollapseLabel (id=collapse-button)
                    - VerticalGroup:
                        - RunLabel (id=run-button)
                        - Static (id=exec-count)
                - ContentSwitcher (id=collapse-content)
                    - CodeArea (id=text)
                    - Static (id=collapsed-display)
            - HorizontalGroup (id=output-section)
                - OutputCollapseLabel (id=output-collapse-button)
                - ContentSwitcher (id=collapse-outputs)
                    - VerticalGroup (id=outputs)
                    - Static (id=collapsed-output)
        """
        with HorizontalGroup():
            with HorizontalGroup(id="code-sidebar"):
                yield self.collapse_btn
                with VerticalGroup():
                    yield self.run_label
                    yield self.exec_count_display
            with self.switcher:
                yield self.input_text
                yield self.collapsed_display

        with self.output_box:
            yield self.output_collapse_btn
            with self.output_switcher:
                yield self.outputs_group
                yield Static("Outputs are collapsed...", id="collapsed-output")

    def on_mount(self):
        """On mount, toggle the display for the output collapse button if there are outputs and
        display the outputs.
        """
        self.call_after_refresh(self.update_outputs, self.outputs)

    def escape(self, event: Key):
        """Event handler to be called when the escape key is pressed."""
        self.focus()
        event.stop()

    def watch_exec_count(self, new: int | None) -> None:
        """Watcher for the execution count to update the value of the Static widget when it changes."""
        self.call_after_refresh(
            lambda: self.exec_count_display.update(f"[{new or ' '}]")
        )

    def action_run_cell(self) -> None:
        """Calls the `run_cell` function."""
        self.run_worker(self.run_cell)

    def action_collapse(self) -> None:
        """Collapse the code cell. If the outputs or the code cell is not collapsed,
        collapse it; otherwise, toggle the collapsed state.
        """
        if not self.collapse_btn.collapsed or not self.output_collapse_btn.collapsed:
            self.collapse_btn.collapsed = True
            self.output_collapse_btn.collapsed = True
        else:
            self.collapse_btn.collapsed = not self.collapse_btn.collapsed
            self.output_collapse_btn.collapsed = not self.output_collapse_btn.collapsed

    async def open(self) -> None:
        """Defines what it means to open a code cell. Focus on the input_text widget."""
        if self.collapse_btn.collapsed:
            self.collapse_btn.collapsed = False
        self.call_after_refresh(self.input_text.focus)

    @staticmethod
    def from_nb(nb: dict[str, Any], notebook) -> "CodeCell":
        """Static method to generate a `CodeCell` from a json/dict that represent a code cell.

        Args:
            nb: the notebook json/dict format of the code cell.
            notebook: the `Notebook` object the code cell belongs too.

        Returns: `CodeCell` from notebook format.

        Raises:
            AssertionError: if no notebook or bad notebook representation.
        """
        # need to have a notebook object and a notebook format
        assert nb
        assert notebook
        # needs to be a valid notebook representation
        for key in ["cell_type", "execution_count", "metadata", "source", "outputs"]:
            assert key in nb
        assert nb["cell_type"] == "code"

        source = nb["source"]
        if isinstance(source, list):
            # join the strings if the input was a multiline string
            source = "".join(source)

        return CodeCell(
            source=source,
            outputs=nb["outputs"],
            exec_count=nb["execution_count"],
            metadata=nb["metadata"],
            cell_id=nb.get("id", None),
            notebook=notebook,
        )

    def to_nb(self) -> dict[str, Any]:
        """Serialize the `CodeCell` to notebook format. Format for code cell:
            {
                "cell_type" : "code",
                "execution_count": 1, # integer or null
                "metadata" : {
                    "collapsed" : True, # whether the output of the cell is collapsed
                    "autoscroll": False, # any of true, false or "auto"
                },
                "source" : ["some code"],
                "outputs": [{
                    # list of output dicts (described below)
                    "output_type": "stream",
                    ...
                }],
            }

        Returns: serialized code cell representation.
        """
        return {
            "cell_type": "code",
            "execution_count": self.exec_count,
            "id": self._cell_id,
            "metadata": self._metadata,
            "outputs": self.outputs,
            "source": self.input_text.text,
        }

    def create_cell(self, source: str) -> "CodeCell":
        """Returns a `CodeCell` with a source. Used for splitting code cell."""
        return CodeCell(notebook=self.notebook, source=source)

    def clone(self, connect: bool = True) -> "CodeCell":
        """Clone a code cell. Used for cut/paste.

        Args:
            connect: whether to keep the pointers to the next and previous cells.

        Returns: cloned code cell.
        """
        clone = CodeCell(
            notebook=self.notebook,
            source=self.input_text.text,
            outputs=self.outputs,
            exec_count=self.exec_count,
            metadata=self._metadata,
            cell_id=self._cell_id,
            language=self._language,
        )
        if connect:
            clone.next = self.next
            clone.prev = self.prev

        return clone

    def handle_output(self, output: dict[str, Any]) -> None:
        match output["output_type"]:
            case "execute_input":
                # {
                #   'msg_type' : "stream",
                #   'code' : str,  # Source code to be executed, one or more lines
                #   'execution_count' : int
                # }
                self.exec_count = output["execution_count"]
            case "stream":
                # join the strings and display them in the `OutputAnsi` widget
                # {
                #   "msg_type" : "stream",
                #   "name" : "stdout", # or stderr
                #   "text" : ["multiline stream text"],
                # }
                self.outputs_group.mount(OutputAnsi(output["text"]))
            case "error":
                # display the errors with the `OutputAnsi` widget
                # {
                #   "msg_type" : "error",
                #   'ename' : str,   # Exception name, as a string
                #   'evalue' : str,  # Exception value, as a string
                #   'traceback' : list,
                # }
                self.outputs_group.mount(OutputAnsi(output["traceback"]))
                self.status = ExecStatus.ERROR
            case "execute_result" | "display_data":
                # the display_data and output_result have different formats
                # {
                #   "msg_type" : "execute_result" | "display_data",
                #   "execution_count": 42, # if "execute_result"
                #   "data" : {
                #     "text/plain" : ["multiline text data"],
                #     "image/png": ["base64-encoded-png-data"],
                #     "application/json": {
                #       # JSON data is included as-is
                #       "json": "data",
                #     },
                #   },
                #   "metadata" : {
                #     "image/png": {
                #       "width": 640,
                #       "height": 480,
                #     },
                #   },
                # }
                for type, data in output["data"].items():
                    match type:
                        case "text/plain":
                            # plain text can also use the `OutputAnsi` widget for display
                            self.outputs_group.mount(OutputAnsi(data))
                        case "application/json":
                            # json is displayed with the `OutputJson` widget
                            self.outputs_group.mount(OutputJson(data))
                        case "image/png":
                            # display the images with the `OutputImage` widget
                            metadata = output["metadata"]
                            self.outputs_group.mount(OutputImage(data, metadata))
                        case "text/html":
                            # display the html douput with the `OutputHTHML` widget
                            self.outputs_group.mount(OutputHTML(data))

    async def update_outputs(self, outputs: list[dict[str, Any]]) -> None:
        """Generate the widgets to store the different output types that result from running
        code cell.

        Args:
            outputs: list of serialized outputs.
        """
        # remove the children widgets first
        await self.outputs_group.remove_children()

        self.output_collapse_btn.display = len(outputs) > 0
        for output in outputs:
            self.handle_output(output)

        self.refresh()

    @property
    def status(self) -> ExecStatus:
        return self.run_label.status

    @status.setter
    def status(self, status: ExecStatus) -> None:
        self.run_label.status = status

    async def run_cell(self) -> None:
        """Run code in code cell with the kernel in a thread. Update the outputs and the
        execution count for the cell.
        """
        # check if there is a kernel for the notebook
        if not self.notebook._is_kernel_connected():
            return

        self.status = ExecStatus.QUEUED
        self.notebook._exec_queue.enqueue(self)
        self.status = ExecStatus.IDLE

    def interrupt_cell(self) -> None:
        """Interrupt kernel when running cell."""

        if not self.notebook._is_kernel_connected():
            return

        self.notebook.interrupt_exec()
