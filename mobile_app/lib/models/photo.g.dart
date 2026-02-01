// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'photo.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Photo _$PhotoFromJson(Map<String, dynamic> json) => Photo(
  id: (json['id'] as num).toInt(),
  originalImage: json['original_image'] as String?,
  thumbnailImage: json['thumbnail_image'] as String?,
  watermarkedImage: json['watermarked_image'] as String?,
  likesCount: (json['likes_count'] as num?)?.toInt() ?? 0,
  isLiked: json['is_liked'] as bool? ?? false,
  commentsCount: (json['comments_count'] as num?)?.toInt() ?? 0,
  event: (json['event'] as num?)?.toInt(),
  uploader: json['uploader'],
  aiTags: (json['ai_tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
  manualTags: (json['manual_tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
  exifData: json['exif_data'] as Map<String, dynamic>?,
  processingStatus: json['processing_status'] as String?,
);

Map<String, dynamic> _$PhotoToJson(Photo instance) => <String, dynamic>{
  'id': instance.id,
  'original_image': instance.originalImage,
  'thumbnail_image': instance.thumbnailImage,
  'watermarked_image': instance.watermarkedImage,
  'likes_count': instance.likesCount,
  'is_liked': instance.isLiked,
  'comments_count': instance.commentsCount,
  'event': instance.event,
  'uploader': instance.uploader,
  'ai_tags': instance.aiTags,
  'manual_tags': instance.manualTags,
  'exif_data': instance.exifData,
  'processing_status': instance.processingStatus,
};
