#!/bin/zsh

# Create the screenshots directory if it doesn't exist
mkdir -p ~/Desktop/screenshots

# Capture the selected area and save it with a timestamp
screencapture -s ~/Desktop/screenshots/selection_screenshot_$(date +"%Y-%m-%d_%H-%M-%S").png