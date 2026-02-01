class LikeResponse {
  final int photoId;
  final int userId;
  final bool liked;
  final int likesCount;

  LikeResponse({
    required this.photoId,
    required this.userId,
    required this.liked,
    required this.likesCount,
  });

  factory LikeResponse.fromJson(Map<String, dynamic> json) {
    return LikeResponse(
      photoId: (json['photo_id'] as num?)?.toInt() ?? 0,
      userId: (json['user_id'] as num?)?.toInt() ?? 0,
      liked: json['liked'] as bool? ?? false,
      likesCount: (json['likes_count'] as num?)?.toInt() ?? 0,
    );
  }
}
