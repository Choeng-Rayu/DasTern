// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ai_response_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AiResponseDtoImpl _$$AiResponseDtoImplFromJson(Map<String, dynamic> json) =>
    _$AiResponseDtoImpl(
      success: json['success'] as bool,
      error: json['error'] as String?,
      patientInfo: json['patient_info'] as Map<String, dynamic>?,
      medicalInfo: json['medical_info'] as Map<String, dynamic>?,
      medications: (json['medications'] as List<dynamic>?)
          ?.map((e) => MedicationItemDto.fromJson(e as Map<String, dynamic>))
          .toList(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$AiResponseDtoImplToJson(_$AiResponseDtoImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'error': instance.error,
      'patient_info': instance.patientInfo,
      'medical_info': instance.medicalInfo,
      'medications': instance.medications,
      'metadata': instance.metadata,
    };

_$MedicationItemDtoImpl _$$MedicationItemDtoImplFromJson(
        Map<String, dynamic> json) =>
    _$MedicationItemDtoImpl(
      name: json['name'] as String,
      dosage: json['dosage'] as String,
      times:
          (json['times'] as List<dynamic>?)?.map((e) => e as String).toList(),
      times24h: (json['times_24h'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      repeat: json['repeat'] as String?,
      notes: json['notes'] as String?,
    );

Map<String, dynamic> _$$MedicationItemDtoImplToJson(
        _$MedicationItemDtoImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'dosage': instance.dosage,
      'times': instance.times,
      'times_24h': instance.times24h,
      'repeat': instance.repeat,
      'notes': instance.notes,
    };
