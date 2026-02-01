// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'comment.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Comment _$CommentFromJson(Map<String, dynamic> json) => Comment(
      id: (json['id'] as num?)?.toInt() ?? 0,
      content: json['content'] as String? ?? '',
      authorId: (json['author_id'] as num?)?.toInt() ?? 0,
      authorEmail: json['author_email'] as String?,
      parentId: (json['parent_id'] as num?)?.toInt(),
      createdAt: json['created_at'] as String? ?? '',
      replies: (json['replies'] as List<dynamic>?)
          ?.map((e) => Comment.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$CommentToJson(Comment instance) => <String, dynamic>{
      'id': instance.id,
      'content': instance.content,
      'author_id': instance.authorId,
      'author_email': instance.authorEmail,
      'parent_id': instance.parentId,
      'created_at': instance.createdAt,
      'replies': instance.replies,
    };
