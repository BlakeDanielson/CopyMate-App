"""
Module for extracting metadata from image files.
"""

import exifread
import os
from datetime import datetime


def extract_basic_metadata(file_path):
    """
    Extracts basic metadata (like capture date) from an image file.

    Args:
        file_path (str): The path to the image file.

    Returns:
        dict: A dictionary containing extracted metadata, or None if extraction fails.
              Keys might include 'capture_date'.
    """
    metadata = {}
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag='DateTimeOriginal')

            if 'EXIF DateTimeOriginal' in tags:
                date_str = str(tags['EXIF DateTimeOriginal'])
                # EXIF format: 'YYYY:MM:DD HH:MM:SS'
                try:
                    metadata['capture_date'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    print(f"Warning: Could not parse date '{date_str}' for {file_path}")
                    metadata['capture_date'] = None # Or handle differently
            else:
                metadata['capture_date'] = None

            # Add other relevant metadata extraction here (e.g., GPS, camera model)

    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return None
    except Exception as e:
        print(f"Error processing metadata for {file_path}: {e}")
        # Attempt to get file system modification time as a fallback
        try:
            mtime = os.path.getmtime(file_path)
            metadata['capture_date'] = datetime.fromtimestamp(mtime)
            print(f"Warning: Using file modification time as fallback for {file_path}")
        except Exception as fallback_e:
            print(f"Error getting modification time for {file_path}: {fallback_e}")
            metadata['capture_date'] = None
        # Keep other potential fields empty or None if primary extraction failed

    return metadata

# Example usage:
if __name__ == '__main__':
    # Create a dummy file path for testing (replace with a real image path)
    # test_file = 'path/to/your/test/image.jpg'
    # if os.path.exists(test_file):
    #     meta = extract_basic_metadata(test_file)
    #     print(f"Extracted metadata for {test_file}:")
    #     print(meta)
    # else:
    #     print(f"Test file not found: {test_file}")
    print("Metadata extractor module ready.") 