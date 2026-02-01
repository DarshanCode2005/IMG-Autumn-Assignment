// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Profile _$ProfileFromJson(Map<String, dynamic> json) => Profile(
  bio: json['bio'] as String?,
  batch: json['batch'] as String?,
  dept: json['dept'] as String?,
  profilePic: json['profile_pic'] as String?,
);

Map<String, dynamic> _$ProfileToJson(Profile instance) => <String, dynamic>{
  'bio': instance.bio,
  'batch': instance.batch,
  'dept': instance.dept,
  'profile_pic': instance.profilePic,
};

User _$UserFromJson(Map<String, dynamic> json) => User(
  id: (json['id'] as num?)?.toInt() ?? 0,
  username: json['username'] as String,
  email: json['email'] as String,
  role: json['role'] as String,
  firstName: json['first_name'] as String? ?? '',
  lastName: json['last_name'] as String? ?? '',
  isVerified: json['is_verified'] as bool,
  profile: json['profile'] == null
      ? null
      : Profile.fromJson(json['profile'] as Map<String, dynamic>),
);

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
  'id': instance.id,
  'username': instance.username,
  'email': instance.email,
  'role': instance.role,
  'first_name': instance.firstName,
  'last_name': instance.lastName,
  'is_verified': instance.isVerified,
  'profile': instance.profile,
};
