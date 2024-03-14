# Blue and Pink Synth Editor
A full-featured editor for the Dreadbox Nymphes synthesizer. 
Uses [nymphes-osc](https://github.com/jtpack/nymphes-osc) in a separate process to do the actual communication with the Nymphes.

2024, Scott Lumsden


## This is ALPHA software.
## Platforms:
- macOS
- Linux (Including RPi)
- Windows (Possibly. Not tested)

## Supports Nymphes Firmware Version: 2.0

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
- On Mac OS / Linux:
  - `python3 -m venv venv`
  - `source venv/bin/activate`

- On Windows:
  - `py -3 -m venv venv`
  - `venv\scripts\activate`

## Install nymphes-osc in the virtual environment as an editable package
  - `pip install -e ~/nymphes-osc`
    - _Note: On Windows you may need to replace ~ with the full path to your home directory_

## 4. Install Blue-and-Pink-Synth-Editor in the virtual environment as an editable package
- `pip install -e .`

## 5. Run Blue-and-Pink-Synth-Editor
- `python -m blue_and_pink_synth_editor`

## 6. Compile an executable binary
-   `pyinstaller BlueAndPinkSynthEditor.spec`

When the build finishes, the executable will be found in the dist folder.
- On macOS this will be dist/BlueAndPinkSynthEditor.app
  - You can ignore the dist/BlueAndPinkSynthEditor folder
