"""
Configuration options for the omgui library.

Configuration settings order of priority:
    1. Programatically via omgui.configure()
    2. Environment variables (OMGUI_*)
    3. Configuration file (omgui.config.yml)
    4. Default values

Usage:
    from omgui import config

    if config.prompt:
        ...
"""

# Std
import os
from pathlib import Path

# 3rd party
import yaml

# OMGUI
from omgui.spf import spf
from omgui.util.logger import get_logger, set_log_level


logger = get_logger()


def config():
    """
    Get the config singleton instance.
    """
    return Config()


def configure(
    app_name: str | None = None,
    host: str | None = None,
    port: int | None = None,
    session: bool | None = None,
    workspace: str | None = None,
    log_level: str | None = None,
    stateless: bool | None = None,
    # Advanced:
    base_path: str | None = None,
    redis_url: str | None = None,
    data_dir: str | None = None,
    prompt: bool | None = None,
    sample_files: bool | None = None,
    _viz_deps: bool | None = None,
) -> None:
    """
    Optional config options to be set right after import.

    This will update config with the provided values.
    See configuration.py for details.
    """

    if app_name:
        config().set("app_name", app_name)

    if host:
        config().set("host", host)

    if port:
        config().set("port", port)

    if session:
        from omgui import context

        config().set("session", True)
        context.new_session()

    if workspace:
        # Note: workspace gets created in startup()
        config().set("workspace", workspace)

    if log_level:
        config().set("log_level", log_level)
        set_log_level(log_level)

    if stateless:
        config().set("stateless", stateless)

    # -- Advanced --

    if base_path:
        config().set("base_path", base_path)

    if redis_url:
        config().set("redis_url", redis_url)

    if data_dir:
        config().set("data_dir", data_dir)

    if prompt:
        config().set("prompt", prompt)

    if sample_files is not None:
        config().set("sample_files", sample_files)

    if _viz_deps is not None:
        config().set("_viz_deps", _viz_deps)

    # Re-initialize config to apply changes
    config().re_init()


class Config:
    """
    Configuration singleton for omgui.

    Every option corresponds to an environment variable
    in SCREAMING_SNAKE_CASE.

    Priorities (high to low):
        1. omgui.configure() during runtime
        2. Environment variables (OMGUI_*)
        3. Configuration file (omgui.config.yml)
        4. Default values

    For option descriptions, please consult:
    /docs/config.md


    Option         Type   Default       Env variable
    ------------------------------------------------------
    session        bool   False         OMGUI_SESSION
    prompt         bool   True          OMGUI_PROMPT
    workspace      str    "DEFAULT"     OMGUI_WORKSPACE
    data_dir       str    "~/.omgui"    OMGUI_DATA_DIR
    host           str    "localhost"   OMGUI_HOST
    port           int    8024          OMGUI_PORT
    base_path      str    ""            OMGUI_BASE_PATH
    sample_files   bool   True          OMGUI_SAMPLE_FILES
    log_level      str    "INFO"        OMGUI_LOG_LEVEL
    ------------------------------------------------------

    System flags
    ------------
    _viz_deps: bool, default False / .env: n/a
        Whether the optional visualization dependencies are installed.
        This is automatically set to True when the required dependencies
        are detected, and should not be set manually.
    """

    # Singleton instance
    _instance = None
    _initialized = False

    # Config options from file / env
    _config_file = None
    _config_env = None

    # Default config
    default_config = {
        "app_name": "omgui",
        "host": "localhost",
        "port": 8024,
        "session": False,
        "workspace": "DEFAULT",
        "log_level": "INFO",
        "stateless": False,
        # Advanced:
        "base_path": "",
        "redis_url": None,
        "data_dir": "~/.omgui",
        "prompt": True,
        "sample_files": True,
        "_viz_deps": False,
    }

    # Config settings set via omgui.configure() during runtime
    config_runtime = {}

    def __new__(cls, **args):
        """
        Control singleton instance creation.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, defaults: bool = False):
        """
        Initialize the configuration by loading from environment variables,
        configuration file, and setting defaults.
        """
        # Prevent re-initialization of singleton
        if self._initialized:
            return

        # When running config.reset(defaults=True)
        # --> set config to default values only
        if defaults:
            _config = self.default_config

        # Normal initialization
        else:
            _config = (
                self.default_config  # Base: defaults
                | self.config_file()  # 3nd priority: omgui.config.yml
                | self.config_env()  # 2nd priority: environment variables
                | self.config_runtime  # 1st priority: set via omgui.configure()
            )

        # Write to self
        for key, value in _config.items():
            setattr(self, key, value)

        # Create the data directory if it doesn't exist
        if not Path(_config.get("data_dir")).expanduser().exists():
            logger.info(
                "Creating missing omgui data directory at '%s'", _config.get("data_dir")
            )
            Path(_config.get("data_dir")).expanduser().mkdir(
                parents=True, exist_ok=True
            )

    @classmethod
    def re_init(cls, defaults: bool = False):
        """
        Re-initialize the singleton instance.
        This is used after config values are changed
        via omgui.configure() or config.reset().
        """
        instance = cls._instance
        if instance is not None:
            instance._initialized = False
            instance.__init__(defaults=defaults)

    def config_file(self):
        """
        Returns the loaded config file as a dict.
        """
        if self._config_file is None:
            self._config_file = self._load_config_file()
        return self._config_file

    def _load_config_file(self):
        """
        Loads configuration from a YAML file.
        Returns a dict.
        """

        _config_file = {}
        try:
            config_path = Path(os.getcwd()) / "omgui.config.yml"
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as file:
                    _config_file = yaml.safe_load(file)
                    _config_file = _config_file if _config_file else {}

            # Log what's loaded
            _file_vars = list(_config_file.keys())
            logger.info(
                "Loaded config options from file omgui.config.yml: %s",
                ", ".join(_file_vars) if _file_vars else "None",
            )

            return _config_file

        except Exception as err:  # pylint: disable=broad-except
            logger.error("An error occurred while loading the config file: %s", err)
            return {}

    def config_env(self):
        """
        Returns the loaded config env as a dict.
        """
        if self._config_env is None:
            self._config_env = self._load_config_env()
        return self._config_env

    def _load_config_env(self):
        """
        Loads configuration from environment variables.
        Returns a dict.
        """
        _config_env = {}
        for key, val in self.default_config.items():
            env_var = f"OMGUI_{key.upper()}"
            if env_var in os.environ:
                val = os.environ[env_var]
                if isinstance(val, bool):
                    val = val.lower() in ("true", "1", "yes")
                elif isinstance(val, int):
                    val = int(val)
                _config_env[key] = val

        # Log what's loaded
        _env_vars = list(_config_env.keys())
        logger.info(
            "Loaded config options from environment variables: %s",
            ", ".join(_env_vars) if _env_vars else "None",
        )
        return _config_env

    def set(self, key, value):
        """
        Set a configuration value.
        This is used by omgui.config(key=val)
        """

        if key in self.default_config:
            self.config_runtime[key] = value
            logger.info("Config '%s' set to '%s'", key, value)
        else:
            logger.warning("Config key '%s' not recognized.", key)

    def reset(self, defaults: bool = False):
        """
        Resets the configuration to default values.
        """
        self.config_runtime = {}
        self._config_env = None
        self._config_file = None
        self.re_init(defaults)
        if defaults:
            logger.info("Configuration reset to default values")
        else:
            logger.info("Configuration reset")

    def fixed_port(self) -> bool:
        """
        Returns True if a custom port is set,
        in which case we don't want to auto-increment it.
        """
        return (
            "port" in self.config_env()
            or "port" in self.config_file()
            or "port" in self.config_runtime
        )

    def host_url(self) -> str:
        """
        Returns the host URL, e.g. http://localhost:8024
        """
        base_path = self.base_path if self.base_path else ""
        return f"http://{self.host}:{self.port}{base_path}"

    def get_dict(self):
        """
        Returns the current config, mainly for debugging purposes.
        """
        return self.__dict__.copy()

    def report(self):
        """
        Prints an overview of the current configuration.
        """
        _report = []
        _report.append("<h1>Compiled config</h1>")
        for key, val in self.__dict__.items():
            if not key.startswith("_"):
                _report.append(f"<green>{key:12}</green><soft>:</soft> {val}")

        spf("\n".join(_report), pad=2, edge=True)
        _report = []

        _report.append("<h2>Configuration Sources:</h2>\n")

        _report.append("  1. Config runtime")
        for key, val in self.config_runtime.items():
            if not key.startswith("_"):
                _report.append(f"     {key:12}: {val}")
        if len(self.config_runtime.items()) == 0:
            _report.append("     <soft>None</soft>")

        _report.append("\n  2. Config env")
        for key, val in self.config_env().items():
            _report.append(f"     {key:12}: {val}")
        if len(self.config_env().items()) == 0:
            _report.append("     <soft>None</soft>")

        _report.append("\n  3. Config file")
        for key, val in self.config_file().items():
            _report.append(f"     {key:12}: {val}")
        if len(self.config_file().items()) == 0:
            _report.append("     <soft>None</soft>")

        _report.append("\n  4. Default config:")
        for key, val in self.default_config.items():
            _report.append(f"     {key:12}: {val}")

        spf("\n".join(_report), pad_btm=2)
