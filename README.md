# Blue and Pink Synth Editor
A full-featured editor for the Dreadbox Nymphes synthesizer. 
Uses [nymphes-osc](https://github.com/jtpack/nymphes-osc) in a separate process to do the actual communication with the Nymphes.

2024, Scott Lumsden

## This is BETA software

## Features

- Supports all MIDI-controllable Nymphes functions
- User and Factory preset recall via MIDI Program Change and Bank MSB Messages
- MIDI CC control of preset parameters, including the modulation matrix
- Request SYSEX dump of all presets
- Decode and generate SYSEX messages to access all preset parameters, including chords settings
  - This also means that most parameters have full floating-point resolution, not just 0-127 MIDI CC values
- Save and load presets as files
- User-controllable pass-through from MIDI input ports to Nymphes
- User-controllable pass-through from Nymphes to MIDI output ports


## Nymphes Settings
- Make sure you have Nymphes Firmware Version 2.1 (the latest version as of March 2024)
- Make sure that MIDI CC send/receive is turned ON
- Make sure that MIDI Program Change send/receive is turned ON
- Make sure that you choose the correct MIDI channel on the Settings page in Blue and Pink Synth Editor


## Platforms:
- macOS

Support for Linux and Windows is planned for the future

  
# Installation

## 1. Download nymphes-osc

Clone the repository to your home directory
- `cd ~`
- `git clone https://github.com/jtpack/nymphes-osc.git`

## 2. Download Blue and Pink Synth Editor
Clone the repository to your home directory
- `cd ~`
- `git clone git@github.com:jtpack/Blue-and-Pink-Synth-Editor.git`

## 2. Create a virtual environment for Blue-and-Pink-Synth-Editor and activate it
Change to the Blue-and-Pink-Synth-Editor directory:
  - `cd ~/Blue-and-Pink-Synth-Editor`

Create and activate the virtual environment:
- `python3 -m venv venv`
- `source venv/bin/activate`

## Install nymphes-osc in the virtual environment as an editable package
  - `pip install -e ~/nymphes-osc`

## 4. Install Blue-and-Pink-Synth-Editor in the virtual environment as an editable package
- `pip install -e .`

## 5. Run Blue-and-Pink-Synth-Editor to make sure it works
- `python -m blue_and_pink_synth_editor`

Note: The app checks for the Blue and Pink Synth Editor folder in /Applications when it runs. If the folder doesn't exist then it is created. Inside that the presets folder is created.

## 6. Compile the app into an executable binary
- `pyinstaller BlueAndPinkSynthEditor.spec`

## 7. Move the compiled app into the folder in /Applications
- `mv dist/BlueAndPinkSynthEditor.app /Applications/Blue\ and\ Pink\ Synth\ Editor`

## 8. Run the compiled app by double-clicking on it

- To see debug output on the console, run the app from the command line instead
  - `/Applications/Blue\ and\ Pink\ Synth\ Editor/BlueAndPinkSynthEditor.app/Contents/MacOS/BlueAndPinkSynthEditor`
