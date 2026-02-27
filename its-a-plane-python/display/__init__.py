#!/usr/bin/env python3
# =============================================================================
# display/__init__.py — RGB Matrix Display Driver
# Revised for: 128x64 panel support, Delta logo cycling, auto-shutdown
# =============================================================================

import sys
import os
import time
import threading
from datetime import datetime

# Add the parent directory to the path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

try:
    from config import (
        BRIGHTNESS, GPIO_SLOWDOWN, HAT_PWM_ENABLED,
        LED_ROWS, LED_COLS, LED_CHAIN, LED_PARALLEL,
        LED_ROW_ADDR_TYPE, LED_MULTIPLEXING, LED_RGB_SEQUENCE,
        DIM_BRIGHTNESS, DIM_START, DIM_END,
        DELTA_LOGO_ENABLED, DELTA_LOGO_PATH,
        DELTA_LOGO_INTERVAL, DELTA_LOGO_DURATION,
        AUTO_SHUTDOWN_ENABLED, AUTO_SHUTDOWN_TIME,
    )
except ImportError:
    # Defaults if config values are missing
    BRIGHTNESS = 50
    GPIO_SLOWDOWN = 4
    HAT_PWM_ENABLED = False
    LED_ROWS = 64
    LED_COLS = 128
    LED_CHAIN = 1
    LED_PARALLEL = 1
    LED_ROW_ADDR_TYPE = 0
    LED_MULTIPLEXING = 0
    LED_RGB_SEQUENCE = "RGB"
    DIM_BRIGHTNESS = 15
    DIM_START = 22
    DIM_END = 7
    DELTA_LOGO_ENABLED = False
    DELTA_LOGO_PATH = "images/delta_logo.ppm"
    DELTA_LOGO_INTERVAL = 30
    DELTA_LOGO_DURATION = 5
    AUTO_SHUTDOWN_ENABLED = False
    AUTO_SHUTDOWN_TIME = "23:30"


class Display:
    """
    Manages the RGB LED matrix hardware.
    Handles initialization, brightness dimming, Delta logo cycling,
    and auto-shutdown scheduling.
    """

    def __init__(self):
        # ── Matrix Hardware Options ──────────────────────────────────────
        options = RGBMatrixOptions()
        options.rows = LED_ROWS
        options.cols = LED_COLS
        options.chain_length = LED_CHAIN
        options.parallel = LED_PARALLEL
        options.row_address_type = LED_ROW_ADDR_TYPE
        options.multiplexing = LED_MULTIPLEXING
        options.brightness = BRIGHTNESS
        options.gpio_slowdown = GPIO_SLOWDOWN
        options.led_rgb_sequence = LED_RGB_SEQUENCE
        options.drop_privileges = False
        options.limit_refresh_rate_hz = 120

        if HAT_PWM_ENABLED:
            options.hardware_mapping = 'adafruit-hat-pwm'
        else:
            options.hardware_mapping = 'adafruit-hat'

        self.matrix = RGBMatrix(options=options)
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()

        # ── Display Properties ───────────────────────────────────────────
        self.width = LED_COLS * LED_CHAIN
        self.height = LED_ROWS
        self.brightness = BRIGHTNESS

        # ── Delta Logo State ─────────────────────────────────────────────
        self.delta_logo_image = None
        self.showing_logo = False
        self._last_logo_time = 0
        self._logo_thread = None

        if DELTA_LOGO_ENABLED:
            self._load_delta_logo()

        # ── Auto-Shutdown Thread ─────────────────────────────────────────
        if AUTO_SHUTDOWN_ENABLED:
            self._start_shutdown_scheduler()

    # ── Matrix Access ────────────────────────────────────────────────────
    def swap_frame(self):
        """Swap the offscreen canvas to the display."""
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def clear(self):
        """Clear the offscreen canvas."""
        self.offscreen_canvas.Clear()

    def set_pixel(self, x, y, r, g, b):
        """Set a single pixel on the offscreen canvas."""
        self.offscreen_canvas.SetPixel(x, y, r, g, b)

    def set_image(self, image, x_offset=0, y_offset=0, unsafe=False):
        """
        Set an image on the offscreen canvas.
        Image should be a PIL Image object.
        """
        if unsafe:
            self.offscreen_canvas.SetImage(image, x_offset, y_offset, unsafe)
        else:
            self.offscreen_canvas.SetImage(image, x_offset, y_offset)

    def draw_text(self, font, x, y, color, text):
        """Draw text on the offscreen canvas."""
        return graphics.DrawText(self.offscreen_canvas, font, x, y, color, text)

    def draw_line(self, x0, y0, x1, y1, color):
        """Draw a line on the offscreen canvas."""
        graphics.DrawLine(self.offscreen_canvas, x0, y0, x1, y1, color)

    # ── Brightness & Dimming ─────────────────────────────────────────────
    def update_brightness(self):
        """Adjust brightness based on time of day (dim schedule)."""
        hour = datetime.now().hour
        if DIM_START > DIM_END:
            # Overnight dimming (e.g., 22:00 to 07:00)
            is_dim = hour >= DIM_START or hour < DIM_END
        else:
            is_dim = DIM_START <= hour < DIM_END

        target = DIM_BRIGHTNESS if is_dim else BRIGHTNESS
        if self.matrix.brightness != target:
            self.matrix.brightness = target

    # ── Delta Logo ───────────────────────────────────────────────────────
    def _load_delta_logo(self):
        """Load the Delta logo image, scaling it to fit the panel."""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(script_dir, DELTA_LOGO_PATH)

        if not os.path.exists(logo_path):
            print(f"[WARNING] Delta logo not found at {logo_path}")
            print("          Delta logo cycling is disabled.")
            return

        try:
            img = Image.open(logo_path).convert("RGB")
            # Scale to fit the panel while maintaining aspect ratio
            img_ratio = img.width / img.height
            panel_ratio = self.width / self.height

            if img_ratio > panel_ratio:
                # Image is wider — fit to width
                new_width = self.width
                new_height = int(self.width / img_ratio)
            else:
                # Image is taller — fit to height
                new_height = self.height
                new_width = int(self.height * img_ratio)

            img = img.resize((new_width, new_height), Image.LANCZOS)

            # Center on a black background
            background = Image.new("RGB", (self.width, self.height), (0, 0, 0))
            x_off = (self.width - new_width) // 2
            y_off = (self.height - new_height) // 2
            background.paste(img, (x_off, y_off))

            self.delta_logo_image = background
            print(f"[INFO] Delta logo loaded: {new_width}x{new_height}, "
                  f"centered on {self.width}x{self.height} canvas")
        except Exception as e:
            print(f"[ERROR] Failed to load Delta logo: {e}")
            self.delta_logo_image = None

    def should_show_logo(self):
        """
        Check if it's time to show the Delta logo.
        Returns True if DELTA_LOGO_INTERVAL seconds have passed since last show.
        Only triggers during weather/clock display (not during flight tracking).
        """
        if not DELTA_LOGO_ENABLED or self.delta_logo_image is None:
            return False

        now = time.time()
        if now - self._last_logo_time >= DELTA_LOGO_INTERVAL:
            return True
        return False

    def show_delta_logo(self):
        """
        Display the Delta logo for DELTA_LOGO_DURATION seconds.
        Call this from the main loop when should_show_logo() returns True.
        """
        if self.delta_logo_image is None:
            return

        self.showing_logo = True
        self._last_logo_time = time.time()

        # Display the logo
        self.clear()
        self.set_image(self.delta_logo_image)
        self.swap_frame()

        # Hold for the configured duration
        time.sleep(DELTA_LOGO_DURATION)
        self.showing_logo = False

    # ── Auto-Shutdown ────────────────────────────────────────────────────
    def _start_shutdown_scheduler(self):
        """Start a background thread that checks for the shutdown time."""
        self._shutdown_thread = threading.Thread(
            target=self._shutdown_loop,
            daemon=True
        )
        self._shutdown_thread.start()
        print(f"[INFO] Auto-shutdown scheduled for {AUTO_SHUTDOWN_TIME}")

    def _shutdown_loop(self):
        """Background loop that initiates shutdown at the configured time."""
        try:
            shutdown_hour, shutdown_minute = map(int, AUTO_SHUTDOWN_TIME.split(":"))
        except ValueError:
            print(f"[ERROR] Invalid AUTO_SHUTDOWN_TIME: {AUTO_SHUTDOWN_TIME}")
            return

        shutdown_triggered = False

        while True:
            now = datetime.now()
            if (now.hour == shutdown_hour and
                now.minute == shutdown_minute and
                not shutdown_triggered):

                print(f"[INFO] Auto-shutdown triggered at {now.strftime('%H:%M')}")
                # Clear the display before shutdown
                self.clear()
                self.swap_frame()
                time.sleep(2)

                # Initiate system shutdown
                os.system("sudo shutdown -h now")
                shutdown_triggered = True

            # Reset the trigger flag after the minute passes
            if now.minute != shutdown_minute:
                shutdown_triggered = False

            time.sleep(30)  # Check every 30 seconds
            self.play()

        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

