## Project Overview

- A desktop application for organizing family photos using AI/CV features. Runs locally on macOS and Windows.

## Key Components and Their Interactions

- **Core Module**: Contains the main logic for photo processing, analysis, and organization
- **GUI Module**: Handles the user interface components built with PySide6
- **Utils Module**: Contains helper functions and utilities used throughout the application
- **Main**: Entry point for the application

## Data Flow

- *(To be fully defined)*
- User uploads photos through the GUI
- Photos are processed by the core module for analysis and classification
- Results are displayed in the GUI for user review and modification

## External Dependencies

- **PySide6**: Qt-based GUI framework
- **Pillow**: Image processing library
- **imagehash**: Perceptual hashing for duplicate detection
- **OpenCV**: Computer vision library for image analysis
- **ExifRead**: Reading metadata from images

## Recent Significant Changes

- Project Initialization
- Basic project structure and module setup
- Implemented basic photo loading via GUI (File menu)
- Added core metadata extraction module (`exifread`)
- Implemented `Photo` dataclass for storing image data
- Displayed loaded photos in a GUI table (`QTableWidget`)
- Added core analysis module (`analysis.py`) with blur detection (Laplacian variance)
- Integrated analysis results into `Photo` object and GUI table
- Added perceptual hashing (`imagehash`) to `analysis.py`
- Implemented duplicate detection logic in `process_files` based on hash comparison
- Updated `Photo` class with duplicate tracking fields
- Added "Duplicate Info" column to GUI table

## User Feedback Integration and Its Impact on Development

- *(To be defined)*

## Additional Documentation

- *(None yet)* 