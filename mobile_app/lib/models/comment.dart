import 'package:json_annotation/json_annotation.dart';

part 'comment.g.dart';

@JsonSerializable()
class Comment {
  final int id;
  final String content;
  final dynamic author;  // Can be a nested object or null
  @JsonKey(name: 'author_email')
  final String? authorEmail;
  final int? parent;
  @JsonKey(name: 'created_at')
  final String createdAt;
  final List<Comment>? replies;

  Comment({
    required this.id,
    required this.content,
    this.author,
    this.authorEmail,
    this.parent,
    required this.createdAt,
    this.replies,
  });

  factory Comment.fromJson(Map<String, dynamic> json) => _$CommentFromJson(json);
  Map<String, dynamic> toJson() => _$CommentToJson(this);
  
  // Helper to get author ID
  int get authorId => author is Map ? author['id'] ?? 0 : 0;
  
  // Helper to get display name
  String get authorDisplayName {
    if (authorEmail != null) return authorEmail!;
    if (author is Map) {
      return author['email'] ?? author['username'] ?? 'User ${author['id']}';
    }
    return 'Unknown';
  }
}
