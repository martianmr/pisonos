# coding: UTF-8
"""pisonos.py - core module for Rasberry Pi Sonos Controller."""

from _version import __version__
print ("pisonos " + __version__)

import pisonoslcd as lcd

############################
# SETUP FUNCTIONS
############################

def init_lcd():
    """Setup the LCD display for use."""

    # Initialize the LCD
    lcd.init()

    # Create a raspberry custom character and output a message on the LCD display
    raspi = (
        0b00000,
        0b01010,
        0b00100,
        0b01010,
        0b10101,
        0b01010,
        0b00100,
        0b00000,
    )
    lcd.create_char(0, raspi)
    lcd.message('Raspberry Pi ' + chr(0) + '\nSonos Remote')

def setup_clock_font():
    """Create custom characters to display large numbers on the 2x16 LCD display."""

    # Data for large numeric display custom characters used for clock
    bigfont = (
        (
            0b00111,
            0b01111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
        ),
        (
            0b11111,
            0b11111,
            0b11111,
            0b00000,
            0b00000,
            0b00000,
            0b11111,
            0b11111,
        ),
        (
            0b11100,
            0b11110,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
        ),
        (
            0b11111,
            0b11111,
            0b11111,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
        ),
        (
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b01111,
            0b00111,
        ),
        (
            0b11111,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b11111,
            0b11111,
            0b11111,
        ),
        (
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11110,
            0b11100,
        ),
        (
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b11111,
            0b11111,
            0b11111,
        ),
    )

    # Clear the display
    lcd.clear()

    # Create the custom graphics for big numbers
    i = 0
    while i < len(bigfont):
        lcd.create_char(i, bigfont[i])
        i += 1

def connect_to_sonos():
    """Get the player name from config and attempt to connect to it."""

    # Read the config file to get the player name
    import configparser
    config = configparser.ConfigParser()
    config.read('pisonos.cfg')
    if 'pisonos' in config:
        player = config['pisonos']['player']

    # Output a message with connection information from config
    lcd.clear()
    lcd.message('Pisonos ' + __version__ + '\n' + player)
    print('Attempting connection to ' + player)

    # Attempt to connect to Sonos system
    count=0
    disc = soco.discover()
    while not disc:
       print('Waiting for connection')
       time.sleep(5)
       count = count + 1
       disc = soco.discover()
       if count > 10:
           print('Unable to connect to Sonos network')
           lcd.cleanup()
           sys.exit(1)

    # Find the correct sonos based on player name from config
    sonos = None
    for zone in disc:
        try:
            if zone.player_name == player:
                sonos = zone
                print(zone)
        except OSError as e:
            # If a device is offline but still registered with our Sonos system we will get this error
            # If the offline device is the device we want we wil pick up this and exit after the loop
            msg = 'WARNING: OSError received from device connect: {}'.format(str(e))
            print(msg)
        except Exception as e:
            # Any other exception at this stage and we break out and cleanup
            sonos = None
            msg = 'Exception on connect: {}'.format(type(e).__name__)
            print(msg)
            print(e)
            break
    
    # Check if we found the right device or exit
    if sonos == None:
        print('Could not find Sonos device ' + player)
        lcd.cleanup()
        sys.exit(1)

    # Return the device
    return sonos

############################
# UTILITY FUNCTIONS
############################

def draw_big_number(num, pos):
    """Update the display buffer to draw a single large number (num) at position (pos) on the LCD display."""

    global NewLine1, NewLine2
    # Data for arrangment of custom characters into large numbers used for clock
    bignumber = (
        ((0,3,2),(4,7,6)), #0
        ((32,3,255),(32,32,255)), #1
        ((1,1,2),(255,5,5)), #2
        ((3,1,2),(7,5,6)), #3
        ((255,32,7),(3,3,255)), #4
        ((255,1,1),(5,5,6)), #5
        ((0,1,1),(4,5,6)), #6
        ((3,3,255),(32,0,32)), #7
        ((0,1,2),(4,5,6)), #8
        ((0,1,2),(5,5,6)), #9
    )
    i = 0
    temp1 = NewLine1.ljust(16)
    temp2 = NewLine2.ljust(16)
    NewLine1 = ''
    NewLine2 = ''
    if pos > 0:
       NewLine1 = temp1[:pos]
       NewLine2 = temp2[:pos]
    while i < 3:
        NewLine1 += chr(bignumber[num][0][i])
        NewLine2 += chr(bignumber[num][1][i])
        i += 1
    if pos < 13:
        NewLine1 += temp1[pos+3:]
        NewLine2 += temp2[pos+3:]

def isradio():
    """Determine if we are playing radio by checking the track duration, if duration is 0 we return true otherwise false."""

    retval = sonos.get_current_track_info()['duration'] == '0:00:00'
    return retval

def get_track_info():
    """Get information on title, track and artist and display.
    
    If this is radio we display title+artist on the first line and the channel on the second line.
    Otherwise display title on the first line and artist on the second.
    """

    from unidecode import unidecode
    if (isradio()):
        title = sonos.get_current_track_info()['title']
        artist = sonos.get_current_track_info()['artist']
        divider = "" if (title == "" or artist == "") else " - "
        line1 = title + divider + artist
        line2 = sonos.get_current_media_info()['channel']
    else:
        line1 = sonos.get_current_track_info()['title']
        line2 = sonos.get_current_track_info()['artist']

    return unidecode(line1), unidecode(line2)    

def display_message(text):
    """Display some text on the second LCD line, usually used to indicate state changes."""

    global Time, NewLine2, NewLine1
    Time = time.time()
    NewLine1 = ''
    NewLine2 = text
    ClockCount = 0

def display_track_info(state):
    """Determines what we want to display to LCD based on current state and updates the buffers accordingly."""

    global NewLine1, NewLine2, Time, StoppedTime, Enabled
    NewTime = time.time()
    if NewTime - Time < 1:
        return
    global PowerTime, ClockCount
    if NewTime - PowerTime < 2:
        return
    PowerTime = 0
    Time = NewTime
    global AlwaysShowTime
    strtime = time.strftime('%X')
    if state != 'PLAYING' or AlwaysShowTime:
        # No information to show or we want to see the time, show a large font clock
        if AlwaysShowTime or (StoppedTime != 0 and NewTime - StoppedTime > 20):
            Enabled = False
            NewLine1 = "        " + chr(161)
            NewLine2 = "        " + chr(223)
            firstpos = 1 if strtime[1] == '1' else 0 
            draw_big_number(int(strtime[0]), firstpos)
            draw_big_number(int(strtime[1]), 4)
            draw_big_number(int(strtime[3]), 9)
            lastpos = 12 if strtime[4] == '1' else 13 
            draw_big_number(int(strtime[4]), lastpos)
            return
        if StoppedTime == 0:
            StoppedTime = NewTime
        NewLine1 = ''
        NewLine2 = state
    else:
        # Get information on the current track and display it
        if StoppedTime != 0:
            StoppedTime = 0
            Enabled = True
        ClockCount += 1
        if ClockCount > 3:
            try:
               NewLine1, NewLine2 = get_track_info()
            except:
               NewLine1 = ''
               NewLine2 = 'Connection Error'
            ClockCount = 0

def play_radio(index, canwrap = False):
    """Attempt to play a radio station saved as index number in the Sonos favourites."""

    stations = sonos.music_library.get_sonos_favorites()

    LastStation = stations.number_returned-1
    if LastStation < 0:
        return False
    if index > LastStation and not canwrap:
        return False
    if index < 0:
        index = LastStation
    if index > LastStation:
        index = 0

    uri = stations[index].resources[0].uri
    uri = uri.replace('&', '&amp;')
 
    # XML for Tune In service - completely arbitrary (as far as I know) which service we use but we need to specify one when starting saved content
    meta_template = '<DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:r="urn:schemas-rinconnetworks-com:metadata-1-0/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><item id="R:0/0/0" parentID="R:0/0" restricted="true"><dc:title>{title}</dc:title><upnp:class>object.item.audioItem.audioBroadcast</upnp:class><desc id="cdudn" nameSpace="urn:schemas-rinconnetworks-com:metadata-1-0/">{service}</desc></item></DIDL-Lite>'
    tunein_service = 'SA_RINCON65031_'
    metadata = meta_template.format(title=stations[index].title, service=tunein_service)
    sonos.play_uri(uri, metadata)
    global CurrentStation    
    CurrentStation = index   
    return True

############################
# COMMAND FUNCTIONS
############################

def power(param):
    """Handle the power button, will play/pause or shutdown the Rasberry Pi if repeated."""

    global PowerTime, NewLine1, NewLine2
    state = sonos.get_current_transport_info()['current_transport_state']
    if state != 'PLAYING' and PowerTime == 0:
        sonos.play()
        ClockCount = 0
        return
    NewTime = time.time()
    if NewTime - PowerTime > 2:
        sonos.stop()
        global Time, Title
        PowerTime = NewTime
        Time = NewTime
        NewLine1 = 'Press again to'
        NewLine2 = 'Shut Down Pi'
    else:
        NewLine1 = 'Pi is Shutting'
        NewLine2 = 'Down'
        import os
        time.sleep(2)
        os.system("sudo shutdown now")

def mode(param):
    """Switch between radio and music queue."""

    if isradio():
        try:
            sonos.play_from_queue(0)
        except:
            play_radio(CurrentStation)
    else:
        try:
            play_radio(CurrentStation)
        except:
            sonos.play_from_queue(0)
    ClockCount = 0

def mute(param):
    """Mute the Sonos device."""

    sonos.mute = not sonos.mute
    if sonos.mute:
        display_message("Mute On")
    else:
        display_message("Mute Off")

def playpause(param):
    """Play or pause depending on current state."""

    state = sonos.get_current_transport_info()['current_transport_state']
    if state == 'PLAYING':
        sonos.pause()
    else:
        sonos.play()
    state = sonos.get_current_transport_info()['current_transport_state']
    display_message(state)

def previous(param):
    """Play the previous track or station."""

    if isradio():
        global CurrentStation
        CurrentStation -= 1
        play_radio(CurrentStation, True)
        return
    try:
        sonos.previous()
    except:
        sonos.stop()
    ClockCount = 0

def next(param):
    """Play the next track or station."""

    if isradio():
        global CurrentStation
        CurrentStation += 1
        play_radio(CurrentStation, True)
        return
    try:
        sonos.next()
    except:
        pass
    ClockCount = 0

def bassboost(param):
    """Enable/disable bass boost."""

    sonos.loudness = not sonos.loudness
    if sonos.loudness:
        display_message("Loudness On")
    else:
        display_message("Loudness Off")

def volumeup(param):
    """Turn volume up."""

    sonos.mute = False
    sonos.volume += 2
    display_message(str(sonos.volume))

def volumedown(param):
    """Turn volume down."""

    sonos.mute = False
    sonos.volume -= 2
    display_message(str(sonos.volume))

def shuffle(param):
    """Enable/disable track shuffle."""

    if sonos.play_mode == 'SHUFFLE':
        sonos.play_mode = 'NORMAL'
    else:
        sonos.play_mode = 'SHUFFLE'
    display_message(sonos.play_mode)

def usd(param):
    """Override current display and show the time."""

    global AlwaysShowTime
    AlwaysShowTime = not AlwaysShowTime

def number(num):
    """Pick a radio station from favorites or an item from the current queue."""

    display_message(str(num))
    if isradio():
        play_radio(int(num)-1, False)
        return
    try:
        sonos.play_from_queue(int(num)-1)
    except:
        pass
    ClockCount = 0

############################
# HANDLERS
############################

def cleanup():
    """Attempt to clean up when we know we are shutting down the service."""

    global sub, Shutdown
    sub.unsubscribe()
    Shutdown = True
    time.sleep(0.5)
    lcd.cleanup()

def errback(exception):
    """Handle connection errors from Sonos and terminate the service, service can be automatically restarted to retry connection."""

    global Shutdown
    msg = 'Error received on autorenew: {}'.format(str(exception))
    print(msg)
    Shutdown = True

############################
# THREADS
############################

def get_ir_input():
    """Thread to read the IR device."""

    import lirc # type: ignore
    
    # map functions
    functions = {
        'power' : power,
        'mode' : mode,
        'mute' : mute,
        'playpause' : playpause,
        'previous' : previous,
        'next' : next,
        'bassboost' : bassboost,
        'volumeup' : volumeup,
        'volumedown' : volumedown,
        'shuffle' : shuffle,
        'u' : usd,
        '0' : number,
        '1' : number,
        '2' : number,
        '3' : number,
        '4' : number,
        '5' : number,
        '6' : number,
        '7' : number,
        '8' : number,
        '9' : number,
    }

    # Loop to read input from IR and perform matching functions
    global Enabled
    while (not Shutdown):
        # get code from remote
        codeIR = ""
        try:
            # Connect to lirc prog as defined in lircrc
            with lirc.LircdConnection('sonosmonitor') as conn:
                codeIR = conn.readline()
        except TimeoutError:
            print ("\nTimeout")
        if codeIR:
            func = functions[codeIR]
            try:
                func(codeIR)
            except:
                pass
            Enabled = True

def display_scrolling():
    """Thread to continuously display the contents of the line buffers on the 2x16 LCD display.
    
    Content is scrolled if it will not fit on the line. Thread will exit if the service is shutting
    down to prevent display corruption in a raw GPIO configuration due to data being partially written
    to the LCD device.  
    """

    start = -8
    Line1 = ''
    Line2 = ''
    Scroll1 = start
    Scroll2 = start
    Length1 = 0
    Length2 = 0
    line1 = ''
    line2 = ''
    Clear = False
    enabled = True

    lcd.set_color(1.0, 1.0, 0.0) # Yellow

    # Loop to update display until shutdown
    while (not Shutdown):
        try:
            time.sleep(0.2)
        except KeyboardInterrupt:
            break
        if enabled != Enabled:
            enabled = Enabled
            if enabled:
                lcd.set_color(1.0, 1.0, 0.0) # Yellow
            else:
                if AlwaysShowTime:
                    lcd.set_color(1.0, 0.0, 1.0) # Magenta
                else:
                    lcd.set_color(1.0, 0.0, 0.0) # Red
                
        # new information - reset everything
        if NewLine1 != Line1 or NewLine2 != Line2:
            Scroll1 = start
            Scroll2 = start
            Length1 = len(NewLine1)
            Length2 = len(NewLine2)
            Line1 = NewLine1
            Line2 = NewLine2
            Clear = True
        else:
            Clear = False

        # Temporary buffers for scrolling
        line1 = Line1
        line2 = Line2

        # If line1 is longer than 16 characters implement scrolling
        if Length1 > 16:
            pos1 = min(max(0, Scroll1), Length1 - 16)
            line1 = line1[pos1:]
            if pos1 == 0:
                line1 = (line1[:15] + chr(126))
            Scroll1 += 1
            if Scroll1 > Length1-10:
                Scroll1 = start
        line1 = line1.ljust(16)[:16]

        # If line2 is longer than 16 characters implement scrolling
        if Length2 > 16:
            pos2 = min(max(0, Scroll2), Length2 - 16)
            line2 = line2[pos2:]
            if pos2 == 0:
                line2 = (line2[:15] + chr(126))
            Scroll2 += 1
            if Scroll2 > Length2-10:
                Scroll2 = start    
        line2 = line2.ljust(16)[:16]

        # Output the current buffer state to LCD
        if Clear:
            lcd.show_cursor(False)
            lcd.clear()
        lcd.home()
        lcd.message(line1 + '\n' + line2)

    print("Display shutdown")
 
############################
# MAIN THREAD
############################

# Setup 2x16 lcd display
init_lcd()

try:
    import sys
    import time
    import soco # type: ignore
    import threading

    # Support for Sonos events
    from queue import Empty
    from soco.events import event_listener # type: ignore
except KeyboardInterrupt:
    lcd.cleanup()
    sys.exit(0)

# Initialise variables
CurrentStation = 0
Time = 0
PowerTime = 0
ClockCount = 0
StoppedTime = 0
NewLine1 = ''
NewLine2 = ''
Scrolling = True
Enabled = True
AlwaysShowTime = False
Shutdown = False

try:
    # Connect to Sonos system and get current transport state
    sonos = connect_to_sonos()
    state = sonos.get_current_transport_info()['current_transport_state']

    # Create the large custom characters for the clock
    setup_clock_font()

    # Create thread to update the LCD display
    display_thread = threading.Thread(target = display_scrolling)
    display_thread.daemon = True
    display_thread.start()

    # Subscribe to transport messages from the Sonos
    sub = sonos.avTransport.subscribe(requested_timeout = 60, auto_renew = True)

    # Create a handler for connection errors
    sub.auto_renew_fail=errback

    # Create thread to handle IR input
    ir_thread = threading.Thread(target = get_ir_input)
    ir_thread.daemon = True
    ir_thread.start()

except KeyboardInterrupt:
    lcd.cleanup()
    sys.exit(0)

# Create a handler to run at exit
import atexit
atexit.register(cleanup)

try:
    # Main loop
    while (not Shutdown):
        event = ''
        try:
            # Get an event from sonos
            event = sub.events.get(timeout=0.1)
        except Empty:
            pass
        except KeyboardInterrupt:
            # Handle keyboard interrupt
            break
        if event != '':
            if 'transport_state' in event.variables:
                # Update the transport state
                state = event.variables['transport_state']

        # Update the LCD buffers with current track info
        try:
            display_track_info(state)
        except KeyboardInterrupt:
            # Handle keyboard interrupt
            break

        # Pause for a short time to avoid consuming excessive CPU
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            # Handle keyboard interrupt
            break

finally:
    # Clean up subscription
    event_listener.stop()
 