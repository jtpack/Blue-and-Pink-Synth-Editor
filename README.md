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
- Windows
- Linux (Lightly tested with Debian 12 inside VirtualBox)
  - It is unknown whether this will work on a computer running Linux as its actual OS
- Raspberry Pi with a Touchscreen (Use this repository: https://github.com/jtpack/Blue-and-Pink-Synth-Editor-RPi)


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
- Creates virtual MIDI input and output ports so you can record and automate from a DAW like Ableton Live, Logic, etc


# Nymphes Preparation

- Make sure you have Nymphes Firmware Version 2.1 (the current version as of this writing - January 2025)
- Make sure that MIDI CC send/receive is turned ON
- Make sure that MIDI Program Change send/receive is turned ON
- Make sure that you choose the correct MIDI channel on the Settings page in Blue and Pink Synth Editor

  
# Installation

## 1. Download nymphes-osc

Clone the nymphes-osc repository to your home directory
- `$ cd ~`
- `$ git clone https://github.com/jtpack/nymphes-osc.git`

## 2. Download Blue and Pink Synth Editor
Clone the Blue-and-Pink-Synth-Editor repository to your home directory
- `$ cd ~`
- `$ git clone https://github.com/jtpack/Blue-and-Pink-Synth-Editor.git`

## 3. Create a virtual environment for Blue-and-Pink-Synth-Editor and activate it
- `$ cd ~/Blue-and-Pink-Synth-Editor`
- macOS and Linux: 
  - `$ python3 -m venv venv`
  - `$ source venv/bin/activate`
- Windows: 
  - `$ py -3 -m venv venv`
  - `$ venv\Scripts\activate`
  - _If you are using Windows PowerShell and get an error message, you may need to first use the following command:_ 
    - `$ Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

## 4. Install nymphes-osc in the virtual environment as an editable package
- macOS and Linux: `$ pip install -e ~/nymphes-osc`
- Windows: `$ pip install -e <full absolute path to nymphes-osc folder>`
  - ie: `$ pip install -e C:\Users\jtpac\nymphes-osc`

### Windows: Manual Installation of python-rtmidi
Make sure you have Cmake installed
- Download python-rtmidi source code
  - `$ cd ~/Blue-and-Pink-Synth-Editor`
  - `$ git clone --recurse-submodules https://github.com/SpotlightKid/python-rtmidi.git`
- Increase the RtMidiInData bufferSize in RtMidi.h
  - `$ cd ~/Blue-and-Pink-Synth-Editor/python-rtmidi/src/rtmidi`
  - Open RtMidi.h and find the RtMidiInData Default constructor
    - Change `bufferSize(1024)` to `bufferSize(8196)`
    - Save the file
  - Commit the changes to the local python-midi and rtmidi repositories
    - This appears to be necessary for the changes to work
    - `$ cd ~/Blue-and-Pink-Synth-Editor/python-rtmidi/src/rtmidi`
    - `$ git add RtMidi.h`
    - `$ git commit -m "Increased bufferSize to 8196 in RtMidiInData default constructor"`
    - `$ cd ~/Blue-and-Pink-Synth-Editor/python-rtmidi`
    - `$ git add -A`
    - `$ git commit -m "Increased bufferSize to 8196 in RtMidiInData default constructor"`
- Install packages needed to build a wheel and install it
  - `$ pip install build installer`
- Build the wheel
  - `$ cd ~/Blue-and-Pink-Synth-Editor/python-rtmidi`
  - `$ python -m build`
- Install the newly-built wheel into the virtual environment
  - `$ python -m installer <Full absolute path to the .whl file that was just built>`
    - example: `$ python -m installer C:\Users\scott\nymphes-osc\python-rtmidi\dist\python_rtmidi-1.5.8-cp312-cp312-win_amd64.whl`

## 5. Install Blue-and-Pink-Synth-Editor in the virtual environment as an editable package
- `$ cd ~/Blue-and-Pink-Synth-Editor`
- `$ pip install -e .`

## 6. Run Blue-and-Pink-Synth-Editor to make sure it works
- `$ python -m blue_and_pink_synth_editor`

## 7. Compile the app into an executable binary
- `$ pyinstaller BlueAndPinkSynthEditor.spec`

## 8. Run it from the command line to make sure it works
- macOS:
  - `$ dist/BlueAndPinkSynthEditor.app/Contents/MacOS/BlueAndPinkSynthEditor`
- Windows:
  - `$ dist/BlueAndPinkSynthEditor/BlueAndPinkSynthEditor.exe`
- Linux:
  - `$ dist/BlueAndPinkSynthEditor/BlueAndPinkSynthEditor`

## 9. Run it by double-clicking its icon
- macOS:
  - Double-click the file at `~/Blue-and-Pink-Synth-Editor/dist/BlueAndPinkSynthEditor.app`
- Windows:
  - Double-click the file at `~/Blue-and-Pink-Synth-Editor/dist/BlueAndPinkSynthEditor/BlueAndPinkSynthEditor.exe`

## 10. On macOS, move the compiled app to /Applications
- `mv dist/BlueAndPinkSynthEditor.app /Applications/`
- From now on you can run the compiled app by double-clicking on it in the Applications folder
