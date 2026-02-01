import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../api/photo_service.dart';
import '../api/api_client.dart';
import '../models/photo.dart';

class PhotoProvider extends ChangeNotifier {
  final PhotoService _photoService;
  List<Photo> _photos = [];
  bool _isLoading = false;
  String? _error;
  int? _currentEventId;

  PhotoProvider() : _photoService = PhotoService(ApiClient());

  List<Photo> get photos => _photos;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadPhotos(int? eventId, {String? tags}) async {
    _currentEventId = eventId;
    _isLoading = true;
    _error = null;
    _photos = []; // Clear previous photos
    notifyListeners();
    try {
      _photos = await _photoService.searchPhotos(eventId: eventId, tags: tags);
      debugPrint('PhotoProvider: Successfully loaded ${_photos.length} photos.');
    } catch (e) {
      debugPrint('PhotoProvider: Error loading photos: $e');
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> toggleLike(int photoId) async {
    try {
      final index = _photos.indexWhere((p) => p.id == photoId);
      if (index != -1) {
        final result = await _photoService.toggleLike(photoId);
        _photos[index] = _photos[index].copyWith(
          isLiked: result.liked,
          likesCount: result.likesCount,
        );
        notifyListeners();
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> updateTags(int photoId, List<String> tags) async {
    try {
      final updatedPhoto = await _photoService.updatePhotoTags(photoId, tags);
      final index = _photos.indexWhere((p) => p.id == photoId);
      if (index != -1) {
        _photos[index] = updatedPhoto;
        notifyListeners();
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  Future<void> uploadPhotos(List<XFile> files, int? eventId) async {
    try {
      await _photoService.uploadPhotos(files, eventId);
    } catch (e) {
      rethrow;
    }
  }

  void handleMessage(Map<String, dynamic> data) {
    debugPrint('PhotoProvider: Received message: $data');
    if (data['type'] == 'photo_like_update') {
      final photoId = (data['photo_id'] as num).toInt();
      final likesCount = (data['likes_count'] as num).toInt();
      
      final index = _photos.indexWhere((p) => p.id == photoId);
      if (index != -1) {
        _photos[index] = _photos[index].copyWith(
          likesCount: likesCount,
        );
        notifyListeners();
      }
    } else if (data['type'] == 'new_comment') {
      final photoId = (data['photo_id'] as num).toInt();
      final commentsCount = (data['comments_count'] as num).toInt();
      
      final index = _photos.indexWhere((p) => p.id == photoId);
      if (index != -1) {
        _photos[index] = _photos[index].copyWith(
          commentsCount: commentsCount,
        );
        notifyListeners();
      }
    } else if (data['type'] == 'photo_processed' && data['status'] == 'completed') {
      // Refresh list if this is the current event
      loadPhotos(_currentEventId);
    }
  }
}
