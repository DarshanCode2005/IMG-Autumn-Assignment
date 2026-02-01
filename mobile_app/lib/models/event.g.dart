// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'event.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Event _$EventFromJson(Map<String, dynamic> json) => Event(
      id: (json['id'] as num?)?.toInt() ?? 0,
      name: json['name'] as String? ?? '',
      slug: json['slug'] as String? ?? '',
      date: json['date'] as String? ?? '',
      location: json['location'] as String?,
      description: json['description'] as String?,
      qrCodePath: json['qr_code_path'] as String?,
    );

Map<String, dynamic> _$EventToJson(Event instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'slug': instance.slug,
      'date': instance.date,
      'location': instance.location,
      'description': instance.description,
      'qr_code_path': instance.qrCodePath,
    };
