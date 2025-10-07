# Std
from time import sleep
from threading import Thread
from pathlib import Path

# OMGUI
from omgui.context import ctx
from omgui.configuration import config
from omgui import configure
from omgui.util.logger import get_logger

# Logger
logger = get_logger()


def startup():
    """
    Application startup routine.
    """

    # ------------------------------------
    # region - Dependency Checks
    # ------------------------------------

    # Check if [viz] optional dependencies are installed
    # and set config._viz_deps accordingly
    try:
        import plotly  # pylint: disable=unused-import
        import kaleido  # pylint: disable=unused-import
        import cairosvg  # pylint: disable=unused-import

        configure(_viz_deps=True)
        logger.info("Optional [viz] dependencies are installed")
    except ImportError:
        configure(_viz_deps=False)
        logger.warning(
            "Optional [viz] dependencies are not installed - install with `pip install omgui[viz]`"
        )

    # endregion
    # ------------------------------------
    # region - Workspace Setup
    # ------------------------------------

    def _prepare_workspace():
        """
        Make sure workspace exists and load sample files if needed.

        Note: the ._system dir and mws.json file are created by ctx._load_mws()
        """

        # Wait for configure() to have been applied
        sleep(0.1)

        # Create workspace if not existing
        workspace = config().workspace
        workspace_path = ctx().workspace_path()
        if not workspace_path.exists():
            ctx().create_workspace(workspace)

            # Add sample files to workspace
            if config().sample_files:
                _load_sample_files()

        # Set workspace
        else:
            ctx().set_workspace(workspace, silent=True)

        # Add sample files to workspace
        if config().sample_files:
            _load_sample_files()

    def _load_sample_files():
        """
        Load sample files into the current workspace.
        """
        import tarfile

        sample_file = Path(__file__).parent / "gui" / "data" / "samples.tar.gz"
        workspace_path = ctx().workspace_path()

        with tarfile.open(sample_file, "r:gz") as tar_ref:
            tar_ref.extractall(workspace_path)

    Thread(target=_prepare_workspace).start()

    # endregion
    # ------------------------------------
