import 'package:json_annotation/json_annotation.dart';

part 'event.g.dart';

@JsonSerializable()
class Event {
  final int id;
  final String name;
  final String slug;
  final String date;  // API returns date string "YYYY-MM-DD"
  final String? location;
  final String? description;
  @JsonKey(name: 'qr_code_path')
  final String? qrCodePath;

  Event({
    required this.id,
    required this.name,
    required this.slug,
    required this.date,
    this.location,
    this.description,
    this.qrCodePath,
  });

  factory Event.fromJson(Map<String, dynamic> json) => _$EventFromJson(json);
  Map<String, dynamic> toJson() => _$EventToJson(this);
}
