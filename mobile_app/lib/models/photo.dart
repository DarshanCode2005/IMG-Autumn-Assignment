import 'package:json_annotation/json_annotation.dart';

part 'photo.g.dart';

@JsonSerializable()
class Photo {
  final int id;
  @JsonKey(name: 'original_image')
  final String? originalImage;
  @JsonKey(name: 'thumbnail_image')
  final String? thumbnailImage;
  @JsonKey(name: 'watermarked_image')
  final String? watermarkedImage;
  @JsonKey(name: 'likes_count')
  final int likesCount;
  @JsonKey(name: 'is_liked')
  final bool isLiked;
  @JsonKey(name: 'comments_count')
  final int commentsCount;
  final int? event;
  final dynamic uploader;
  @JsonKey(name: 'ai_tags')
  final List<String>? aiTags;
  @JsonKey(name: 'manual_tags')
  final List<String>? manualTags;
  @JsonKey(name: 'exif_data')
  final Map<String, dynamic>? exifData;
  @JsonKey(name: 'processing_status')
  final String? processingStatus;

  Photo({
    required this.id,
    this.originalImage,
    this.thumbnailImage,
    this.watermarkedImage,
    this.likesCount = 0,
    this.isLiked = false,
    this.commentsCount = 0,
    this.event,
    this.uploader,
    this.aiTags,
    this.manualTags,
    this.exifData,
    this.processingStatus,
  });

  factory Photo.fromJson(Map<String, dynamic> json) => _$PhotoFromJson(json);
  Map<String, dynamic> toJson() => _$PhotoToJson(this);
  
  // CopyWith helper
  Photo copyWith({
    int? id,
    String? originalImage,
    String? thumbnailImage,
    String? watermarkedImage,
    int? likesCount,
    bool? isLiked,
    int? commentsCount,
    int? event,
    dynamic uploader,
    List<String>? aiTags,
    List<String>? manualTags,
    Map<String, dynamic>? exifData,
    String? processingStatus,
  }) {
    return Photo(
      id: id ?? this.id,
      originalImage: originalImage ?? this.originalImage,
      thumbnailImage: thumbnailImage ?? this.thumbnailImage,
      watermarkedImage: watermarkedImage ?? this.watermarkedImage,
      likesCount: likesCount ?? this.likesCount,
      isLiked: isLiked ?? this.isLiked,
      commentsCount: commentsCount ?? this.commentsCount,
      event: event ?? this.event,
      uploader: uploader ?? this.uploader,
      aiTags: aiTags ?? this.aiTags,
      manualTags: manualTags ?? this.manualTags,
      exifData: exifData ?? this.exifData,
      processingStatus: processingStatus ?? this.processingStatus,
    );
  }
  
  // Helpers to get full URLs
  static const String _baseUrl = 'http://localhost:8000';
  
  String get fullThumbnailUrl => thumbnailImage != null 
    ? '$_baseUrl$thumbnailImage' 
    : (originalImage != null ? '$_baseUrl$originalImage' : '');
    
  String get fullWatermarkedUrl => watermarkedImage != null 
    ? '$_baseUrl$watermarkedImage' 
    : (originalImage != null ? '$_baseUrl$originalImage' : '');

  String get fullOriginalUrl => originalImage != null ? '$_baseUrl$originalImage' : '';
  
  int get uploaderId => uploader is Map ? uploader['id'] ?? 0 : 0;
}
