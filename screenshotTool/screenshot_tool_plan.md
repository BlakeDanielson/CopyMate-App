# MacOS Screenshot Tool Implementation Plan

## Objective
Replace the default macOS screenshot keyboard shortcuts (Cmd+Shift+3 and Cmd+Shift+4) with custom scripts (`screenshot_fullscreen.sh` and `screenshot_selection.sh`), modifying the scripts to save screenshots to `~/Desktop/screenshots` in PNG format.

## Plan Details

### 1. Modify Scripts

* **Update `screenshot_fullscreen.sh`:**
  * Save the fullscreen screenshot to a timestamped file in `~/Desktop/screenshots`
  * Add logic to create the `~/Desktop/screenshots` directory if it doesn't exist

* **Update `screenshot_selection.sh`:**
  * Save the selected area screenshot to a timestamped file in `~/Desktop/screenshots`
  * Add logic to create the `~/Desktop/screenshots` directory if it doesn't exist

### 2. Identify and Disable Default Shortcuts

* Determine the specific keys in `com.apple.symbolichotkeys` that control the Cmd+Shift+3 and Cmd+Shift+4 shortcuts
* Use the `defaults write` command to disable these default hotkeys

### 3. Create and Assign New Shortcuts

* Use the `defaults write` command to create new symbolic hotkeys
* Configure these new hotkeys to execute the modified `screenshot_fullscreen.sh` and `screenshot_selection.sh` scripts when Cmd+Shift+3 and Cmd+Shift+4 are pressed

### 4. Apply Changes

* Restart the `cfprefsd` process using `killall cfprefsd` to ensure the system applies the changes made to the `com.apple.symbolichotkeys` domain

## Implementation Flow

```mermaid
graph TD
    A[User Request] --> B{Modify Scripts};
    B --> C[Update screenshot_fullscreen.sh];
    B --> D[Update screenshot_selection.sh];
    C --> E[Add Directory Creation];
    D --> E[Add Directory Creation];
    E --> F{Configure System Shortcuts};
    F --> G[Identify Default Hotkeys];
    G --> H[Disable Default Hotkeys];
    H --> I[Create New Hotkeys];
    I --> J[Assign Scripts to New Hotkeys];
    J --> K[Restart cfprefsd];
    K --> L[Task Complete];