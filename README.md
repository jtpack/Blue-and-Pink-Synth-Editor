# nymphes-gui
A graphical editor for the Dreadbox Nymphes synthesizer. 
Uses [nymphes-osc](https://github.com/jtpack/nymphes-osc) in a separate process to do the actual communication with the Nymphes.

2024, Scott Lumsden

## This is ALPHA software.

## Platforms:
- macOS
- Linux (Including RPi)
- Windows (Most functions work)

## Supports Nymphes Firmware Version: 2.0

# Installation

## 1. Clone this repository to your home directory
- `cd ~`
- `git clone git@github.com:jtpack/nymphes-gui.git`

## 2. Create a virtual environment and activate it
- `cd ~/nymphes-gui`
#### Mac OS / Linux:
- `python3 -m venv venv`
- `source venv/bin/activate`
#### Windows:
- `py -3 -m venv venv`
- `venv\scripts\activate`

## 3. Install Dependencies

### nymphes-osc
- Clone the repository to your home directory
  - `cd ~`
  - `git clone https://github.com/jtpack/nymphes-osc.git`
- Go back to the nymphes-gui directory
  - `cd ~/nymphes-gui`
- Install nymphes-osc in your virtual environment as an editable package
  - `pip install -e ~/nymphes-osc`
    - _Note: On Windows you may need to replace ~ with the full path to your home directory_

## 4. Install nymphes-gui itself
- `pip install -e .`

## 5. Run nymphes-gui
- `python -m nymphes_gui`

## 6. Compile an executable binary
-   `pyinstaller NymphesEdit.spec`

When the build finishes, the executable will be found in the dist folder.
- On macOS this will be dist/NymphesEdit.app
  - You can ignore the dist/NymphesEdit folder.
- On Windows, you need both dist/NymphesEdit.exe and the dist/_internal folder.
  - Windows Defender or other anti-virus software may interfere with compilation or incorrectly flag the compiled executable as a virus
    - This is an issue related to pyinstaller
      - Do not worry: you have not created a virus

