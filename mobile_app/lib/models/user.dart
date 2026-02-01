import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class Profile {
  final String? bio;
  final String? batch;
  final String? dept;
  @JsonKey(name: 'profile_pic')
  final String? profilePic;

  Profile({
    this.bio,
    this.batch,
    this.dept,
    this.profilePic,
  });

  factory Profile.fromJson(Map<String, dynamic> json) => _$ProfileFromJson(json);
  Map<String, dynamic> toJson() => _$ProfileToJson(this);

  // Helper to get full URL
  String? get fullProfilePicUrl {
    if (profilePic == null || profilePic!.isEmpty) return null;
    // If already a full URL, return as is
    if (profilePic!.startsWith('http')) return profilePic;
    // Otherwise, prepend base URL
    return 'http://localhost:8000$profilePic';
  }
}

@JsonSerializable()
class User {
  final int id;
  final String username;
  final String email;
  final String role;
  @JsonKey(name: 'first_name')
  final String firstName;
  @JsonKey(name: 'last_name')
  final String lastName;
  @JsonKey(name: 'is_verified')
  final bool isVerified;
  final Profile? profile;

  User({
    required this.id,
    required this.username,
    required this.email,
    required this.role,
    this.firstName = '',
    this.lastName = '',
    required this.isVerified,
    this.profile,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
