# Blue and Pink Synth Editor on Raspberry Pi with [Raspberry Pi Touch Display](https://www.raspberrypi.com/products/raspberry-pi-touch-display/)

A full-featured editor for the Dreadbox Nymphes synthesizer. 

These instructions will get you started using it on Raspberry Pi with a touchscreen.

2024, Scott Lumsden

# Features

- View and edit all MIDI-controllable Nymphes parameters in a preset, including modulation matrix and chords
- Recall presets via MIDI Program Change and Bank MSB Messages
- Request SYSEX dump of all presets
- Decode and generate Nymphes preset SYSEX messages
  - This allows full floating-point resolution for most parameters, not just 0-127 MIDI CC values
- Save and load preset files
  - These are human-readable txt files
- Convert syx SYSEX preset files to txt preset files
  - This allows you to see their settings, and to choose where or whether to store them in Nymphes' preset slots
- MIDI pass-through from input ports to Nymphes
- MIDI pass-through from Nymphes to output ports


# Instructions

# Nymphes Setup
- Make sure you have Nymphes Firmware Version 2.1 (the latest version as of March 2024)
- Make sure that MIDI CC send/receive is turned ON
- Make sure that MIDI Program Change send/receive is turned ON
- Make sure that you choose the correct MIDI channel on the Settings page in Blue and Pink Synth Editor

*For assistance with Nymphes' menu system: see the [Dreadbox Nymphes Manual](https://www.dreadbox-fx.com/wp-content/uploads/2024/03/Nymphes_Owners-Manual-v2.0.pdf)*


# 1. Hardware

Tested Raspberry Pi Models:
- Raspberry Pi 5
- Raspberry Pi 4

Tested Touchscreens:
- [Raspberry Pi Touch Display](https://www.raspberrypi.com/products/raspberry-pi-touch-display/)


# 2. Operating System
*These instructions are for the latest version of Raspberry Pi OS (Bookworm)*

## Flash Micro-SD Card with Raspberry Pi OS

### Use Raspberry Pi Imager (https://www.raspberrypi.com/software/)

- First Screen
  - Choose Raspberry Pi 5
  - Choose Raspberry Pi OS (64 Bit)
    - This is also known as "Bookworm"
  - Choose your micro-SD card
  - Click Next

- Next Screen
  - Click EDIT SETTINGS
  
- OS Customisation Screen
  - General Tab
    - Choose a hostname that you like
    - Set username and password
    - Configure wireless LAN (if you will be using Wi-Fi)
    - Set the local settings to match where you are

  - Services Tab
    - Enable SSH
      - Choose "Use password authentication"
        - This is the default
  - Click SAVE

- Next Dialog
  - Click YES to apply customization settings you've just set

- Next Dialog
  - Click YES to continue


# 3. Raspberry Pi Configuration

### Insert SD Card and Power Up Raspberry Pi

### Log In via SSH
- `$ ssh <username>@apollo.local`
  - Substitute the username you chose in the previous section

### Configure Displays

*Two displays will be enabled: DSI-1 (the touchscreen, which will show Blue and Pink Synth Editor in fullscreen), and HDMI-1 (a larger virtual screen which will be used visible using VNC for programming and general access)*

#### Edit /boot/firmware/cmdline.txt:
- `$ sudo nano /boot/firmware/cmdline.txt`
- Add the following to the end of the single line in the file (do not create a 2nd line):
  - ` video=DSI-1:800x480D video=HDMI-A-2:1920x1080MRD`
- Save and exit nano

### Reboot
- `$ sudo reboot`

### Enable X11
*We are using X11 instead of Wayland because VNC support with Wayland currently does not support showing more than one display*

- `$ sudo raspi-config`
  - Select Advanced Options
  - Select Wayland
  - Select X11
  - Select Finish
  - Select Yes to reboot

### Enable VNC
- `$ sudo raspi-config`
  - Select Interface Options
  - Select VNC
  - Select YES

### Log In Via VNC
*Use [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) if you don't already have a VNC client preference*
- Username and password will be the same as with ssh

### Configure Displays Layout
- Main Menu -> Preferences -> Screen Configuration
  - Layout Menu -> Screens -> HDMI-1-2 -> Active
    - The HDMI-1-2 screen appears in the Screen Layout Editor
  - Move the HDMI-1-2 screen to the right of the DSI-1 screen
  - Click Apply and then click Yes to keep the settings

### Map Touch Interface to Control Only the LCD

#### Check the name of the LCD's screen:

- `$ xrandr`
- in the listing, take note of the name of the DSI screen
	- It will probably be `DSI-1`

#### Check the id of the touch interface:

- `$ xinput`
- In the listing, take note of the id of the device with the name `6-0038 generic ft5x06 (79)` or similar
	- It will likely be 6

#### Test-map the touch interface to the LCD:

- `$ xinput map-to-output 6 DSI-1`
	- Substitute touch id and screen name if yours are different
- Touch and drag on the touchscreen
	- Make sure that the mouse cursor moves correctly under your finger, and only appears on the LCD

#### If the mapping worked, make it permanent:
- `$ nano ~/.xsessionrc`
  - Add the mapping command on its own line
    - ie: `xinput map-to-output 6 DSI-1`
  - Save the file and exit nano

#### Make sure the touchscreen mapping is correctly loaded on boot
- `$ sudo reboot`
- When finished booting, try touchscreen

### Enable Samba for Sharing the Home Folder on the Network
*This makes it easy to access presets, logs and other files from another computer*

#### Install Samba:
- `$ sudo apt-get install samba samba-common-bin`

#### Edit Samba config:
- `$ sudo nano /etc/samba/smb.conf`
  - In the `[homes]` section:
    - Set `writeable = yes`
    - Set `browseable = yes`

#### Set a Samba password for the user:
- `$ sudo smbpasswd -a <username>`
  - You will be prompted to enter a password

#### Restart Samba:
- `$ sudo systemctl restart smbd`

#### Verify Samba is Working:
- On your other computer, use your file explorer (Finder on macOS, Windows Explorer on Windows) to find the shared folder from the Raspberry Pi, and try to access it

## (Optional) Install Useful Development Tools

### Visual Studio Code

#### - Install Visual Studio Code:
- `$ sudo apt-get install code`

#### - Run Visual Studio Code:
- Main Menu -> Programming -> Visual Studio Code

#### - Install Useful Extensions:
- Go to Extensions
- Find the python extension (made by Microsoft) and install it
- Install the Gitlens extension

### Protokol
*For debugging MIDI and OSC messages*

#### - Download Protokol:
- Use web browser to go to hexler.net/protokol
- Download the ARM/32-bit/Raspberry Pi .deb package file

#### - Install Protokol:
- Use the file browser to go to ~/Downloads
- Right-click on the .deb file you've just downloaded, and choose "Package Install"

#### - Run Protokol:
- Raspberry Pi Menu -> Programming -> Protokol


# Blue and Pink Synth Editor Installation

## Install dependencies
```
$ sudo apt-get -y install build-essential git make autoconf automake libtool \
pkg-config cmake ninja-build libasound2-dev libpulse-dev libaudio-dev \
libjack-dev libsndio-dev libsamplerate0-dev libx11-dev libxext-dev \
libxrandr-dev libxcursor-dev libxfixes-dev libxi-dev libxss-dev libwayland-dev \
libxkbcommon-dev libdrm-dev libgbm-dev libgl1-mesa-dev libgles2-mesa-dev \
libegl1-mesa-dev libdbus-1-dev libibus-1.0-dev libudev-dev fcitx-libs-dev
```

```
$ sudo apt-get install xorg wget libxrender-dev lsb-release libraspberrypi-dev raspberrypi-kernel-headers
```

## Download nymphes-osc Respository

- `$ cd ~`
- `$ git clone https://github.com/jtpack/nymphes-osc.git`

## Download Blue and Pink Synth Editor Respository

- `$ cd ~`
- `$ git clone git@github.com:jtpack/Blue-and-Pink-Synth-Editor.git`

## Create a virtual environment for Blue-and-Pink-Synth-Editor and activate it

- `$ cd ~/Blue-and-Pink-Synth-Editor`
- `$ python3 -m venv venv`
- `$ source venv/bin/activate`

## Install nymphes-osc in the virtual environment

- `$ pip install -e ~/nymphes-osc`

## Install Blue-and-Pink-Synth-Editor in the virtual environment

- `$ pip install -e .`

## Run Blue-and-Pink-Synth-Editor to make sure it works

- `$ python -m blue_and_pink_synth_editor`

## Compile the app into an executable binary

- `$ pyinstaller BlueAndPinkSynthEditor.spec`

## Run the compiled app to make sure it works

- `$ dist/BlueAndPinkSynthEditor/BlueAndPinkSynthEditor`

## Move the compiled app to /usr/local/bin

- `$ sudo mv dist/BlueAndPinkSynthEditor/ /usr/local/bin/Blue-and-Pink-Synth-Editor/dist/BlueAndPinkSynthEditor/BlueAndPinkSynthEditor`

## Add Entry in Raspberry Pi Main Menu
- `$ sudo cp BlueAndPinkSynthEditor.desktop /usr/share/applications`

## Make Blue and Pink Synth Editor Run Automatically on Boot

#### - Create `~/.config/autostart/` directory if it doesn't exist:
- `$ mkdir ~/.config/autostart`

#### - Copy desktop file to autostart directory:
- `$ cp BlueAndPinkSynthEditor.desktop ~/.config/autostart`

#### - Reboot:
- `$ sudo reboot`

## How to quit Blue and Pink Synth Editor
Press the Escape Key
