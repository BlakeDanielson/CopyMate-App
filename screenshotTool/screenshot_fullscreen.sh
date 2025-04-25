#!/bin/zsh

# Create the screenshots directory if it doesn't exist
mkdir -p ~/Desktop/screenshots

# Capture the fullscreen and save it with a timestamp
screencapture ~/Desktop/screenshots/fullscreen_screenshot_$(date +"%Y-%m-%d_%H-%M-%S").png