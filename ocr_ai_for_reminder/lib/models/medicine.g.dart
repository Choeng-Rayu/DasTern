// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'medicine.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$MedicineImpl _$$MedicineImplFromJson(Map<String, dynamic> json) =>
    _$MedicineImpl(
      name: json['name'] as String,
      dosage: json['dosage'] as String,
      frequency: json['frequency'] as String,
      duration: json['duration'] as String?,
      instructions: json['instructions'] as String?,
      isMorning: json['isMorning'] as bool? ?? false,
      isAfternoon: json['isAfternoon'] as bool? ?? false,
      isEvening: json['isEvening'] as bool? ?? false,
      isNight: json['isNight'] as bool? ?? false,
    );

Map<String, dynamic> _$$MedicineImplToJson(_$MedicineImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'dosage': instance.dosage,
      'frequency': instance.frequency,
      'duration': instance.duration,
      'instructions': instance.instructions,
      'isMorning': instance.isMorning,
      'isAfternoon': instance.isAfternoon,
      'isEvening': instance.isEvening,
      'isNight': instance.isNight,
    };
