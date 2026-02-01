import 'package:flutter/material.dart';
import '../api/api_client.dart';
import '../models/comment.dart';

class CommentProvider extends ChangeNotifier {
  final ApiClient _apiClient = ApiClient();
  Map<int, List<Comment>> _photoComments = {};
  bool _isLoading = false;

  List<Comment> getCommentsForPhoto(int photoId) => _photoComments[photoId] ?? [];
  bool get isLoading => _isLoading;

  Future<void> loadComments(int photoId) async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.dio.get('/photos/$photoId/comments');
      final List<dynamic> data = response.data;
      _photoComments[photoId] = data.map((json) => Comment.fromJson(json)).toList();
    } catch (e) {
      debugPrint('Error loading comments: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> addComment(int photoId, String content, {int? parentId}) async {
    try {
      await _apiClient.dio.post('/photos/$photoId/comments', data: {
        'content': content,
        'parent_id': parentId,
      });
      await loadComments(photoId); // Reload
    } catch (e) {
      debugPrint('Error adding comment: $e');
      rethrow;
    }
  }
}
