# pisonos

A Raspberry Pi based remote control and LCD display for Sonos (also a clock).

## Purpose

I like my Sonos smart speakers.
I don't much like having to use my phone to control them.
I mean, it's fine most of the time, but imagine I'm listening to some noisy music (at the appropriate volume) and I hear a knock at the door. It's probably someone come to tell me I've won a massive yacht! I really want to quickly mute the Sonos so they aren't greeted by a wall of noisy music (at the appropriate volume) and for some reason decide that's a good reason not to offer me a yacht. There are some buttons on the device itself but it's high up on a shelf and not convenient, so to do what I want to do I need to grab my phone, wait for it's addled brain to sort itself out enough to display the unlock screen, enter my unlock code, wait again for the app to open and then find the right button to mute the Sonos. By the time I've done all that my neighbour will have my yacht and I will be sad :-(.
This project solves this problem by converting a Raspberry Pi into a receiver for a remote control for the Sonos to control volume, tracks, stations and more.
While we're at it, it will also display track or station info on a 16x2 LCD screen.
If it's not doing any of that it will show the time in a large and friendly font because, why not?

## Build Components

- Raspberry Pi - any should work, tested on Pi 3 Model B Rev 1.2, 1GB.
- Adafruit RGB LCD kit for Raspberry Pi, e.g. [this one](https://www.adafruit.com/product/1110).
- Miniature IR Receiver module, e.g. [this one](https://hobbycomponents.com/opto-electronics/463-1838b-infrared-ir-receiver).
- Jumper wires to attach IR Receiver to GPIO.
- Remote control like [this](https://www.aliexpress.com/item/1005002081959107.html).
- Case (optional) - I used [this](https://thepihut.com/products/modmypi-adafruit-16x2-lcd-screen-case?srsltid=AfmBOorhfcRfZjTSCbsUtXaS8RMoi6B2NXOTRrtWFNtPT4AFw15qLh0m), sadly no longer available :-(.

## Build Instructions

- Connect the Adafruit LCD to the Raspberry Pi.
- Connect power pin of IR Receiver to 3.3v GPIO power.
- Connect ground pin of IR Receiver to GPIO ground.
- Connect signal pin of IR Receiver to GPIO pin 18.

## Setup Instructions

- Clone this repo somewhere where you can run bash and connect to your Pi.
- Create a file in the root of the repo named *ip*.cfg where *ip* is the network address of your Pi.
- Add this line to the file...  
    player='*name*'  
    ...where *name* is the room name of your Sonos target device.
- Run...  
  ./install.sh *ip*
  ...where *ip* is the network address of your Pi.

## License

pisonos is is released under the [MIT license](https://opensource.org/license/mit).
