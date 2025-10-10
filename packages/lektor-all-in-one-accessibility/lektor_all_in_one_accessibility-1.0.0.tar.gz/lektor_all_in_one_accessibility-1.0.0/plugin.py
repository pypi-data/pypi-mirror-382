import os
import requests
from lektor.pluginsystem import Plugin
import configparser
from pathlib import Path
import logging

class AccessibilityPlugin(Plugin):
    """
    Lektor Plugin: Accessibility Widget
    Injects a third-party accessibility widget into your static site.
    Loads configuration from `configs/accessibility.ini` and optionally pushes config to an API.
    """
    name = "all-in-one-accessibility"
    description = "Website accessibility widget for improving WCAG 2.0, 2.1, 2.2 and ADA compliance!"

    WIDGET_JS_URL = "https://www.skynettechnologies.com/accessibility/js/all-in-one-accessibility-js-widget-minify.js?"
    API_SAVE_URL ="https://ada.skynettechnologies.us/api/widget-setting-update-platform"

    def __init__(self, *args, **kwargs):
        # Standard plugin init
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.accessibility_cfg = {}  # Cached configuration dictionary

    # ===============================
    # CONFIG VALIDATION
    # ===============================
    def validate_required_fields(self, cfg):
        """
        Validates that required fields exist if plugin is enabled.
        """
        required_keys = [
            "widget_color_code",
            "widget_icon_size",
            "widget_position",
            "widget_icon_type",
        ]

        missing_keys = [key for key in required_keys if not cfg.get(key)]
        
        if missing_keys:
            error_msg = f"Missing required config fields when enable=true: {', '.join(missing_keys)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    # ===============================
    # SETUP HOOK
    # ===============================
    def on_setup_env(self, **extra):
        """
        Called during Lektor environment setup.
        Loads and validates the config, injects the widget script, and pushes config to API.
        """
        env = self.env
        if not env:
            raise RuntimeError("No Lektor environment found in on_setup_env.")
        
        self.accessibility_cfg = self.load_accessibility_config(env)

        # Validate config only if plugin is enabled
        if self.accessibility_cfg.get('enable', 'false').lower() in ['true', '1', 'yes']:
            self.validate_required_fields(self.accessibility_cfg)

        # Inject widget script into Jinja environment
        env.jinja_env.globals['accessibility_widget_script'] = self.render_widget_script()

        # Push config to API (optional)
        self.push_config_to_api()

    # ===============================
    # CONFIG LOADING
    # ===============================
    def load_accessibility_config(self, env):
        """
        Loads configuration from configs/accessibility.ini file.
        """
        config_path = Path(env.root_path) / "configs" / "accessibility.ini"
        parser = configparser.ConfigParser()

        if not config_path.exists():
            raise RuntimeError(f"No config found at {config_path}")

        parser.read(config_path)

        if not parser.has_section("settings"):
            raise RuntimeError("[settings] section missing in accessibility.ini")
        
        return parser["settings"]

    # ===============================
    # RENDER <script> TAG
    # ===============================
    def render_widget_script(self):
        """
        Renders the <script> tag that loads the widget JS.
        Injected into base template via Jinja global.
        """
        cfg = self.accessibility_cfg
        if not cfg or cfg.get('enable', 'false').lower() not in ['true', '1', 'yes']:
            return ""

        return f'<script id="aioa-adawidget" src="{self.WIDGET_JS_URL}"></script>'

    # ===============================
    # BUILD PAYLOAD FROM CONFIG
    # ===============================
    def build_data_from_config(self):
        """
        Transforms the config settings into the payload format required by the API.
        """
        cfg = self.accessibility_cfg
        if not cfg:
            return {}

        # Domain priority: Environment variable overrides config
        domain = os.environ.get('LEKTOR_DOMAIN', '').strip()
        if not domain:
            raise ValueError(
                "LEKTOR_DOMAIN environment variable is not set or empty. "
                "Please set it before running Lektor."
            )

        # Flags for optional behavior
        enable_widget_custom_position = cfg.getboolean('enable_widget_custom_position', fallback=False)
        enable_widget_custom_size = cfg.getboolean('enable_widget_custom_size', fallback=False)

        data = {
            "u": domain,
            "widget_color_code": cfg.get('widget_color_code', '#420083'),
            "is_widget_custom_position": int(enable_widget_custom_position),
            "is_widget_custom_size": int(enable_widget_custom_size),
        }

        # Icon positioning (static vs. custom)
        if not enable_widget_custom_position:
            data.update({
                "widget_position_top": 0,
                "widget_position_right": 0,
                "widget_position_bottom": 0,
                "widget_position_left": 0,
                "widget_position": cfg.get('widget_position', 'bottom_right'),
            })
        else:
            # Custom positioning logic
            widget_position = {
                "widget_position_top": 0,
                "widget_position_right": 0,
                "widget_position_bottom": 0,
                "widget_position_left": 0,
            }

            # Horizontal alignment
            widget_position_right = cfg.get('widget_position_right', '')
            widget_position_right_px = int(cfg.get('widget_position_right_px', '0'))

            if widget_position_right == "to_the_left":
                widget_position["widget_position_left"] = widget_position_right_px
            elif widget_position_right == "to_the_right":
                widget_position["widget_position_right"] = widget_position_right_px

            # Vertical alignment
            widget_position_bottom = cfg.get('widget_position_bottom', '')
            widget_position_bottom_px = int(cfg.get('widget_position_bottom_px', '0'))

            if widget_position_bottom == "to_the_bottom":
                widget_position["widget_position_bottom"] = widget_position_bottom_px
            elif widget_position_bottom == "to_the_top":
                widget_position["widget_position_top"] = widget_position_bottom_px

            data.update(widget_position)
            data["widget_position"] = ""  # Overwrite static position

        # Icon size (default class or custom px)
        if not enable_widget_custom_size:
            data.update({
                "widget_icon_size": cfg.get('widget_icon_size', ''),
                "widget_icon_size_custom": 0,
            })
        else:
            data.update({
                "widget_icon_size": "",
                "widget_icon_size_custom": int(cfg.get('widget_icon_size_custom', '0')),
            })

        # Widget size toggle (oversize = 1)
        widget_size_value = 1 if cfg.get('widget_size', '') == 'oversize' else 0

        data.update({
            "widget_size": widget_size_value,
            "widget_icon_type": cfg.get('widget_icon_type', ''),
        })

        return data

    # ===============================
    # PUSH CONFIG TO EXTERNAL API
    # ===============================
    def push_config_to_api(self):
        """
        Pushes the final config payload to an external API for syncing.
        Only runs if plugin is enabled.
        """
        cfg = self.accessibility_cfg

        if not cfg:
            raise ValueError("Accessibility config not loaded.")

        if cfg.get('enable', 'false').lower() not in ['true', '1', 'yes']:
            raise ValueError("Accessibility plugin is disabled in your config file.")

        data = self.build_data_from_config()
        files=[
        
        ]
        headers = {}
        
        try:
            response = requests.post(self.API_SAVE_URL, headers=headers,data=data,files=files)
            response.raise_for_status()
            self.logger.info(f"Accessibility config pushed successfully: {response.text}")
        except requests.RequestException as e:
            self.logger.error(f"Failed to push accessibility config: {e}")
        