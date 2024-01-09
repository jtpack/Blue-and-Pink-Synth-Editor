# nymphes-gui
A friendly user interface for nymphes-osc

2024, Scott Lumsden

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
  - `git clone git@github.com:jtpack/nymphes-osc.git`
- Go back to the nymphes-gui directory
  - `cd ~/nymphes-gui`
- Install nymphes-osc in your virtual environment as an editable package
  - `pip install -e ~/nymphes-osc`
    - _Note: On Windows you may need to replace ~ with the full path to your home directory_

## 4. Install nymphes-gui itself
  - `pip install -e .`

## 4. Run nymphes-gui
  - `python -m nymphes_gui`
