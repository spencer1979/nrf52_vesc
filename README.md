# nrf52_vesc

## Build environment setup on Ubuntu:
1. Install packages:
```bash
sudo apt install build-essential srecord binutils-arm-none-eabi libnewlib-dev libnewlib-arm-none-eabi
```
2. Unzip NRF SDK: nRF5_SDK_15.3.0_59ac345.zip
3. Install toolchain: gcc-arm-none-eabi_7-2018-q2-6_amd64.deb

## Build NRF52832 for SPEsc
1. Modify 'SDK_ROOT' in Makefile. This is the path for NRF SDK which unzipped in environment setup step. 
2. Use cust build script and enter desired BLE name.
```bash
cd build_all
./build_52832
```
3. Final binary will be: nrf52832_vesc_ble_rx8_tx6_led3.bin

## Flash SPEsc NRF5 via VESC tool 3.01:
1. Use USB cable to connect to VESC, and Choose connect in VESC tool.
2. Enter "SWD programmer"
3. Choose "Connect NRF5X" at right bottom corner, then should see connected NRF at left bottom corner
4. Enter "Custom File" tab and choose firmware
5. Choose "Erase & Upload"

## Vedder's Readme
This is code for the NRF52832 and the NRF52840 for communicating between the VESC and VESC Tool (linux and mobile) over BLE. After uploading the firmware, the NRF can be connected to the VESC using the RX and TX pins chosen in main.c, and the BLE scanner in VESC Tool should be able to find it and connect. Note that the UART port on the VESC must be enabled with a baud rate of 115200 for this to work. The NRF can also communicate with the VESC Remote at the same time as it runs BLE.  

The code can be build with the NRF52 SDK by changing the path in Makefile. There is a variable in the makefile called IS_52832. If it is set to 1, the code is built for the NRF52832, otherwise it is built for the NRF52840. The difference between the two is which files are included from the NRF SDK and whether USB-CDC support is used in main.c. For now USB-CDC is only useful for printing debug information, but later it might be possible to connect VESC Tool over it.

This is how to connect an STLINK V2 to the NRF52 for uploading the code:

| NRF52         | STLINK V2     |
| ------------- |---------------|
| GND           | GND           |
| VDD           | 3.3V          |
| SDO           | SWDIO         |
| SCL           | SWCLK         |

The first time the code is uploaded mass_erase must be run, and the softdevice must be uploaded. This can be done with the following make rules:

```bash
make mass_erase
```

```bash
make upload_sd
```

after that and after future changes only the code itself needs to be uploaded:

```bash
make upload
```

After the code is uploaded, the NRF52 can be connected to the VESC in the following way:

| NRF52         | VESC          |
| ------------- |---------------|
| GND           | GND           |
| VDD           | VCC (3.3V)    |
| Px.y (TX)     | RX            |
| Px2.y2 (RX)   | TX            |

Note that a 10 uF ceremaic capacitor between VCC and GND close to the NRF52 module might be needed if the cables are long. Otherwise the connection can become slow and unstable.

