import 'package:freezed_annotation/freezed_annotation.dart';

part 'medicine.freezed.dart';
part 'medicine.g.dart';

@freezed
class Medicine with _$Medicine {
  const factory Medicine({
    required String name,
    required String dosage,
    required String frequency,
    String? duration,
    String? instructions,
    @Default(false) bool isMorning,
    @Default(false) bool isAfternoon,
    @Default(false) bool isEvening,
    @Default(false) bool isNight,
  }) = _Medicine;

  factory Medicine.fromJson(Map<String, dynamic> json) =>
      _$MedicineFromJson(json);
}
