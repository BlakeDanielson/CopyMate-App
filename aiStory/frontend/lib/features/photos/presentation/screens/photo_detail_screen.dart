import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../domain/models/photo.dart';
import '../../domain/models/photo_status.dart';
import '../providers/photo_notifier.dart';

/// Screen for displaying a photo in detail
class PhotoDetailScreen extends ConsumerStatefulWidget {
  /// Route name for navigation
  static const routeName = '/photos/detail';

  /// ID of the photo to display
  final String photoId;

  /// Creates a new PhotoDetailScreen
  const PhotoDetailScreen({
    super.key,
    required this.photoId,
  });

  @override
  ConsumerState<PhotoDetailScreen> createState() => _PhotoDetailScreenState();
}

class _PhotoDetailScreenState extends ConsumerState<PhotoDetailScreen> {
  bool _isLoading = false;
  bool _isProcessing = false;
  bool _showDeleteDialog = false;

  @override
  void initState() {
    super.initState();
    _loadPhoto();
  }

  Future<void> _loadPhoto() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      await ref.read(photoNotifierProvider.notifier).loadPhoto(widget.photoId);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading photo: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _processPhoto() async {
    if (_isProcessing) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      final success = await ref.read(photoNotifierProvider.notifier)
          .processPhoto(widget.photoId);

      if (mounted && success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Photo processed successfully'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error processing photo: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
    }
  }

  Future<void> _deletePhoto() async {
    setState(() {
      _showDeleteDialog = false;
    });

    try {
      final success = await ref.read(photoNotifierProvider.notifier)
          .deletePhoto(widget.photoId);

      if (mounted && success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Photo deleted'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Navigate back to gallery
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error deleting photo: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showConfirmDelete() {
    setState(() {
      _showDeleteDialog = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    final photoState = ref.watch(photoNotifierProvider);
    final photo = photoState.selectedPhoto;
    
    // If no photo is selected, show loading state
    if (photo == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Photo Details'),
        ),
        body: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Photo Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: _showConfirmDelete,
            tooltip: 'Delete photo',
          ),
        ],
      ),
      body: Stack(
        children: [
          // Main content
          SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Photo
                Hero(
                  tag: 'photo_${photo.id}',
                  child: _buildPhotoView(photo),
                ),
                
                // Details
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // File details
                      _buildDetailCard(
                        title: 'File Information',
                        icon: Icons.description,
                        details: [
                          DetailItem(
                            'Filename',
                            photo.originalFilename,
                          ),
                          DetailItem(
                            'Type',
                            photo.contentType,
                          ),
                          DetailItem(
                            'Upload Date',
                            DateFormat.yMMMd().add_jm().format(photo.createdAt),
                          ),
                          DetailItem(
                            'Status',
                            _getStatusString(photo.status),
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // Storage details
                      _buildDetailCard(
                        title: 'Storage Information',
                        icon: Icons.cloud,
                        details: [
                          DetailItem(
                            'Provider',
                            photo.storageProvider,
                          ),
                          DetailItem(
                            'Bucket',
                            photo.bucketName,
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // Process button - Only show if photo is not completed or failed
                      if (photo.status != PhotoStatus.completed && 
                          photo.status != PhotoStatus.failed) ...[
                        ElevatedButton.icon(
                          onPressed: _isProcessing ? null : _processPhoto,
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            minimumSize: const Size(double.infinity, 50),
                          ),
                          icon: const Icon(Icons.auto_fix_high),
                          label: Text(
                            _isProcessing ? 'Processing...' : 'Process Photo',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Delete confirmation dialog
          if (_showDeleteDialog)
            _buildDeleteConfirmation(),
            
          // Loading overlay
          if (_isLoading)
            Container(
              color: Colors.black.withOpacity(0.5),
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildPhotoView(Photo photo) {
    return FutureBuilder<String?>(
      future: ref.read(photoNotifierProvider.notifier).getPhotoUrl(photo.id),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Container(
            height: 300,
            color: Colors.grey[200],
            child: const Center(child: CircularProgressIndicator()),
          );
        }
        
        if (snapshot.hasError || !snapshot.hasData || snapshot.data == null) {
          return Container(
            height: 300,
            color: Colors.grey[300],
            child: const Center(
              child: Icon(
                Icons.broken_image_outlined,
                size: 64,
                color: Colors.grey,
              ),
            ),
          );
        }
        
        final imageUrl = snapshot.data!;
        
        return CachedNetworkImage(
          imageUrl: imageUrl,
          height: 300,
          fit: BoxFit.cover,
          placeholder: (context, url) => Container(
            color: Colors.grey[200],
            child: const Center(child: CircularProgressIndicator()),
          ),
          errorWidget: (context, url, error) => Container(
            color: Colors.grey[300],
            child: const Center(
              child: Icon(
                Icons.error_outline,
                color: Colors.red,
                size: 64,
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildDetailCard({
    required String title,
    required IconData icon,
    required List<DetailItem> details,
  }) {
    final theme = Theme.of(context);
    
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: theme.primaryColor),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const Divider(),
            const SizedBox(height: 8),
            ...details.map((detail) => Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(
                    width: 100,
                    child: Text(
                      '${detail.label}:',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.grey,
                      ),
                    ),
                  ),
                  Expanded(
                    child: Text(
                      detail.value,
                      style: const TextStyle(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            )).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildDeleteConfirmation() {
    return Container(
      color: Colors.black54,
      alignment: Alignment.center,
      child: Card(
        margin: const EdgeInsets.all(32),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.warning_amber_rounded,
                color: Colors.orange,
                size: 48,
              ),
              const SizedBox(height: 16),
              const Text(
                'Delete Photo?',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'This action cannot be undone. The photo will be permanently deleted from the server.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _showDeleteDialog = false;
                      });
                    },
                    child: const Text('Cancel'),
                  ),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                    ),
                    onPressed: _deletePhoto,
                    child: const Text('Delete'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getStatusString(PhotoStatus status) {
    switch (status) {
      case PhotoStatus.pending:
        return 'Pending';
      case PhotoStatus.uploaded:
        return 'Uploaded';
      case PhotoStatus.processing:
        return 'Processing';
      case PhotoStatus.completed:
        return 'Completed';
      case PhotoStatus.failed:
        return 'Failed';
      default:
        return 'Unknown';
    }
  }
}

/// Helper class for detail items
class DetailItem {
  /// Label for the detail
  final String label;
  
  /// Value of the detail
  final String value;

  /// Creates a new DetailItem
  const DetailItem(this.label, this.value);
}