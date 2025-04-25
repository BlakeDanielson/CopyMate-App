"""
Main window for the Family Photo Organizer application.
"""

import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressDialog,
    QMenu,
)
from PySide6.QtGui import QAction, QColor
from PySide6.QtCore import Qt # For date formatting

# Import the metadata extractor
from family_photo_organizer.core.metadata_extractor import extract_basic_metadata
# Import the Photo class
from family_photo_organizer.core.photo import Photo
# Import the analysis function
from family_photo_organizer.core.analysis import analyze_photo
# Import imagehash for comparison
import imagehash
import os # Needed for folder scanning
from datetime import datetime


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Family Photo Organizer")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        self._create_menus()
        self._create_central_widget()

        self.photos = [] # List to store Photo objects
        
        # Classification options
        self.classification_options = ["good", "exciting", "boring", "blurry"]

    def _create_menus(self):
        """Create the menu bar."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open Files...", self)
        open_action.triggered.connect(self.open_files)
        file_menu.addAction(open_action)

        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_central_widget(self):
        """Create the central widget placeholder."""
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create the table widget
        self.photo_table = QTableWidget()
        self.photo_table.setColumnCount(4) # Add column for Duplicates
        self.photo_table.setHorizontalHeaderLabels(["Filename", "Capture Date", "Classification", "Duplicate Info"])
        self.photo_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Filename stretches
        self.photo_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Date resizes
        self.photo_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Classification resizes
        self.photo_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Duplicates resizes
        self.photo_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Make read-only
        self.photo_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Setup context menu for the table
        self.photo_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.photo_table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.photo_table)

        # Status label at the bottom
        self.status_label = QLabel("Welcome! Select File > Open to load photos.")
        layout.addWidget(self.status_label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_files(self):
        """Open a file dialog to select multiple image files."""
        # TODO: Add more specific file filters based on supported types
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.heic *.raw)") # Add more as needed
        file_dialog.setViewMode(QFileDialog.ViewMode.List)

        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            if filenames:
                print(f"Selected files: {filenames}")
                self.status_label.setText(f"Processing {len(filenames)} file(s)...")
                # Pass filenames to the core processing module
                self.process_files(filenames)
                self.status_label.setText(f"Finished processing {len(filenames)} file(s).")

    def open_folder(self):
        """Open a file dialog to select a folder."""
        folder_dialog = QFileDialog(self)
        folder_path = folder_dialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            print(f"Selected folder: {folder_path}")
            self.status_label.setText(f"Scanning folder: {folder_path}...")
            # Process all supported files in the folder
            supported_extensions = (".png", ".jpg", ".jpeg", ".heic", ".raw") # Case-insensitive
            files_to_process = []
            for item in os.listdir(folder_path):
                if item.lower().endswith(supported_extensions):
                    files_to_process.append(os.path.join(folder_path, item))
            
            if files_to_process:
                print(f"Found {len(files_to_process)} supported files in folder.")
                self.process_files(files_to_process)
                self.status_label.setText(f"Finished processing {len(files_to_process)} file(s) from folder.")
            else:
                self.status_label.setText(f"No supported image files found in folder: {folder_path}")

    def process_files(self, file_paths):
        """
        Processes a list of image files, extracting metadata.

        Args:
            file_paths (list): A list of absolute paths to image files.
        """
        HASH_THRESHOLD = 5 # Perceptual hash difference threshold

        new_photos_processed = 0
        existing_files = {photo.file_path for photo in self.photos}
        
        # Progress dialog for potentially long operations
        progress = QProgressDialog("Processing photos...", "Cancel", 0, len(file_paths), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(True)
        progress.setMinimumDuration(1000) # Only show if takes > 1 second

        for i, file_path in enumerate(file_paths):
            progress.setValue(i)
            if progress.wasCanceled():
                break

            if file_path in existing_files:
                print(f"Skipping already loaded file: {os.path.basename(file_path)}")
                continue
                
            print(f"--- Processing: {os.path.basename(file_path)} ---")
            metadata = extract_basic_metadata(file_path)
            if metadata:
                print(f"  Capture Date: {metadata.get('capture_date')}")

                # Create Photo object and add to list
                photo = Photo(file_path=file_path)
                photo.update_metadata(metadata)

                # Perform analysis
                print(f"  Analyzing quality...")
                analysis_data = analyze_photo(file_path)
                if analysis_data:
                    photo.update_analysis(analysis_data)
                    print(f"  Analysis complete. Classification: {photo.classification}, pHash: {photo.phash}, Variance: {analysis_data.get('laplacian_variance', 'N/A'):.2f}")

                    # --- Duplicate Check --- 
                    if photo.phash:
                        new_hash = imagehash.hex_to_hash(photo.phash)
                        is_duplicate = False
                        for existing_photo in self.photos:
                            if existing_photo.phash and existing_photo.file_path != photo.file_path:
                                try:
                                    existing_hash = imagehash.hex_to_hash(existing_photo.phash)
                                    hash_diff = new_hash - existing_hash
                                    if hash_diff <= HASH_THRESHOLD:
                                        # Mark as duplicate
                                        # Simple strategy: group by the first photo encountered in the group
                                        if existing_photo.duplicate_group_id:
                                            photo.duplicate_group_id = existing_photo.duplicate_group_id
                                            photo.is_duplicate_of = existing_photo.duplicate_group_id # Point to group leader
                                        else:
                                            # This existing photo is the first of its group
                                            group_id = existing_photo.file_path # Use leader's path as ID
                                            existing_photo.duplicate_group_id = group_id
                                            photo.duplicate_group_id = group_id
                                            photo.is_duplicate_of = group_id

                                        print(f"  Potential duplicate found! (Diff: {hash_diff}) Group: {os.path.basename(photo.duplicate_group_id)}")
                                        is_duplicate = True
                                        break # Found a match, stop checking for this photo
                                except ValueError:
                                    print(f"Warning: Could not compare invalid hash for {existing_photo.filename}")
                        # If not a duplicate of any existing photo, it could be a group leader
                        # if not is_duplicate:
                        #    photo.duplicate_group_id = photo.file_path # It leads its own group (of 1 initially)
                            
                else:
                    print("  Analysis failed.")

                self.photos.append(photo)
                new_photos_processed += 1
            else:
                print("  Could not extract metadata.")
            print("-------------------------------")
        
        # TODO: Store or display the extracted metadata
        # TODO: Update GUI to show the photos
        self.update_photo_table()

        print(f"\nProcessed {new_photos_processed} new files. Total photos loaded: {len(self.photos)}.")

    def show_context_menu(self, position):
        """
        Show a context menu for the selected table item.
        """
        # Get the current row
        row = self.photo_table.rowAt(position.y())
        if row < 0:
            return  # No valid row selected
        
        # Get the photo object from the sorted list
        sorted_photos = sorted(
            self.photos,
            key=lambda p: p.capture_date if p.capture_date else datetime.min,
            reverse=True
        )
        
        if row >= len(sorted_photos):
            return  # Invalid row
            
        selected_photo = sorted_photos[row]
        
        # Create context menu
        context_menu = QMenu(self)
        
        # Create a submenu for classification options
        classification_menu = QMenu("Change Classification", self)
        
        # Add classification options
        for classification in self.classification_options:
            action = QAction(classification, self)
            action.triggered.connect(lambda checked=False, c=classification: self.change_classification(row, c))
            classification_menu.addAction(action)
        
        # Add the classification submenu to the context menu
        context_menu.addMenu(classification_menu)
        
        # Add separator
        context_menu.addSeparator()
        
        # Add duplicate management options
        if selected_photo.duplicate_group_id is None or selected_photo.is_duplicate_of is None:
            # Photo is not currently marked as duplicate
            mark_duplicate_menu = QMenu("Mark as Duplicate of...", self)
            
            # Find potential duplicates based on similar filename (just as an example)
            potential_matches = []
            for photo in self.photos:
                if photo.file_path != selected_photo.file_path:
                    potential_matches.append(photo)
            
            if potential_matches:
                for photo in sorted(potential_matches, key=lambda p: p.filename):
                    action = QAction(photo.filename, self)
                    action.triggered.connect(lambda checked=False, p=photo: self.mark_as_duplicate(row, p.file_path))
                    mark_duplicate_menu.addAction(action)
            else:
                action = QAction("No other photos available", self)
                action.setEnabled(False)
                mark_duplicate_menu.addAction(action)
                
            context_menu.addMenu(mark_duplicate_menu)
        else:
            # Photo is already marked as duplicate, offer to remove from group
            remove_duplicate_action = QAction("Remove from Duplicate Group", self)
            remove_duplicate_action.triggered.connect(lambda: self.remove_from_duplicate_group(row))
            context_menu.addAction(remove_duplicate_action)
        
        # Show the menu at the position
        context_menu.exec(self.photo_table.mapToGlobal(position))
    
    def change_classification(self, row, new_classification):
        """
        Change the classification of a photo and mark it as manually overridden.
        
        Args:
            row (int): The row index in the table.
            new_classification (str): The new classification value.
        """
        # Get the photo object from the sorted list
        sorted_photos = sorted(
            self.photos,
            key=lambda p: p.capture_date if p.capture_date else datetime.min,
            reverse=True
        )
        
        if 0 <= row < len(sorted_photos):
            photo = sorted_photos[row]
            # Update the photo object
            photo.classification = new_classification
            photo.classification_override = True
            
            # Update the table UI
            self.update_photo_table()
            
            print(f"Manual classification override: {photo.filename} set to '{new_classification}'")

    def mark_as_duplicate(self, row, primary_photo_path):
        """
        Manually mark a photo as duplicate of another photo.
        
        Args:
            row (int): The row index in the table of the photo to mark.
            primary_photo_path (str): The file path of the primary photo.
        """
        # Get the photo object from the sorted list
        sorted_photos = sorted(
            self.photos,
            key=lambda p: p.capture_date if p.capture_date else datetime.min,
            reverse=True
        )
        
        if 0 <= row < len(sorted_photos):
            photo = sorted_photos[row]
            primary_photo = next((p for p in self.photos if p.file_path == primary_photo_path), None)
            
            if primary_photo:
                # If primary doesn't have a group yet, create one
                if not primary_photo.duplicate_group_id:
                    primary_photo.duplicate_group_id = primary_photo.file_path
                
                # Mark as duplicate
                photo.is_duplicate_of = primary_photo.duplicate_group_id
                photo.duplicate_group_id = primary_photo.duplicate_group_id
                photo.duplicate_override = True
                
                # Update the table UI
                self.update_photo_table()
                
                print(f"Manual duplicate override: {photo.filename} marked as duplicate of {os.path.basename(primary_photo_path)}")
    
    def remove_from_duplicate_group(self, row):
        """
        Manually remove a photo from its duplicate group.
        
        Args:
            row (int): The row index in the table.
        """
        # Get the photo object from the sorted list
        sorted_photos = sorted(
            self.photos,
            key=lambda p: p.capture_date if p.capture_date else datetime.min,
            reverse=True
        )
        
        if 0 <= row < len(sorted_photos):
            photo = sorted_photos[row]
            
            # Remove from group
            old_group = photo.duplicate_group_id
            photo.is_duplicate_of = None
            photo.duplicate_group_id = None
            photo.duplicate_override = True
            
            # Update the table UI
            self.update_photo_table()
            
            print(f"Manual duplicate override: {photo.filename} removed from duplicate group {os.path.basename(old_group) if old_group else 'unknown'}")
            
    def update_photo_table(self):
        """Updates the QTableWidget with the current list of photos."""
        self.photo_table.setRowCount(len(self.photos))
        
        # Sort photos by capture date (most recent first), handle None dates
        sorted_photos = sorted(
            self.photos,
            key=lambda p: p.capture_date if p.capture_date else datetime.min,
            reverse=True
        )

        # Define colors for classification and override visual feedback
        classification_colors = {
            'blurry': QColor(255, 200, 200),  # Light red
            'good': QColor(200, 255, 200),    # Light green
            'exciting': QColor(200, 200, 255), # Light blue
            'boring': QColor(255, 255, 200)    # Light yellow
        }
        
        override_color = QColor(255, 220, 180)  # Light orange for overrides

        for row, photo in enumerate(sorted_photos):
            filename_item = QTableWidgetItem(photo.filename)
            
            date_str = "N/A"
            if photo.capture_date:
                try:
                    # Format date nicely, check Qt documentation for specific formats
                    date_str = photo.capture_date.strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    date_str = str(photo.capture_date) # Fallback

            date_item = QTableWidgetItem(date_str)

            # Add an asterisk to indicate manual override
            classification_str = photo.classification if photo.classification else "N/A"
            if photo.classification_override:
                classification_str = f"{classification_str}*"
            classification_item = QTableWidgetItem(classification_str)

            duplicate_info_str = ""
            if photo.is_duplicate_of:
                 # Show just the filename of the photo it's a duplicate of
                 duplicate_info_str = f"Dup of: {os.path.basename(photo.is_duplicate_of)}"
                 # Add an asterisk if manually overridden
                 if photo.duplicate_override:
                     duplicate_info_str = f"{duplicate_info_str}*"
            elif photo.duplicate_group_id and photo.file_path == photo.duplicate_group_id:
                 # Indicate it's the leader of a potential group
                 # Count members in the group
                 group_members = sum(1 for p in self.photos if p.duplicate_group_id == photo.duplicate_group_id)
                 if group_members > 1:
                     duplicate_info_str = f"Group Leader ({group_members})"
                     # Add an asterisk if the group has any manually overridden members
                     has_overrides = any(p.duplicate_override for p in self.photos 
                                       if p.duplicate_group_id == photo.duplicate_group_id)
                     if has_overrides:
                         duplicate_info_str = f"{duplicate_info_str}*"
                 # else: show nothing if it's a group of 1

            duplicate_item = QTableWidgetItem(duplicate_info_str)

            # Set background color based on classification
            if photo.classification in classification_colors:
                # If override, use the override color instead
                if photo.classification_override:
                    classification_item.setBackground(override_color)
                else:
                    classification_item.setBackground(classification_colors[photo.classification])
            
            # If duplicate is overridden, highlight the duplicate info cell
            if photo.duplicate_override:
                duplicate_item.setBackground(override_color)

            self.photo_table.setItem(row, 0, filename_item)
            self.photo_table.setItem(row, 1, date_item)
            self.photo_table.setItem(row, 2, classification_item)
            self.photo_table.setItem(row, 3, duplicate_item)


# Example usage for testing the window directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 