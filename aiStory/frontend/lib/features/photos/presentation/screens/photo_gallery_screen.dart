import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/photo_notifier.dart';
import '../providers/photo_providers.dart';
import '../widgets/photo_grid_item.dart';
import 'photo_detail_screen.dart';
import 'photo_upload_screen.dart';

/// Screen for displaying a gallery of photos
class PhotoGalleryScreen extends ConsumerStatefulWidget {
  /// Route name for navigation
  static const routeName = '/photos';

  /// Creates a new PhotoGalleryScreen
  const PhotoGalleryScreen({super.key});

  @override
  ConsumerState<PhotoGalleryScreen> createState() => _PhotoGalleryScreenState();
}

class _PhotoGalleryScreenState extends ConsumerState<PhotoGalleryScreen> {
  bool _isLoading = false;
  final _scrollController = ScrollController();
  int _currentPage = 1;
  static const int _pageSize = 20;

  @override
  void initState() {
    super.initState();
    _loadPhotos();

    // Add scroll listener for pagination
    _scrollController.addListener(_scrollListener);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollListener() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200) {
      // Load more photos when reaching near the end of the list
      _loadMorePhotos();
    }
  }

  Future<void> _loadPhotos() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      await ref.read(photoNotifierProvider.notifier).loadPhotos(
        page: 1,
        pageSize: _pageSize,
      );
      
      // Reset current page
      _currentPage = 1;
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading photos: $e'),
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

  Future<void> _loadMorePhotos() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Load next page
      _currentPage++;
      
      await ref.read(photoNotifierProvider.notifier).loadPhotos(
        page: _currentPage,
        pageSize: _pageSize,
        refresh: false,
      );
    } catch (e) {
      // Revert page increment on error
      _currentPage--;
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading more photos: $e'),
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

  Future<void> _refreshPhotos() async {
    return _loadPhotos();
  }

  @override
  Widget build(BuildContext context) {
    final photoState = ref.watch(photoNotifierProvider);
    final photos = photoState.photos;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Photos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {
              // Show filter dialog (not implemented in this version)
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Filtering will be available in a future update'),
                ),
              );
            },
            tooltip: 'Filter photos',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshPhotos,
        child: photoState.isLoading && photos.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : photos.isEmpty
                ? _buildEmptyState()
                : _buildPhotoGrid(photos),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.pushNamed(
            context, 
            PhotoUploadScreen.routeName,
          ).then((_) => _refreshPhotos());
        },
        child: const Icon(Icons.add_a_photo),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.photo_library_outlined,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'No photos yet',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Upload your first photo to get started',
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pushNamed(
                context, 
                PhotoUploadScreen.routeName,
              ).then((_) => _refreshPhotos());
            },
            icon: const Icon(Icons.add_a_photo),
            label: const Text('Upload Photo'),
          ),
        ],
      ),
    );
  }

  Widget _buildPhotoGrid(List photos) {
    return GridView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(8.0),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.0,
        crossAxisSpacing: 8.0,
        mainAxisSpacing: 8.0,
      ),
      itemCount: photos.length + (_isLoading ? 1 : 0),
      itemBuilder: (context, index) {
        // Show loading indicator at the end while loading more
        if (index == photos.length) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(16.0),
              child: CircularProgressIndicator(),
            ),
          );
        }

        // Regular photo item
        final photo = photos[index];
        return PhotoGridItem(
          photo: photo,
          onTap: () {
            // Select photo and navigate to detail view
            ref.read(photoNotifierProvider.notifier).selectPhoto(photo.id);
            Navigator.pushNamed(
              context,
              PhotoDetailScreen.routeName,
              arguments: photo.id,
            );
          },
        );
      },
    );
  }
}