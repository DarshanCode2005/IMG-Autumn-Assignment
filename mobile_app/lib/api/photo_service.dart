import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import '../utils/constants.dart';
import 'api_client.dart';
import '../models/photo.dart';
import '../models/like_response.dart';

class PhotoService {
  final ApiClient _apiClient;

  PhotoService(this._apiClient);

  Future<List<Photo>> searchPhotos({int? eventId, String? tags, int skip = 0, int limit = 100}) async {
    try {
      final Map<String, dynamic> queryParams = {
        'offset': skip,
        'limit': limit,
      };
      if (eventId != null) {
        queryParams['event_id'] = eventId;
      }
      if (tags != null && tags.isNotEmpty) {
        queryParams['tags'] = tags;
      }

      final response = await _apiClient.dio.get('/photos/', queryParameters: queryParams);
      
      // DRF pagination returns {count, next, previous, results}
      if (response.data is Map && response.data.containsKey('results')) {
        final List<dynamic> data = response.data['results'];
        return data.map((json) => Photo.fromJson(json)).toList();
      }
      
      // Fallback if pagination is disabled or different format
      final List<dynamic> data = response.data;
      return data.map((json) => Photo.fromJson(json)).toList();
    } catch (e) {
      throw e;
    }
  }

  Future<LikeResponse> toggleLike(int photoId) async {
    try {
      final response = await _apiClient.dio.post('/photos/$photoId/like/');
      return LikeResponse.fromJson(response.data);
    } catch (e) {
      throw e;
    }
  }

  Future<Photo> updatePhotoTags(int photoId, List<String> tags) async {
    try {
      final response = await _apiClient.dio.put(
        '/photos/$photoId/', 
        data: {'manual_tags': tags}
      );
      return Photo.fromJson(response.data);
    } catch (e) {
      throw e;
    }
  }

  Future<void> uploadPhotos(List<XFile> files, int? eventId) async {
    try {
      debugPrint('PhotoService: Preparing FormData for ${files.length} files. EventID: $eventId');
      
      final Map<String, dynamic> map = {};
      if (eventId != null) {
        map['event_id'] = eventId;
      }

      final List<MultipartFile> multipartFiles = [];
      for (var file in files) {
        if (kIsWeb) {
          final bytes = await file.readAsBytes();
          multipartFiles.add(MultipartFile.fromBytes(
            bytes,
            filename: file.name,
          ));
        } else {
          multipartFiles.add(await MultipartFile.fromFile(
            file.path,
            filename: file.name,
          ));
        }
      }
      map['files'] = multipartFiles;

      final formData = FormData.fromMap(map);

      debugPrint('PhotoService: Sending POST request to ${AppConstants.baseUrl}/photos/upload/');
      final response = await _apiClient.dio.post(
        '/photos/upload/',
        data: formData,
      );
      
      debugPrint('PhotoService: Upload finished. Response: ${response.data}');
    } catch (e) {
      debugPrint('PhotoService: ERROR during upload: $e');
      if (e is DioException) {
        debugPrint('PhotoService: Dio Error Details: ${e.response?.data}');
      }
      throw e;
    }
  }
}
