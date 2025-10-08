from __future__ import annotations
import colorama
from pathlib import Path
import threading
from typing import List, Optional, Tuple, TYPE_CHECKING
from . import util


if TYPE_CHECKING:
    from .util import PathOrStr
    from .actions import Action


class Task:
    """
    Task to be executed.
    """
    def __init__(
            self,
            name: str,
            *,
            dependencies: Optional[List["PathOrStr"]] = None,
            targets: Optional[List["PathOrStr"]] = None,
            action: Optional[Action] = None,
            task_dependencies: Optional[List[Task]] = None,
            location: Optional[Tuple[str, int]] = None,
            ) -> None:
        self.name = name
        self.dependencies = dependencies or []
        self.targets = [Path(path) for path in (targets or [])]
        self.action = action
        self.task_dependencies = task_dependencies or []
        self.location = location or util.get_location()

    def execute(self, stop: Optional[threading.Event] = None) -> None:
        if self.action:
            self.action.execute(self, stop)

    def __hash__(self) -> int:
        return hash(self.name)

    def format(self, color: str = None) -> str:
        name = self.name
        if color:
            name = f"{color}{name}{colorama.Fore.RESET}"
        filename, lineno = self.location
        return f"<task `{name}` @ {filename}:{lineno}>"

    def __repr__(self) -> str:
        return self.format()
