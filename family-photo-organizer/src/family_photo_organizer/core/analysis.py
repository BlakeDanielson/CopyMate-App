"""
Module for performing analysis on photos (quality, content, etc.).
"""

import cv2
import numpy as np
# Import imagehash and PIL
import imagehash
from PIL import Image
import os # For example usage

def calculate_phash(file_path):
    """
    Calculates the perceptual hash (pHash) of an image.
    Returns None if calculation fails.
    """
    try:
        img = Image.open(file_path)
        hash_val = imagehash.phash(img)
        return str(hash_val)
    except Exception as e:
        print(f"Warning: Error calculating pHash for {os.path.basename(file_path)}: {e}")
        return None

def analyze_photo(file_path):
    """
    Performs analysis on a photo: pHash calculation and blur detection.

    Args:
        file_path (str): The path to the image file.

    Returns:
        dict: A dictionary containing analysis results.
              Keys might include 'laplacian_variance', 'classification', 'phash'.
              Returns an empty dict if all analysis fails.
    """
    results = {}
    
    # --- pHash calculation --- 
    phash_value = calculate_phash(file_path)
    if phash_value:
        results['phash'] = phash_value
    
    # --- Blur Detection --- 
    try:
        # Using cv2.imread might struggle with some formats like HEIC or RAW initially.
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        
        if image is not None:
            # Calculate the Laplacian variance
            lap_var = cv2.Laplacian(image, cv2.CV_64F).var()
            results['laplacian_variance'] = lap_var

            # Basic Classification Rules (placeholder)
            BLUR_THRESHOLD = 100.0 
            if lap_var < BLUR_THRESHOLD:
                results['classification'] = 'blurry'
            else:
                results['classification'] = 'ok' 
        else:
             print(f"Warning: OpenCV could not read image for blur analysis: {os.path.basename(file_path)}")

    except Exception as e:
        print(f"Warning: Error during OpenCV analysis for {os.path.basename(file_path)}: {e}")
        # Don't discard phash if it exists
        results.pop('laplacian_variance', None)
        results.pop('classification', None)

    return results

# Example usage:
if __name__ == '__main__':
    # Replace with a real image path for testing
    # test_file = 'path/to/your/test/image.jpg'
    # if os.path.exists(test_file):
    #     analysis_results = analyze_photo(test_file)
    #     print(f"Analysis results for {test_file}:")
    #     print(analysis_results)
    # else:
    #     print(f"Test file not found: {test_file}")
    print("Analysis module ready.") 