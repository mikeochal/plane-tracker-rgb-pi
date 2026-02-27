from datetime import datetime
from utilities.temperature import grab_forecast
from utilities.animator import Animator
from setup import colours, fonts, frames
from rgbmatrix import graphics
import time as time_module  # avoid conflict if 'time' is already used
import logging


# Configure logging
#logging.basicConfig(filename='myapp.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Setup
CLOCK_FONT = fonts.large_bold
CLOCK_POSITION = (0, 11)
DAY_COLOUR = colours.LIGHT_ORANGE
NIGHT_COLOUR = colours.LIGHT_BLUE

from config import CLOCK_FORMAT

class ClockScene(object):
    def __init__(self):
        super().__init__()
        self._last_logo_check = 0  # NEW: track when we last showed the logo
        self._last_time = None
        self.today_sunrise = None
        self.today_sunset = None
        self.last_fetch_date = None  # Store the date of the last forecast fetch

    def calculate_sunrise_sunset(self):
        now = datetime.now()
        #print("Checking the sun...")
        
        # Check if it's a new day or if there is no cached data
        if (self.last_fetch_date != now.date()):
            #print("Fetching forecast data...")
            forecast = grab_forecast()
            for day in forecast:
                forecast_date = day['startTime'][:10]
                if forecast_date == now.strftime('%Y-%m-%d'):
                    # Parse UTC sunrise and sunset times
                    utc_sunrise = datetime.strptime(day['values']['sunriseTime'], '%Y-%m-%dT%H:%M:%SZ')
                    utc_sunset = datetime.strptime(day['values']['sunsetTime'], '%Y-%m-%dT%H:%M:%SZ')

                    # Cache the sunrise and sunset times
                    self.today_sunrise = utc_sunrise
                    self.today_sunset = utc_sunset
                    self.last_fetch_date = now.date()  # Update the last fetch date
                    #logging.info(f"Fetched forecast data for {forecast_date}, sunrise: {utc_sunrise}, sunset: {utc_sunset}")
                    #print(f"Fetched forecast data for {forecast_date}, sunrise: {utc_sunrise}, sunset: {utc_sunset}")

        return self.today_sunrise, self.today_sunset

    @Animator.KeyFrame.add(frames.PER_SECOND * 1)
    def draw(self):
    # ── Delta Logo Cycling (NEW) ─────────────────────────────
    # Check if the display wants to show the Delta logo
    # This only triggers every DELTA_LOGO_INTERVAL seconds
    if hasattr(self.display, 'should_show_logo') and self.display.should_show_logo():
        self.display.show_delta_logo()
        # show_delta_logo() blocks for DELTA_LOGO_DURATION seconds,
        # then returns so the clock redraws normally
        return  # Skip this frame's clock draw, it will draw next cycle
    # ─────────────────────────────────────────────────────────

    # ... rest of existing clock drawing code below ...
    def clock(self, count):
        if len(self._data):
            # Ensure redraw when there's new data
            self._last_time = None 
        else:
            # If there's no data to display, then draw a clock
            now = datetime.now()
            if CLOCK_FORMAT == "12hr":
              clock_format = "%l:%M"
            elif CLOCK_FORMAT == "24hr":
              clock_format = "%H:%M"
            current_time = now.strftime(clock_format)

            utc_sunrise, utc_sunset = self.calculate_sunrise_sunset()

            time_until_sunrise = (utc_sunrise - datetime.utcnow()).total_seconds()
            time_until_sunset = (utc_sunset - datetime.utcnow()).total_seconds()
            
            if time_until_sunset <= 0:
                clock_color = NIGHT_COLOUR
            elif time_until_sunrise <= 0:
                clock_color = DAY_COLOUR
            else:
                clock_color = NIGHT_COLOUR

            if self._last_time:
                _ = graphics.DrawText(
                    self.canvas,
                    CLOCK_FONT,
                    CLOCK_POSITION[0],
                    CLOCK_POSITION[1],
                    colours.BLACK,
                    self._last_time,
                )
            self._last_time = current_time

            _ = graphics.DrawText(
                self.canvas,
                CLOCK_FONT,
                CLOCK_POSITION[0],
                CLOCK_POSITION[1],
                clock_color,
                current_time,
            )
