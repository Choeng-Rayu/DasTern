import 'package:freezed_annotation/freezed_annotation.dart';
import 'medicine.dart';

part 'prescription.freezed.dart';
part 'prescription.g.dart';

@freezed
class Prescription with _$Prescription {
  const factory Prescription({
    required String id,
    @Default([]) List<Medicine> medications,
    String? patientName,
    String? doctorName,
    String? date,
    @Default(ProcessStatus.initial) ProcessStatus status,
  }) = _Prescription;

  factory Prescription.fromJson(Map<String, dynamic> json) =>
      _$PrescriptionFromJson(json);
}

enum ProcessStatus {
  initial,
  scanning,
  scanned,
  analyzing,
  analyzed,
  confirmed,
  error
}
