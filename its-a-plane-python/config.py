# =============================================================================
# config.py — Plane Tracker RGB Pi Configuration
# Revised for: 128x64 P2 panel, Pi 4B, Adafruit Bonnet
# =============================================================================

# ─── Location Settings ───────────────────────────────────────────────────────
ZONE_HOME = {
    "tl_y": 56.06403,       # Top-Left Latitude (deg)
    "tl_x": -4.51589,       # Top-Left Longitude (deg)
    "br_y": 55.89088,       # Bottom-Right Latitude (deg)
    "br_x": -4.19694        # Bottom-Right Longitude (deg)
}

LOCATION_HOME = [
    55.9074356,              # Latitude (deg)
    -4.3331678,              # Longitude (deg)
    0.01781                  # Altitude (km)
]

WEATHER_LOCATION = "Glasgow"

# ─── API Keys ────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY = ""     # Get from https://openweathermap.org/price

# ─── Display Settings ────────────────────────────────────────────────────────
TEMPERATURE_UNITS = "imperial"   # "metric" or "imperial"
TIME_FORMAT = 12                 # 12 or 24
MIN_ALTITUDE = 100               # Filter planes below this altitude (feet)
BRIGHTNESS = 50                  # 0-100
GPIO_SLOWDOWN = 4                # *** CHANGED: Pi 4 needs 4 (Pi 3 uses 2) ***
JOURNEY_CODE_SELECTED = "GLA"    # Local airport code (bold on display)
JOURNEY_BLANK_FILLER = " ? "     # Unknown airport placeholder
HAT_PWM_ENABLED = False          # Set True if PWM bridge is soldered

# ─── Panel Configuration (NEW) ───────────────────────────────────────────────
# For PH2-128x64-32S panel:
LED_ROWS = 64                    # *** NEW: Panel rows (was 32) ***
LED_COLS = 128                   # *** NEW: Panel columns (was 64) ***
LED_CHAIN = 1                    # Number of daisy-chained panels
LED_PARALLEL = 1                 # Parallel chains
LED_ROW_ADDR_TYPE = 0            # Address type (try 3 or 5 if display is garbled)
LED_MULTIPLEXING = 0             # Multiplexing type (0 for most panels)
LED_RGB_SEQUENCE = "RGB"         # Change to "RBG" if colors are swapped

# ─── Dimming Schedule ────────────────────────────────────────────────────────
# Display dims at these hours (24hr format)
DIM_BRIGHTNESS = 15              # Brightness during dim hours
DIM_START = 22                   # 10 PM
DIM_END = 7                      # 7 AM

# ─── Delta Logo Settings (NEW) ───────────────────────────────────────────────
DELTA_LOGO_ENABLED = True        # *** NEW: Enable Delta logo cycling ***
DELTA_LOGO_PATH = "images/delta_logo.ppm"  # *** NEW: Path to logo image ***
DELTA_LOGO_INTERVAL = 30         # *** NEW: Seconds between logo displays ***
DELTA_LOGO_DURATION = 5          # *** NEW: Seconds to show the logo ***

# ─── Auto-Shutdown Settings (NEW) ────────────────────────────────────────────
AUTO_SHUTDOWN_ENABLED = False    # *** NEW: Enable scheduled shutdown ***
AUTO_SHUTDOWN_TIME = "23:30"     # *** NEW: Time to shutdown (24hr, HH:MM) ***

# ─── Email / Logging Settings ────────────────────────────────────────────────
# (Keep your existing email settings here if using the c0wsaysmoo fork)
# EMAIL_ENABLED = False
# MAX_CLOSEST = 3
# MAX_FARTHEST = 3

