// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'comment.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Comment _$CommentFromJson(Map<String, dynamic> json) => Comment(
  id: (json['id'] as num).toInt(),
  content: json['content'] as String,
  author: json['author'],
  authorEmail: json['author_email'] as String?,
  parent: (json['parent'] as num?)?.toInt(),
  createdAt: json['created_at'] as String,
  replies: (json['replies'] as List<dynamic>?)
      ?.map((e) => Comment.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$CommentToJson(Comment instance) => <String, dynamic>{
  'id': instance.id,
  'content': instance.content,
  'author': instance.author,
  'author_email': instance.authorEmail,
  'parent': instance.parent,
  'created_at': instance.createdAt,
  'replies': instance.replies,
};
