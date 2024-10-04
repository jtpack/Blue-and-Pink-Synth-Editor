2024-10-04
- Fix activation code filedrop:
  - Option 1:
    - Unbind main window filedrop before showing demo mode popup
    - Re-bind main window filedrop when demo mode popup is dismissed
  - Option 2:
    - Don't bind the popup at all
      - Just add activation code handling to the main window's filedrop
