"""pisonoslcd.py - Functions to implement 2x16 LCD display."""

# This module is primarily designed to work with the Adafruit 2x16 LCD dislay,
# setting raw_gpio to true allows an alternative configuration using raw GPIO and CharLCD
raw_gpio = False
lcd = None


def init():
    """Initialise the LCD display."""

    global raw_gpio
    global lcd
    import configparser

    config = configparser.ConfigParser()
    config.read("pisonos.cfg")
    if "LCD" in config:
        raw_gpio = config.getboolean("LCD", "rawgpio", fallback=False)
    if raw_gpio:
        print("Using raw GPIO LCD output")
        import os
        import time
        import RPi.GPIO as GPIO  # type: ignore
        from RPLCD import CharLCD, cleared, cursor  # type: ignore

        # Wait for GPIO to become available
        print("Waiting for GPIO access...")
        while not os.access("/dev/gpiomem", os.R_OK):
            print("Waiting for GPIO access")
            time.sleep(1)
        GPIO.setmode(GPIO.BCM)
        backlight = 4
        GPIO.setup(backlight, GPIO.OUT)
        lcd = CharLCD(
            pin_rs=25,
            pin_rw=None,
            pin_e=24,
            pins_data=[23, 17, 21, 22],
            numbering_mode=GPIO.BCM,
            cols=16,
            rows=2,
            dotsize=8,
            compat_mode=True,
        )
        GPIO.output(backlight, True)
    else:
        print("Using Adafruit LCD")
        import Adafruit_CharLCD as LCD  # type: ignore

        lcd = LCD.Adafruit_CharLCDPlate()
        set_color(1.0, 1.0, 1.0)  # White
    clear()


def cleanup():
    """Close and clean up the LCD display."""

    clear()
    global raw_gpio
    if raw_gpio:
        lcd.display_enabled = False
        lcd.close()
        import RPi.GPIO as GPIO  # type: ignore

        backlight = 4
        GPIO.output(backlight, False)
        GPIO.cleanup()
    else:
        set_color(0.0, 0.0, 0.0)


def clear():
    """Remove all content from the LCD display."""

    home()
    lcd.clear()


def home():
    """Set cursor to top left."""

    lcd.home()


def message(message_string):
    """Show a string on the display."""

    global raw_gpio
    if raw_gpio:
        gpio_message_string = message_string.replace("\n", "\r\n")
        lcd.write_string(gpio_message_string)
    else:
        lcd.message(message_string)


def write_string(message_string):
    """Show a string on the display."""

    message(message_string)


def create_char(charnumber, chardata):
    """Create a custom character."""

    lcd.create_char(charnumber, chardata)


def set_color(red, green, blue):
    """Set the display colour if supported."""

    global raw_gpio
    if not raw_gpio:
        lcd.set_color(red, green, blue)


def show_cursor(visible):
    """Show or hide the cursor."""

    global raw_gpio
    if raw_gpio:
        lcd.cursor_mode = "blink" if visible else "hide"
    else:
        lcd.show_cursor(visible)


def enable_display(enabled):
    """Enable or disable the display."""

    global raw_gpio
    if raw_gpio:
        lcd.display_enabled = enabled
