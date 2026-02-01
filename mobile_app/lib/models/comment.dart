import 'package:json_annotation/json_annotation.dart';

part 'comment.g.dart';

@JsonSerializable()
class Comment {
  final int id;
  final String content;
  @JsonKey(name: 'author_id')
  final int authorId;
  @JsonKey(name: 'author_email')
  final String? authorEmail;
  @JsonKey(name: 'parent_id')
  final int? parentId;
  @JsonKey(name: 'created_at')
  final String createdAt;
  final List<Comment>? replies;

  Comment({
    required this.id,
    required this.content,
    required this.authorId,
    this.authorEmail,
    this.parentId,
    required this.createdAt,
    this.replies,
  });

  factory Comment.fromJson(Map<String, dynamic> json) => _$CommentFromJson(json);
  Map<String, dynamic> toJson() => _$CommentToJson(this);
}
