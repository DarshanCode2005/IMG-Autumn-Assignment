import 'package:json_annotation/json_annotation.dart';

part 'photo.g.dart';

@JsonSerializable()
class Photo {
  final int id;
  @JsonKey(name: 'original_path')
  final String originalPath;
  @JsonKey(name: 'thumbnail_path')
  final String? thumbnailPath;
  @JsonKey(name: 'watermarked_path')
  final String? watermarkedPath;
  @JsonKey(name: 'likes_count')
  final int likesCount;
  @JsonKey(name: 'is_liked')
  final bool isLiked;
  @JsonKey(name: 'comments_count')
  final int commentsCount;
  @JsonKey(name: 'event_id')
  final int? eventId;
  @JsonKey(name: 'uploader_id')
  final int uploaderId;
  @JsonKey(name: 'ai_tags')
  final List<String>? aiTags;
  @JsonKey(name: 'manual_tags')
  final List<String>? manualTags;
  @JsonKey(name: 'exif_data')
  final Map<String, dynamic>? exifData;

  Photo({
    required this.id,
    required this.originalPath,
    this.thumbnailPath,
    this.watermarkedPath,
    this.likesCount = 0,
    this.isLiked = false,
    this.commentsCount = 0,
    this.eventId,
    required this.uploaderId,
    this.aiTags,
    this.manualTags,
    this.exifData,
  });

  factory Photo.fromJson(Map<String, dynamic> json) => _$PhotoFromJson(json);
  Map<String, dynamic> toJson() => _$PhotoToJson(this);
  
  // CopyWith helper
  Photo copyWith({
    int? id,
    String? originalPath,
    String? thumbnailPath,
    String? watermarkedPath,
    int? likesCount,
    bool? isLiked,
    int? commentsCount,
    int? eventId,
    int? uploaderId,
    List<String>? aiTags,
    List<String>? manualTags,
    Map<String, dynamic>? exifData,
  }) {
    return Photo(
      id: id ?? this.id,
      originalPath: originalPath ?? this.originalPath,
      thumbnailPath: thumbnailPath ?? this.thumbnailPath,
      watermarkedPath: watermarkedPath ?? this.watermarkedPath,
      likesCount: likesCount ?? this.likesCount,
      isLiked: isLiked ?? this.isLiked,
      commentsCount: commentsCount ?? this.commentsCount,
      eventId: eventId ?? this.eventId,
      uploaderId: uploaderId ?? this.uploaderId,
      aiTags: aiTags ?? this.aiTags,
      manualTags: manualTags ?? this.manualTags,
      exifData: exifData ?? this.exifData,
    );
  }
  
  // Helpers to get full URLs
  String get fullThumbnailUrl => thumbnailPath != null 
    ? 'http://localhost:8000/$thumbnailPath' 
    : 'http://localhost:8000/$originalPath';
    
  String get fullWatermarkedUrl => watermarkedPath != null 
    ? 'http://localhost:8000/$watermarkedPath' 
    : 'http://localhost:8000/$originalPath';

  String get fullOriginalUrl => 'http://localhost:8000/$originalPath';
}
