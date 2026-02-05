import 'package:freezed_annotation/freezed_annotation.dart';

part 'ai_response_dto.freezed.dart';
part 'ai_response_dto.g.dart';

@freezed
class AiResponseDto with _$AiResponseDto {
  const factory AiResponseDto({
    required bool success,
    String? error,
    @JsonKey(name: 'patient_info') Map<String, dynamic>? patientInfo,
    @JsonKey(name: 'medical_info') Map<String, dynamic>? medicalInfo,
    @JsonKey(name: 'medications') List<MedicationItemDto>? medications,
    Map<String, dynamic>? metadata,
  }) = _AiResponseDto;

  factory AiResponseDto.fromJson(Map<String, dynamic> json) =>
      _$AiResponseDtoFromJson(json);
}

// Logic for MedicationItemDto remains similar, or we can inline it if cleaner
@freezed
class MedicationItemDto with _$MedicationItemDto {
  const factory MedicationItemDto({
    required String name,
    required String dosage,
    List<String>? times,
    @JsonKey(name: 'times_24h') List<String>? times24h,
    String? repeat,
    String? notes,
  }) = _MedicationItemDto;

  factory MedicationItemDto.fromJson(Map<String, dynamic> json) =>
      _$MedicationItemDtoFromJson(json);
}
