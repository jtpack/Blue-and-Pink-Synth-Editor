# Blue and Pink Synth Editor
An editor for the Dreadbox Nymphes synthesizer. 

If you encounter any problems, please create an issue here: https://github.com/jtpack/Blue-and-Pink-Synth-Editor/issues.
I will do my best to help.

If you would like to join the Blue and Pink Synth Editor discord server, use the invitation link on the Settings page inside the app.

2025, Scott Lumsden


# How to Get It

Blue and Pink Synth Editor is open source.
If you're a python programmer, you can follow the instructions in the Installation section below to download the source code and run it on your computer.
Blue and Pink Synth Editor will always be free to use in this way.

If you are not a programmer, you can download a pre-compiled version at https://scottlumsden.com/blueandpinksyntheditor. 
The pre-compiled version runs as a time-limited fully-functional demo.
You can purchase an activation code for $20 to remove the time limit.
It's a one-time purchase and your code will work for all future versions of Blue and Pink Synth Editor.


# Platforms

- macOS
- Linux (Lightly tested with Debian 12 inside VirtualBox on a Mac)
  - It is unknown whether this will work on a computer running Linux as its actual OS
- Raspberry Pi with a Touchscreen (Use this repository: https://github.com/jtpack/Blue-and-Pink-Synth-Editor-RPi)
- Windows support is planned for the future
  - Note: There is an issue with rtmidi on Windows which prevents the reception of large SYSEX messages (like preset dumps from Nymphes)
    - This means that when a preset is loaded on Nymphes, we only get its parameters via MIDI CC
      - This means we do not get parameters as float values, and we also do not get chord parameters
    - This does not stop us from sending these parameters to the Nymphes as a SYSEX message.


# Features

- View and edit all MIDI-controllable Nymphes parameters, including modulation matrix and chords
- Recall presets
- Request SYSEX dump of all presets
- Decode and generate Nymphes preset dump messages
  - This provides full floating-point resolution for most parameters, not just 0-127 MIDI CC values
- Save directly to User and Factory preset slots
- Save presets to files and load them later
  - These are human-readable .txt files which can be opened to see the value of all 235 parameters that make up a preset
- Convert .syx SYSEX preset files to .txt preset files
  - This allows you to see their settings, and to load them without overwriting your Nymphes' preset slots
- MIDI pass-through from input ports to Nymphes
- MIDI pass-through from Nymphes to output ports


# Nymphes Preparation

- Make sure you have Nymphes Firmware Version 2.1 (the current version as of this writing - January 2025)
- Make sure that MIDI CC send/receive is turned ON
- Make sure that MIDI Program Change send/receive is turned ON
- Make sure that you choose the correct MIDI channel on the Settings page in Blue and Pink Synth Editor

  
# Installation

## 1. Download nymphes-osc

Clone the repository to your home directory
- `$ cd ~`
- `$ git clone https://github.com/jtpack/nymphes-osc.git`

## 2. Download Blue and Pink Synth Editor
Clone the repository to your home directory
- `$ cd ~`
- `$ git clone https://github.com/jtpack/Blue-and-Pink-Synth-Editor.git`

## 2. Create a virtual environment for Blue-and-Pink-Synth-Editor and activate it
- `$ cd ~/Blue-and-Pink-Synth-Editor`
- `$ python3 -m venv venv`
- `$ source venv/bin/activate`

## Install nymphes-osc in the virtual environment as an editable package
- `$ pip install -e ~/nymphes-osc`

## 4. Install Blue-and-Pink-Synth-Editor in the virtual environment as an editable package
- `$ pip install -e .`

## 5. Run Blue-and-Pink-Synth-Editor to make sure it works
- `$ python -m blue_and_pink_synth_editor`

## 6. Compile the app into an executable binary
- `$ pyinstaller BlueAndPinkSynthEditor.spec`

## 7. Run it from the command line to make sure it works

### macOS:
- `dist/BlueAndPinkSynthEditor.app/Contents/MacOS/BlueAndPinkSynthEditor`

### Linux:
- `dist/BlueAndPinkSynthEditor/BlueAndPinkSynthEditor`

## 8. On macOS, move the compiled app to /Applications
- `mv dist/BlueAndPinkSynthEditor.app /Applications/`
- From now on you can run the compiled app by double-clicking on it in the Applications folder
