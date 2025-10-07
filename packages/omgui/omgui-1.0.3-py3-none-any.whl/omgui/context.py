"""
OMGUI context manager

By default, a global context file is loaded on startup,
which means that if you switch workspaces, this will
affect all sessions of OMGUI.

You can set the scope to a session-context, which means
that changes to your session context (e.g., switching
workspaces) will not affect the global context or other
sessions. This allows you to work across different
workspaces in parallel.

For now, the context is only used to store your current
workspace. Working set molecules are stored per workspace.

Usage:

    from omgui.context import ctx

    workspace = ctx().workspace
    workspaces = ctx().workspaces()
    ctx().set_workspace("MY_WORKSPACE")
"""

# Std
import json
from pathlib import Path

# OMGUI
from omgui.configuration import config
from omgui.util.logger import get_logger
from omgui.spf import spf

# Logger
logger = get_logger()


def ctx():
    """
    Get the context singleton instance.
    """
    return Context()


def new_session():
    """
    Create a new session-only context.
    """
    Context(session=True)
    spf.success(
        [
            "Session-only context created",
            "Your molecule working set will reset when you exit this session.",
        ]
    )


class Context:
    """
    Context singleton for omgui.
    """

    # Singleton instance
    _instance = None
    _initialized = False

    # Context values
    workspace: str
    session: bool = False  # Session-only context
    vars: dict

    # Default context values
    default_context = {
        "workspace": "DEFAULT",
        "vars": {},
        "session": False,
    }

    # ------------------------------------
    # region - Initialization
    # ------------------------------------

    def __new__(cls, session: bool = None):
        """
        Control singleton instance creation.
        """

        if cls._instance is None or session is True:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, session: bool = None):
        """
        Initializes the context manager.
        """

        # Prevent re-initialization of singleton
        if self._initialized:
            return

        # A: Create virgin session context
        if session:
            _context = self.default_context.copy()
            _context["session"] = True  # Mark as session-only

        # B: Load global context from file
        else:
            _context = self._load_global_context()

        # Set context attributes
        for key, value in _context.items():
            if self.default_context.get(key) is not None:
                setattr(self, key, _context[key])
            else:
                setattr(self, key, value)

        # Make sure workspace exists
        self._create_workspace_dir(self.workspace)

        # Save the context to file
        self._initialized = True
        self.save()

    def _load_global_context(self):
        """
        Loads a saved context file from the data directory.

        Returns:
            dict: The context dictionary, or None if the file is not found.
        """
        try:
            context_path = Path(config().data_dir).expanduser() / "context.json"

            # Load from file
            if context_path.exists():
                with open(context_path, "r", encoding="utf-8") as file:
                    context = json.load(file)
                    return context

            # Fall back to default
            else:
                logger.info("Creating new context file")
                return self.default_context

        except Exception as err:  # pylint: disable=broad-except
            logger.error("An error occurred while loading the context file: %s", err)
            return self.default_context

    # endregion
    # ------------------------------------
    # region - Core
    # ------------------------------------

    def save(self):
        """
        Saves the current context to the context file in the data directory.
        """
        # Session context is not saved to disk
        if self.session:
            return

        try:
            # Save context file, without _private attributes
            ctx_dict = self.__dict__.copy()
            for key in list(ctx_dict.keys()):
                if key.startswith("_"):
                    del ctx_dict[key]
            context_path = Path(config().data_dir).expanduser() / "context.json"
            with open(context_path, "w", encoding="utf-8") as file:
                json.dump(ctx_dict, file, indent=4)

        except Exception as err:  # pylint: disable=broad-except
            logger.error("An error occurred while saving the context file: %s", err)

    def get_dict(self):
        """
        Returns the current context, mainly for debugging purposes.
        """
        return self.__dict__.copy()

    # endregion
    # ------------------------------------
    # region - Workspaces
    # ------------------------------------

    def create_workspace(self, workspace_name):
        """
        Creates a new workspace with the specified name if it doesn't already exist.
        """
        # Create the workspace in the context
        workspace_name = workspace_name.strip().replace(" ", "_").upper()
        if workspace_name in self.workspaces():
            logger.warning("A workspace named '%s' already exists", workspace_name)
            self.set_workspace(workspace_name)
            return
        self.workspace = workspace_name

        # Create the directory
        self._create_workspace_dir(workspace_name)

        self.save()
        spf.success(f"Switched to new workspace: <yellow>{workspace_name}</yellow>")

    def set_workspace(self, workspace_name, silent: bool = False):
        """
        Sets the current workspace to the specified one if it exists.
        """
        # Set the workspace in the context
        workspace_name = workspace_name.strip().replace(" ", "_").upper()
        if workspace_name not in self.workspaces():
            spf.error(
                f"There is no workspace named '<yellow>{workspace_name}</yellow>'"
            )
            return
        self.workspace = workspace_name

        self.save()
        if not silent:
            spf.success(f"Switched to workspace: <yellow>{workspace_name}</yellow>")

    def _create_workspace_dir(self, workspace_name):
        """
        Creates the directory for the specified workspace if it doesn't exist.
        """
        workspace_name = workspace_name.strip().replace(" ", "_").upper()
        workspace_path = self.workspace_path(workspace_name)
        workspace_path_short = self.workspace_path(workspace_name, expanduser=False)
        if not workspace_path.exists():
            try:
                workspace_path.mkdir(parents=True, exist_ok=True)
                spf.success(
                    f"Created new workspace: <yellow>{workspace_path_short}</yellow>"
                )
            except Exception as err:  # pylint: disable=broad-except
                logger.error(
                    "An error occurred while creating the '%s' workspace directory: %s",
                    workspace_name,
                    err,
                )

    def workspace_path(self, workspace=None, expanduser: bool = True):
        """
        Returns the current workspace path.
        """
        data_dir = (
            Path(config().data_dir).expanduser()
            if expanduser
            else Path(config().data_dir)
        )

        return data_dir / "workspaces" / (workspace or self.workspace)

    def workspaces(self):
        """
        Returns the list of workspace names.
        """
        workspaces_path = Path(config().data_dir).expanduser() / "workspaces"
        if workspaces_path.exists():
            return [p.name for p in workspaces_path.iterdir() if p.is_dir()]
        else:
            return []

    # endregion
    # ------------------------------------
