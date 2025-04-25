import 'package:flutter/material.dart';

/// Form for uploading photos with description and tags
class PhotoUploadForm extends StatelessWidget {
  /// Text controller for description field
  final TextEditingController descriptionController;
  
  /// List of tags
  final List<String> tags;
  
  /// Callback for adding a tag
  final Function(String) onAddTag;
  
  /// Callback for removing a tag
  final Function(String) onRemoveTag;

  /// Creates a new PhotoUploadForm
  const PhotoUploadForm({
    super.key,
    required this.descriptionController,
    required this.tags,
    required this.onAddTag,
    required this.onRemoveTag,
  });

  @override
  Widget build(BuildContext context) {
    final tagController = TextEditingController();
    final theme = Theme.of(context);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Description field
        TextFormField(
          controller: descriptionController,
          decoration: const InputDecoration(
            labelText: 'Description (optional)',
            hintText: 'Add a description for your photo',
            border: OutlineInputBorder(),
          ),
          maxLines: 3,
        ),
        
        const SizedBox(height: 24),
        
        // Tags
        Text(
          'Tags',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        
        // Tags input field
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: tagController,
                decoration: const InputDecoration(
                  labelText: 'Add tags (optional)',
                  hintText: 'Enter a tag and press +',
                  border: OutlineInputBorder(),
                ),
                onFieldSubmitted: (value) {
                  if (value.isNotEmpty) {
                    onAddTag(value);
                    tagController.clear();
                  }
                },
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              icon: const Icon(Icons.add_circle),
              onPressed: () {
                if (tagController.text.isNotEmpty) {
                  onAddTag(tagController.text);
                  tagController.clear();
                }
              },
              tooltip: 'Add tag',
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Tags chips
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: tags.map((tag) {
            return Chip(
              label: Text(tag),
              deleteIcon: const Icon(Icons.close, size: 18),
              onDeleted: () => onRemoveTag(tag),
            );
          }).toList(),
        ),
      ],
    );
  }
}