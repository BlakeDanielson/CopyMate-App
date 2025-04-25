# Family Photo Organizer

A local desktop application to help organize family photos using AI analysis for quality and duplicates. Designed for simplicity and ease of use.

## Features (Planned)

*   Upload photos (RAW, JPEG, PNG, HEIC)
*   Extract metadata (Date, Location)
*   AI-based classification (Good, Exciting, Boring)
*   Duplicate detection (including burst photos)
*   Manual override for classifications and duplicates
*   Native GUI for macOS and Windows
*   Automated backup to a single archive file
*   First-launch tutorial

## Project Structure

```
family-photo-organizer/
├── src/
│   ├── family_photo_organizer/    # Main package
│   │   ├── core/                  # Core functionality
│   │   ├── gui/                   # User interface
│   │   └── utils/                 # Helper utilities
│   └── main.py                    # Entry point
├── tests/                         # Unit and integration tests
├── docs/                          # Documentation
├── assets/                        # Images and resources
└── cline_docs/                    # Project management docs
```

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/BlakeDanielson/family-photo-organizer.git
   cd family-photo-organizer
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Development

1. Install in development mode:
   ```
   pip install -e .
   ```

2. Run the application:
   ```
   python src/main.py
   ```

3. Run tests:
   ```
   pytest
   ``` 