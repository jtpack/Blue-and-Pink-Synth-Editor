# NymphesEdit
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

## 1. Download nymphes-osc

Clone the repository to your home directory
- `cd ~`
- `git clone https://github.com/jtpack/nymphes-osc.git`

## 2. Download NymphesEdit
Clone the repository to your home directory
- `cd ~`
- `git clone git@github.com:jtpack/NymphesEdit.git`

## 2. Create a virtual environment for NymphesEdit and activate it
Change to the NymphesEdit directory:
  - `cd ~/NymphesEdit`

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

## 4. Install NymphesEdit in the virtual environment as an editable package
- `pip install -e .`

## 5. Run NymphesEdit
- `python -m nymphes_edit`

## 6. Compile an executable binary
-   `pyinstaller NymphesEdit.spec`

When the build finishes, the executable will be found in the dist folder.
- On macOS this will be dist/NymphesEdit.app
  - You can ignore the dist/NymphesEdit folder.
- On Windows, you need both dist/NymphesEdit.exe and the dist/_internal folder.
  - Windows Defender or other anti-virus software may interfere with compilation or incorrectly flag the compiled executable as a virus
    - This is an issue related to pyinstaller
      - Do not worry: you have not created a virus

