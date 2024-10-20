2024-10-04
- Fix activation code filedrop:
  - Option 1:
    - Unbind main window filedrop before showing demo mode popup
    - Re-bind main window filedrop when demo mode popup is dismissed
  - Option 2:
    - Don't bind the popup at all
      - Just add activation code handling to the main window's filedrop

- Drag activation file onto any window
  - A popup shows the result
    - Success popup
    - Failure popup
    - If the demo mode popup was open, then it closes first

- Create demo mode end popup?
  - Prevent it from being dismissed

- Determine why 