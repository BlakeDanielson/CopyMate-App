import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as path;

import '../../../../core/utils/logger.dart';
import '../providers/photo_notifier.dart';
import '../providers/photo_providers.dart';
import '../widgets/photo_upload_form.dart';

/// Screen for uploading photos
class PhotoUploadScreen extends ConsumerStatefulWidget {
  /// Route name for navigation
  static const routeName = '/photos/upload';

  /// Creates a new PhotoUploadScreen
  const PhotoUploadScreen({super.key});

  @override
  ConsumerState<PhotoUploadScreen> createState() => _PhotoUploadScreenState();
}

class _PhotoUploadScreenState extends ConsumerState<PhotoUploadScreen> {
  File? _selectedImage;
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final List<String> _tags = [];
  bool _isSubmitting = false;

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picker = ImagePicker();
      final pickedImage = await picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 80,
      );

      if (pickedImage == null) {
        return;
      }

      setState(() {
        _selectedImage = File(pickedImage.path);
      });
    } catch (e) {
      logger.e('Error picking image: $e');
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed to pick image. Please try again.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _submitForm() async {
    if (_selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select an image first'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final photoId = await ref.read(photoNotifierProvider.notifier).uploadPhoto(
            photoFile: _selectedImage!,
            description: _descriptionController.text.trim(),
            tags: _tags.isNotEmpty ? _tags : null,
          );

      if (context.mounted) {
        if (photoId != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Photo uploaded successfully!'),
              backgroundColor: Colors.green,
            ),
          );
          
          // Clear form
          setState(() {
            _selectedImage = null;
            _descriptionController.clear();
            _tags.clear();
          });
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to upload photo'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      logger.e('Error uploading photo: $e');
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  void _addTag(String tag) {
    if (tag.isEmpty) return;
    
    final trimmedTag = tag.trim();
    if (trimmedTag.isNotEmpty && !_tags.contains(trimmedTag)) {
      setState(() {
        _tags.add(trimmedTag);
      });
    }
  }

  void _removeTag(String tag) {
    setState(() {
      _tags.remove(tag);
    });
  }

  @override
  Widget build(BuildContext context) {
    final photoState = ref.watch(photoNotifierProvider);
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Upload Photo'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Image Preview or Image Selection Buttons
                if (_selectedImage == null) ...[
                  Card(
                    elevation: 4,
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          const Text(
                            'Select a photo to upload',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              ElevatedButton.icon(
                                onPressed: () => _pickImage(ImageSource.camera),
                                icon: const Icon(Icons.camera_alt),
                                label: const Text('Camera'),
                              ),
                              ElevatedButton.icon(
                                onPressed: () => _pickImage(ImageSource.gallery),
                                icon: const Icon(Icons.photo_library),
                                label: const Text('Gallery'),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ] else ...[
                  Card(
                    elevation: 4,
                    clipBehavior: Clip.antiAlias,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        AspectRatio(
                          aspectRatio: 16 / 9,
                          child: Image.file(
                            _selectedImage!,
                            fit: BoxFit.cover,
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                path.basename(_selectedImage!.path),
                                style: theme.textTheme.bodyMedium,
                                overflow: TextOverflow.ellipsis,
                              ),
                              IconButton(
                                icon: const Icon(Icons.refresh),
                                onPressed: () => setState(() {
                                  _selectedImage = null;
                                }),
                                tooltip: 'Choose different image',
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 24),
                
                // Photo Upload Form
                PhotoUploadForm(
                  descriptionController: _descriptionController,
                  tags: _tags,
                  onAddTag: _addTag,
                  onRemoveTag: _removeTag,
                ),
                
                const SizedBox(height: 24),
                
                // Upload Button
                if (photoState.isUploading) ...[
                  Column(
                    children: [
                      LinearProgressIndicator(
                        value: photoState.uploadProgress,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Uploading: ${(photoState.uploadProgress * 100).toInt()}%',
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ] else ...[
                  ElevatedButton.icon(
                    onPressed: _isSubmitting ? null : _submitForm,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    icon: const Icon(Icons.cloud_upload),
                    label: const Text(
                      'UPLOAD PHOTO',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
                
                // Error Message
                if (photoState.errorMessage != null) ...[
                  const SizedBox(height: 16),
                  Card(
                    color: Colors.red.shade100,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        children: [
                          Icon(Icons.error, color: Colors.red.shade800),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              photoState.errorMessage!,
                              style: TextStyle(color: Colors.red.shade800),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close),
                            onPressed: () {
                              ref.read(photoNotifierProvider.notifier).clearError();
                            },
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}