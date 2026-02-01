import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final int id;
  final String email;
  final String role;
  @JsonKey(name: 'is_verified')
  final bool isVerified;

  User({
    required this.id,
    required this.email,
    required this.role,
    required this.isVerified,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
