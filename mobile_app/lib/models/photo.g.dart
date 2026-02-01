// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'photo.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Photo _$PhotoFromJson(Map<String, dynamic> json) => Photo(
      id: (json['id'] as num?)?.toInt() ?? 0,
      originalPath: json['original_path'] as String? ?? '',
      thumbnailPath: json['thumbnail_path'] as String?,
      watermarkedPath: json['watermarked_path'] as String?,
      likesCount: (json['likes_count'] as num?)?.toInt() ?? 0,
      isLiked: json['is_liked'] as bool? ?? false,
      commentsCount: (json['comments_count'] as num?)?.toInt() ?? 0,
      eventId: (json['event_id'] as num?)?.toInt(),
      uploaderId: (json['uploader_id'] as num?)?.toInt() ?? 0,
      aiTags: (json['ai_tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
      manualTags: (json['manual_tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
      exifData: json['exif_data'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$PhotoToJson(Photo instance) => <String, dynamic>{
      'id': instance.id,
      'original_path': instance.originalPath,
      'thumbnail_path': instance.thumbnailPath,
      'watermarked_path': instance.watermarkedPath,
      'likes_count': instance.likesCount,
      'is_liked': instance.isLiked,
      'comments_count': instance.commentsCount,
      'event_id': instance.eventId,
      'uploader_id': instance.uploaderId,
      'ai_tags': instance.aiTags,
      'manual_tags': instance.manualTags,
      'exif_data': instance.exifData,
    };
