# pisonos

A Raspberry Pi based remote control and LCD display for Sonos (also a clock).

## Build Components

- Raspberry Pi - any should work, tested on Pi 3 Model B Rev 1.2, 1GB
- Adafruit RGB LCD kit for Raspberry Pi, e.g. [this one](https://www.adafruit.com/product/1110)
- Miniature IR Receiver module, e.g. [this one](https://hobbycomponents.com/opto-electronics/463-1838b-infrared-ir-receiver)
- Jumper wires to attach IR Receiver
- Remote control like [this](https://www.aliexpress.com/item/1005002081959107.html)
- Case (optional) - I used [this](https://thepihut.com/products/modmypi-adafruit-16x2-lcd-screen-case?srsltid=AfmBOorhfcRfZjTSCbsUtXaS8RMoi6B2NXOTRrtWFNtPT4AFw15qLh0m), sadly no longer available :-(

## Build Instructions

- Connect the Adafruit LCD to the Raspberry Pi
- Connect power pin of IR Receiver to 3.3v GPIO power
- Connect ground pin of IR Receiver to GPIO ground
- Connect signal pin of IR Receiver to GPIO pin 18

## Setup Instructions

- Clone this repo somewhere where you can run bash and connect to your Pi.
- Create a file in the root of the repo named *something*.cfg where *something* is the network address of your Pi.
- Add this line to the file...
    player='*name*'  
    ...where *name* is the room name of your Sonos target device.
- Run install.sh.

## License

pisonos is is released under the [MIT license](https://opensource.org/license/mit).
