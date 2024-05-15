- Added automatic font size adjustment on presets spinner text, so that filenames longer than 20 characters can still be read.
- Improved UI on all mouse-controllable elements
  - Now when the mouse enters any control, the control grows slightly
  - Control element size is used to show that a click has happened
- Disabled kivy settings editor activated by pressing F1 key because it is not needed and is confusing
  - I didn't even know that it existed until I accidentally pressed F1 and the dialog appeared.
- Reorganization to make it a lot easier to navigate the project:
  - Moved most of the miscellaneous kivy subclasses into a new file: misc_widgets.py
  - Moved dialog classes to their own files
  - Moved SynthEditorValueControl-related classes to a new file: synth_editor_value_controls.py
  - Now BlueAndPinkSynthEditorApp.py contains just the app class.
- Added handling of /poly_aftertouch OSC message that has just been added to nymphes-osc



## v0.2.3-beta

- Added file drag support for both txt preset files and syx files 
- Fixed possible bug - some properties received by OSC were not being updated on the main thread
- Presets spinner now shows the loaded filename without its extension
- Added Error Dialog which pops up when an error occurs


## v0.2.2-beta

- All user-controllable UI elements now show visual feedback when the mouse touches them
  - A short helpful description also appears in the status bar at the bottom left of the window
- In the Chords screen, clicking on a specific chord section title now sends the MIDI CC value to activate the chord
- All buttons are now activated on click, not on release.
  - This improves the responsiveness
- Fixed bug where changing Nymphes output port also affected the input port.
- Improved logging so it is easier to understand.
- Moved presets folder to ~/Library/Application Support/Blue and Pink Synth Editor/ so now we no longer need a folder inside /Applications
- Added MISC section to Settings screen
  - Added a button to open the presets folder in the native file explorer (Finder on macOS, Windows Explorer on Windows, not sure on Linux)
  - Added a button to open the kivy logs folder in the same way


## v0.2.1-beta

- Renamed chord controls to match the changes in nymphes-osc

Changes from nymphes-osc repository:
- Discovered that chord semitone values can be negative
  - Adjusted range to -127 to 127
- Renamed chords to better match what is written in the Nymphes Manual
  - Now the seven normal chords are named 1 through 7, and the default chord is chord 0
  - Note: All old preset files are incompatible unless you rename the chords to match!
- Legato Fix: Turns out Nymphes actually sends a value of 127 when legato is enabled, not 1 as indicated in the Nymphes manual
  - Now we do the same


## v0.2.0-beta

- No change to BlueAndPinkSynthEditor, but a major bug was fixed in nymphes-osc, which prevented /loaded_preset from being sent when a preset was loaded via Program Change from a MIDI port.


## v0.1.9-beta

- Had to revise the folder structure, as we don't have write access for the config file if it is inside the app bundle and has been installed using the pkg installer.
  - Now we are using ~/Library/Application Support/Blue and Pink Synth Editor/
- I also realized that none of this would work for platforms other than macOS, so for those platforms I've gone back to ~/Blue and Pink Synth Editor Data/ for both presets and config files.


## v0.1.8-beta

- Finalized the folder structure for app data and presets. Now programmers and regular users will all have a consistent experience with file locations.
  - Now the app automatically creates /Applications/Blue and Pink Synth Editor/ if necessary on start
    - Then it checks for /Applications/Blue and Pink Synth Editor/presets/ and creates it if necessary
- Updated instructions in README to instruct readers to move the app to /Applications/Blue and Pink Synth Editor/ after compiling


## v0.1.7-beta

- When the mouse is over a control the cursor becomes a hand.
- The Aftertouch control at the bottom of the window now shows the latest aftertouch value regardless of MIDI channel
  - This is to better support MPE
  - When adjusting the control, a channel aftertouch message is sent to Nymphes on its channel
 

## v0.1.6-beta

- Added Nymphes MIDI Channel control on settings page
  - Bugfixes were necessary in nymphes-osc, so make sure you pull the latest version of it.
- Moved config.txt to the app bundle


## v0.1.5-beta

- Calling this BETA software now, not ALPHA
- Changed reload button text to REVERT
- Renamed Float Mode to Fine Mode, as this is a little clearer
- Increased font size of Play Mode buttons
- Discovered that not all white labels were the same color. Fixed it.
- Now there are save and revert buttons
  - They are enabled when there are unsaved changes to the current preset
  - The save button updates the current preset
    - If the current preset is a file then it saves to the file
    - If the current preset is a Nymphes memory slot, then the slot is updated
  - The revert button reloads the current preset


## v0.1.4-beta

- The app was renamed

  
## v0.1.3-beta

- Created chords screen

- Small UI colors improvements
  - The LFO1 and LFO2 label colors look better now, I think


## v0.1.2-beta

- Created status bar at bottom of window
  - Displays status messages
  - Lets user know when Nymphes is not connected
  - Shows parameter values if the mouse hovers over a control
  - Shows most recent mod wheel, velocity and aftertouch values
    - The mod wheel and aftertouch labels also can be used to send a new mod wheel or aftertouch message to Nymphes

- Improved colors
  - More improvement is still possible
