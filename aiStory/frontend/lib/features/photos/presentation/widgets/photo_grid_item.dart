import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models/photo.dart';
import '../providers/photo_notifier.dart';

/// Widget for displaying a photo in a grid
class PhotoGridItem extends ConsumerWidget {
  /// Photo to display
  final Photo photo;
  
  /// Callback when photo is tapped
  final VoidCallback onTap;

  /// Creates a new PhotoGridItem
  const PhotoGridItem({
    super.key,
    required this.photo,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return GestureDetector(
      onTap: onTap,
      child: Card(
        clipBehavior: Clip.antiAlias,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Photo content
            Expanded(
              child: _buildImageWithLoader(context, ref),
            ),
            
            // Status indicator
            _buildStatusIndicator(context),
          ],
        ),
      ),
    );
  }

  Widget _buildImageWithLoader(BuildContext context, WidgetRef ref) {
    return FutureBuilder<String?>(
      future: ref.read(photoNotifierProvider.notifier).getPhotoUrl(photo.id),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (snapshot.hasError || !snapshot.hasData || snapshot.data == null) {
          return const Center(
            child: Icon(
              Icons.broken_image_outlined,
              size: 48,
              color: Colors.grey,
            ),
          );
        }
        
        final imageUrl = snapshot.data!;
        
        return Hero(
          tag: 'photo_${photo.id}',
          child: CachedNetworkImage(
            imageUrl: imageUrl,
            fit: BoxFit.cover,
            placeholder: (context, url) => Container(
              color: Colors.grey[200],
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
            errorWidget: (context, url, error) => Container(
              color: Colors.grey[300],
              child: const Center(
                child: Icon(
                  Icons.error_outline,
                  color: Colors.red,
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatusIndicator(BuildContext context) {
    Color backgroundColor;
    IconData iconData;
    String statusText;
    
    switch (photo.status) {
      case PhotoStatus.pending:
        backgroundColor = Colors.orange.shade100;
        iconData = Icons.hourglass_empty;
        statusText = 'Pending';
        break;
      case PhotoStatus.uploaded:
        backgroundColor = Colors.blue.shade100;
        iconData = Icons.cloud_done;
        statusText = 'Uploaded';
        break;
      case PhotoStatus.processing:
        backgroundColor = Colors.purple.shade100;
        iconData = Icons.settings;
        statusText = 'Processing';
        break;
      case PhotoStatus.completed:
        backgroundColor = Colors.green.shade100;
        iconData = Icons.check_circle;
        statusText = 'Completed';
        break;
      case PhotoStatus.failed:
        backgroundColor = Colors.red.shade100;
        iconData = Icons.error;
        statusText = 'Failed';
        break;
      default:
        backgroundColor = Colors.grey.shade100;
        iconData = Icons.help;
        statusText = 'Unknown';
    }
    
    return Container(
      color: backgroundColor,
      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            iconData,
            size: 14,
            color: backgroundColor.withAlpha(200),
          ),
          const SizedBox(width: 4),
          Text(
            statusText,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: backgroundColor.withAlpha(200),
            ),
          ),
        ],
      ),
    );
  }
}