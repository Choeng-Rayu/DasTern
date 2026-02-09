// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prescription.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$PrescriptionImpl _$$PrescriptionImplFromJson(Map<String, dynamic> json) =>
    _$PrescriptionImpl(
      id: json['id'] as String,
      medications: (json['medications'] as List<dynamic>?)
              ?.map((e) => Medicine.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      patientName: json['patientName'] as String?,
      doctorName: json['doctorName'] as String?,
      date: json['date'] as String?,
      status: $enumDecodeNullable(_$ProcessStatusEnumMap, json['status']) ??
          ProcessStatus.initial,
    );

Map<String, dynamic> _$$PrescriptionImplToJson(_$PrescriptionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'medications': instance.medications,
      'patientName': instance.patientName,
      'doctorName': instance.doctorName,
      'date': instance.date,
      'status': _$ProcessStatusEnumMap[instance.status]!,
    };

const _$ProcessStatusEnumMap = {
  ProcessStatus.initial: 'initial',
  ProcessStatus.scanning: 'scanning',
  ProcessStatus.scanned: 'scanned',
  ProcessStatus.analyzing: 'analyzing',
  ProcessStatus.analyzed: 'analyzed',
  ProcessStatus.confirmed: 'confirmed',
  ProcessStatus.error: 'error',
};
