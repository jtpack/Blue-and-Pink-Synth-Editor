- Fixed bug where dragging a beta test activation code file onto a non-beta version of the app still copied the file to the data folder


## v1.0.3-beta

- Windows is now supported, with exactly the same features and functionality as on macOS
  - Make sure you pull in the latest changes from nymphes-osc (v1.0.1 or later)


## v1.0.2-beta

- Added support for previously-undocumented /mod_source OSC message that nymphes-osc sends when it receives MIDI CC #30 from Nymphes
  - We don't do anything with the message other than log it
    - Support for the message may not really be necessary
- This is the first version that supports the Windows operating system
  - Changes related to this:
    - Added icon for Windows
    - Added support for correct native filebrowser on Windows
  - Open-source users should also get the latest changes for nymphes-osc


## v1.0.1

- Fixed bug where the MIDI Channel control only allowed channels 1-7 instead of 1-16


## v1.0.0

- Improved activation code logging
- Replaced support email address with new one from scottlumsden.com
- Increased status bar text length before reducing font size


## v0.3.8-beta

- Fixed bug where app wasn't verifying that beta test users have a beta test version


## v0.3.7-beta

### New Features / Improvements

- Enabled Activation Codes and Demo Mode in preparation for commercial app release
  - Only affects users who install the app using the installer
    - Open Source users who download the code from github will never need an activation code
  - Added Demo Mode popup which appears when app is started without an activation code
  - Added Demo Mode Screen which appears after running 15 minutes in Demo Mode

- Added CONTACT US section to Settings screen
  - Contains discord, web and email links

- In the Nymphes Ports spinners in the SETTINGS Screen, renamed the NOT CONNECTED options to NO INPUT PORT and NO OUTPUT PORT
  - I found the old NOT CONNECTED options confusing
- Added Nymphes Setup Instructions button in SETTINGS Screen

### Bug Fixes

- Fixed bug where Nymphes MIDI channel settings weren't being saved properly
  - After receiving /nymphes_midi_channel_changed OSC message from nymphes-osc, config.txt was being updated before self._nymphes_midi_channel got updated
  - Now it is done on the main thread, so it occurs after updating self._nymphes_midi_channel

- Fixed bug in nymphes-osc where MIDI Program Change messages above 97 caused the app to crash
  - Open-source users should pull in the latest nymphes-osc changes


## v0.3.6-beta

- Now the LOAD, SAVE AS, and SETTINGS buttons in the top bar toggle between their screens and the main screen
  - This means there's no longer a need for the SETTINGS button to turn into a BACK button
    - This means that you can now directly access the settings screen from all screens
    

## v0.3.5-beta

- Now you can now save to both files and preset slots
  - This includes Factory preset slots
- Now you can select and load both preset slots and files in the LOAD screen (formerly the OPEN file popup)
  - The OPEN button in the Top Bar has been changed to a LOAD button
- The top bar buttons have been rearranged
  - I think this new order is more intuitive
  - There is also a little bit of safety space between the preset + button and the revert button, to make it harder to accidentally press one when you intend to press the other
- All MAIN buttons have been changed to BACK buttons
  - This seems more intuitive to me, as it takes you back to the place you were previously (the main screen)
- In BlueAndPinkSynthEditor.spec: 
  - Fixed path for nymphes-osc import
    - Some people (including me with a fresh install of the code) would get an error complaining about an invalid hidden import when using pyinstaller to compile the app
- Moved app_version_string to the top of BlueAndPinkSynthEditorApp.py
  - It's easier to find now
- Fixed bug where top bar would show the .txt extension in the filename after saving a file, rather than hiding it as it should
- A bug has been fixed in nymphes-osc where the unsaved_changes flag was not reset after saving to a preset slot
  - Be sure to pull in the latest changes in nymphes-osc if you are not using a compiled installer


## v0.3.4-beta

- Improved status message when loading preset file that has been dropped onto the window


## v0.3.3-beta

- Fixed bug that broke preset and sysex file drag-and-drop functionality
- Fixed bug in nymphes-osc which made it load the last preset instead of the first after importing a SYSEX file


## v0.3.2-beta

- Fixed a mistake in the README instructions for where to move the app once compiled
  - In the distant past, we were creating a subfolder in the Applications folder (/Applications/Blue\ and\ Pink\ Synth\ Editor/)
  - However, when we switched to using no subfolder I failed to update the README
- Now using antialiased versions of RoundedRectangle and Rectangle
- Reorganized UI elements into separate py and kv files
  - Now it is much easier to navigate the project
- In the SETTINGS screen, now the OPEN PRESETS FOLDER and OPEN DEBUG LOGS FOLDER buttons are underlined
  - This makes them look like hyperlinks, which is more in line with how they actually work
- Implemented activation code functionality (disabled by default)
  - By default, the app does not require an activation code. However, if the function in activation_code_enabled.py is changed to return True then the app runs in demo mode unless a valid activation code has been loaded.
- Swapped the incoming and outgoing port numbers for communicating with nymphes-osc. I had accidentally mixed them up a while ago, and I've only now realized that the port sending messages to nymphes-osc match nymphes-osc's default listening port. It's not a huge issue, but was a little confusing to me.
- Changed presets spinner so it always has the same number of items
  - The first one always shows the name of the current preset
- Now the preset + and - buttons cycle through the preset slots but do not pass through the init preset.
- File load and save dialogs now sort the files alphabetically
- New Feature: Preset + and - buttons now cycle through preset files if one is currently loaded


## v0.3.1-beta

- A bug was fixed in nymphes-osc that was causing LFO2 type and key sync to not be set when loading a preset file or when using fine mode


## v0.3.0-beta

- A fix was made in nymphes-osc to compensate for the reversed order of the TRI and DUO modes in SYSEX dumps
  - Whenever a preset file was loaded, or whenever fine mode was enabled, or whenever adjusting chords settings, if the play mode was set to TRI or DUO, the opposite play mode would be activated
  - This was hard to figure out, but now things behave as they should


## v0.2.9-beta

- The default filename in the SAVE AS dialog is better now
- Fixed bug in ErrorDialog
- Added docs directory
  - Added pdf and html of the current work-in-progress version of the manual
  - Added Scrivener Files directory to contain the Scrivener document that the manual is generated from


## v0.2.8-beta

- The OPEN PRESETS FOLDER button on the SETTINGS page now opens the presets folder itself, rather than its parent folder
  - In order to achieve this it is necessary to have Finder select a file inside the folder
    - We have chosen the init.txt preset file because we know that it will exist
- The OPEN DEBUG LOGS FOLDER button now does the same thing: it selects the most recent log file (if one exists), so that the logs folder itself is shown rather than its parent folder
  - If there are no log files, then the parent is shown
- SETTINGS and BACK buttons no longer change the status area text
  - This is primarily to prevent the status area text from changing when Nymphes is not connected, but it also just wasn't necessary to provide tooltips for these buttons
- Fixed bug where the currently active Voice Mode button looked enabled when Nymphes was disconnected
- Chords Screen Improvements:
  - Added preset controls to the top bar in the CHORDS screen
    - It was annoying to not be able to scroll through presets in the CHORDS screen, especially when trying to explore factory presets to see how they used chords
  - Added a Left Bar to the CHORDS screen
    - This allows voice mode changes while in the CHORDS screen
    - While in the CHORDS screen, the CHORDS button becomes a BACK button
  - In the CHORDS screen, the far-right top bar button is now a SETTINGS button, just like on the MAIN screen
- The BACK button in the SETTINGS screen now takes you back to either the MAIN screen or CHORDS screen, whichever you were last in
- The SAVE button now is disabled when the init preset is loaded so you don't accidentally overwrite the init preset 
- Fixed bug where the LFO TYPE and SYNC controls weren't actually doing anything!


## v0.2.7-beta

- Removed mentions of Windows and Linux in README
  - Support for these other platforms is expected in the future, but for now it is difficult enough to handle macOS
  - Linux should be the easier of the two. It probably already works. I just don't have the time for testing right now
- Handling /midi_feedback_detected message now
  - Just logging it
- In nymphes-osc, added virtual MIDI ports for easy communication with DAWs
  - Make sure you pull in changes from nymphes-osc repository
- Fixed major bug in ValueControl that prevented float value dragging from working
  

## v0.2.6-beta

- Improved handling of window resizing and moving between displays with different dpi
  - Now sizing should stay consistent
  - Also, now resizing the window from a corner should be a lot smoother
  - MIDI Port Checkboxes in the settings page now look a bit better when the window has been moved from a higher dpi display to a lower one
    - They are about twice the size they should be, but at least you can see the entire checkbox now
- Fixed bug which would disable SETTINGS button if Nymphes was not connected
- Fixed bug which allowed mod amount lines to set status bar text on mouseover even if Nymphes was not connected
- Fixed bugs where certain OSC messages were still setting kivy property values on a background thread rather than scheduling the change on the main thread
  - I don't know that there will be a noticeable difference after changing this, but I do know that similar fixes done in the past improved app stability and responsiveness
- Fixed mistake: LFO1 parameter labels in Oscillator and Filter sections were supposed to be purple
- Expanded the use of colors
  - LFO2 parameter labels are now the same color as the LFO2 modulation amount lines
  - MOD WHEEL control's label now is the same color as MOD WHEEL modulation amount lines
  - VELOCITY label is now the same color as the VELOCITY modulation amount lines
  - AFTERTOUCH control's label is now the same color as the AFTERTOUCH modulation amount lines
  - Added an icon for the app


## v0.2.5-beta

- Fixed import bugs preventing app from compiling
- Forgot to mention in previous changelog that an INVERT MOUSE WHEEL control had been added to settings screen


## v0.2.4-beta

- Added automatic font size adjustment on presets spinner text, so that filenames longer than 20 characters can still be read.
- Improved UI on all mouse-controllable elements
  - Now when the mouse enters any control, the control grows slightly
  - Control element size is used to show that a click has happened
  - Now you can double-click a control and type a value
- Preset Save dialog now opens with the filename selected and focused so there's no need to click on it before you start typing
- Disabled kivy settings editor activated by pressing F1 key because it is not needed and is confusing
  - I didn't even know that it existed until I accidentally pressed F1 and the dialog appeared.
- Reorganization of code for much easier project navigation:
  - Moved most of the miscellaneous kivy subclasses into a new file: misc_widgets.py
  - Moved dialog classes to their own files
  - Moved SynthEditorValueControl-related classes to a new file: synth_editor_value_controls.py
  - Now BlueAndPinkSynthEditorApp.py contains just the app class.
- Added handling of the /poly_aftertouch OSC message that has just been added to nymphes-osc
  - We are simply displaying the value part of the message in the same place we show channel aftertouch
- Updated version in pyproject.toml
  - Had forgotten to do this for a while


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
