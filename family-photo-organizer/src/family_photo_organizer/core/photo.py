"""
Defines the Photo data structure.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import os

@dataclass
class Photo:
    """
    Represents a single photo and its associated data.
    """
    file_path: str
    filename: str = field(init=False)
    capture_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    classification: Optional[str] = None  # e.g., 'good', 'boring', 'exciting'
    classification_override: bool = False
    is_duplicate_of: Optional[str] = None # file_path of the primary photo in a group
    duplicate_group_id: Optional[str] = None
    duplicate_override: bool = False  # Indicates if duplicate status was manually set
    analysis_results: Dict[str, Any] = field(default_factory=dict) # For other metrics
    phash: Optional[str] = None

    def __post_init__(self):
        """Initialize filename after object creation."""
        self.filename = os.path.basename(self.file_path)

    def update_metadata(self, new_metadata: Dict[str, Any]):
        """Updates the photo's metadata, prioritizing capture date."""
        self.metadata.update(new_metadata)
        if 'capture_date' in new_metadata and isinstance(new_metadata['capture_date'], datetime):
            self.capture_date = new_metadata['capture_date']
        elif self.capture_date is None and 'capture_date' in self.metadata:
             # Handle cases where capture_date might be in metadata but not datetime initially
            if isinstance(self.metadata['capture_date'], datetime):
                self.capture_date = self.metadata['capture_date']

    def update_analysis(self, analysis_data: Dict[str, Any]):
        """Updates the photo's analysis results."""
        self.analysis_results.update(analysis_data)
        if 'classification' in analysis_data:
            self.classification = analysis_data['classification']
        if 'phash' in analysis_data:
            self.phash = analysis_data['phash']

# Example usage:
if __name__ == '__main__':
    # Assume metadata was extracted
    extracted_meta = {'capture_date': datetime(2023, 10, 26, 12, 30, 00)}
    
    # Create a Photo object
    photo1 = Photo(file_path="/path/to/image1.jpg")
    photo1.update_metadata(extracted_meta)
    
    print(f"Photo Filename: {photo1.filename}")
    print(f"Capture Date: {photo1.capture_date}")
    print(f"Metadata: {photo1.metadata}")
    
    # Example of setting classification
    photo1.classification = 'good'
    print(f"Classification: {photo1.classification}") 