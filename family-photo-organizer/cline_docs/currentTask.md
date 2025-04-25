## Current Objective

- Implement manual duplicate override in the GUI.

## Context

- Basic photo analysis (blur) is implemented.
- Duplicate detection using perceptual hashing is implemented.
- Manual classification override is implemented.
- Need ability for users to manage duplicate detection results.

## Completed Steps

- ~~Implement duplicate detection:~~ ✓
  - ~~Choose and implement hashing algorithm (pHash from `imagehash`).~~ ✓
  - ~~Add duplicate detection logic to the core module (`analysis.py` calculates hash).~~ ✓
  - ~~Update `Photo` class with duplicate information fields (`phash`, `is_duplicate_of`, `duplicate_group_id`).~~ ✓
  - ~~Updated `process_files` in GUI to compare hashes and mark duplicates.~~ ✓
  - ~~Update GUI to indicate duplicates (added "Duplicate Info" column).~~ ✓

- ~~Implement Manual Classification Override:~~ ✓
  - ~~Add mechanism in GUI (right-click context menu on table row) to change classification.~~ ✓
  - ~~Update `Photo` object to store the override.~~ ✓
  - ~~Visually indicate override in the table (added asterisk and distinct color).~~ ✓

- ~~Implement Manual Duplicate Override:~~ ✓
  - ~~Add functionality to allow users to manually mark/unmark photos as duplicates.~~ ✓
  - ~~Add "Mark as Duplicate" and "Remove from Duplicate Group" options to the context menu.~~ ✓
  - ~~Update the Photo object to track manual duplicate overrides.~~ ✓
  - ~~Visually indicate manual duplicate overrides in the table.~~ ✓

## Next Task

- Implement Photo Viewer:
  - Add ability to view selected photos in a larger display
  - Create a photo viewer dialog or panel
  - Add thumbnail generation for better performance
  - Add basic zoom/pan controls
  - Add navigation between photos (next/previous) 