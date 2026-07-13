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
You can purchase an activation code to remove the time limit.
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

## 0. Install the Required Basic Tools

### Python (Install a recent stable version of Python 3, not Python 2)
- macOS / Linux: Download and install from https://www.python.org/downloads/
- Windows: Download using the Windows App Store: https://apps.microsoft.com/detail/9PNRBTZXMB4Z?hl=en-us&gl=US&ocid=pdpshare

### Git
- macOS: Go to the git website and follow the instructions for one of the installation methods: https://git-scm.com/install/mac
- Windows: Download and install from the git website: https://git-scm.com/install/windows
- Linux: Go to the git website and follow the instructions: https://git-scm.com/install/linux

## Extra Tools to Install on Windows

### CMake
Download and run the CMake installer: https://cmake.org/download/

### Visual Studio Code
This one is optional, but it's a nice free code editor with a built-in terminal, and it will be nicer to use than `notepad.exe` when you need to edit `RtMidi.h` later on. Get it here: https://code.visualstudio.com/download


## 1. Download nymphes-osc

From the Terminal (use PowerShell or Git Bash on Windows), navigate to your home directory
- `cd ~`

Clone the nymphes-osc repository to your home directory
- `git clone https://github.com/jtpack/nymphes-osc.git`

## 2. Download Blue and Pink Synth Editor

 While still in your home directory, clone the Blue-and-Pink-Synth-Editor repository
- `git clone https://github.com/jtpack/Blue-and-Pink-Synth-Editor.git`

## 3. Create a virtual environment for Blue-and-Pink-Synth-Editor and activate it

- `cd ~/Blue-and-Pink-Synth-Editor`
- macOS and Linux: 
  - `python3 -m venv venv`
  - `source venv/bin/activate`
- Windows: 
  - `py -3 -m venv venv`
  - `venv\Scripts\activate`
    - If you are using Windows PowerShell and get an error message indicating that running scripts is disabled on your system, enter the following command and then try again: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

## 4. Install nymphes-osc in the virtual environment as an editable package
Make sure you are still in the Blue-and-Pink-Synth-Editor folder in your home directory (ie: `cd ~/Blue-and-Pink-Synth-Editor`)
- macOS and Linux: `pip install -e ~/nymphes-osc`
- Windows: On Windows you must enter the absolute path to the folder, so it will be something like this: `pip install -e C:\Users\jtpack\nymphes-osc`
  - Obviously, replace `jtpack` with your own username

## 4.1 (Only on Windows): Modify and Manually Install python-rtmidi
On Windows, an issue with MME MIDI prevents python-rtmidi from receiving large SYSEX messages like the ones Nymphes generates. This is solved by downloading the python-rtmidi source code, making a modification, compiling it, and then installing it into the python virtual environment.

- Download python-rtmidi source code
  - `cd ~/Blue-and-Pink-Synth-Editor`
  - `git clone --recurse-submodules https://github.com/SpotlightKid/python-rtmidi.git`
- Increase the RtMidiInData bufferSize in RtMidi.h
  - `cd python-rtmidi/src/rtmidi`
  - Open RtMidi.h and find the RtMidiInData Default constructor
    - Change `bufferSize(1024)` to `bufferSize(8196)`
    - Save the file
  - Commit the changes to the local python-midi and rtmidi repositories
    - This appears to be necessary for the changes to work
    - `git add RtMidi.h`
    - `git commit -m "Increased bufferSize to 8196 in RtMidiInData default constructor"`
    - Navigate up one level (to `python-rtmidi/src/`):
      - `cd ..`
    - `git add -A`
    - `git commit -m "Increased bufferSize to 8196 in RtMidiInData default constructor"`
- Install packages needed to build a wheel and install it
  - `pip install build installer`
- Build the wheel
  - Navigate up one level (to `python-rtmidi/`):
      - `cd ..`
  - `python -m build`
- Install the newly-built wheel into the virtual environment
  - `python -m installer <Full absolute path to the .whl file that was just built>`
    - example: `python -m installer C:\Users\jtpack\Blue-and-Pink-Synth-Editor\python-rtmidi\dist\python_rtmidi-1.6.0-cp313-cp313-win_amd64.whl`
      - Replace `jtpack` with your own username, and replace the actual filename with the one that you created, as it may have a newer version in its name

## 5. Install Blue-and-Pink-Synth-Editor in the virtual environment as an editable package
- `cd ~/Blue-and-Pink-Synth-Editor`
- `pip install -e .`

## 6. Run Blue-and-Pink-Synth-Editor before compiling to make sure it works
- `python -m blue_and_pink_synth_editor`

## 7. Compile Blue and Pink Synth Editor
This makes it easier to run, just like any other app on your computer
- `pyinstaller BlueAndPinkSynthEditor.spec`

### Run it from the command line to make sure it works
Make sure you are in the `Blue-and-Pink-Synth-Editor` folder in your home directory.

Then:
- macOS:
  - `dist/BlueAndPinkSynthEditor.app/Contents/MacOS/BlueAndPinkSynthEditor`
  - Move the app to your Applications folder:
    - `mv dist/BlueAndPinkSynthEditor.app /Applications/`
- Windows:
  - `dist/BlueAndPinkSynthEditor/BlueAndPinkSynthEditor.exe`
- Linux:
  - `dist/BlueAndPinkSynthEditor/BlueAndPinkSynthEditor`

### Run it by double-clicking its icon

- macOS:
  - Use the Finder to navigate to your Applications folder, and double-click `BlueAndPinkSynthEditor.app`
- Windows:
  - Use Windows Explorer to navigate to the `Blue-and-Pink-Synth-Editor` folder in your home directory
  - Navigate to the `dist` folder
  - Double-click `BlueAndPinkSynthEditor/BlueAndPinkSynthEditor.exe`
  - Drag the app onto the Taskbar to create a link to it
