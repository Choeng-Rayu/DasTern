/// Medication data models with manual JSON serialization
/// Matches the AI Service API structure from schemas.py

/// Medication information model from AI Service
class MedicationInfo {
  final String name;
  final String dosage;
  final List<String> times;
  final List<String> times24h;
  final String repeat;
  final int? durationDays;
  final String notes;

  MedicationInfo({
    required this.name,
    required this.dosage,
    required this.times,
    required this.times24h,
    required this.repeat,
    this.durationDays,
    required this.notes,
  });

  factory MedicationInfo.fromJson(Map<String, dynamic> json) {
    return MedicationInfo(
      name: json['name'] ?? '',
      dosage: json['dosage'] ?? '',
      times: json['times'] != null ? List<String>.from(json['times']) : [],
      times24h:
          json['times_24h'] != null ? List<String>.from(json['times_24h']) : [],
      repeat: json['repeat'] ?? 'daily',
      durationDays: json['duration_days'],
      notes: json['notes'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'dosage': dosage,
      'times': times,
      'times_24h': times24h,
      'repeat': repeat,
      'duration_days': durationDays,
      'notes': notes,
    };
  }

  @override
  String toString() =>
      'MedicationInfo(name: $name, dosage: $dosage, times: $times)';
}

/// Patient information model from AI Service
class PatientInfo {
  final String name;
  final String id;
  final int? age;
  final String gender;
  final String hospitalCode;

  PatientInfo({
    required this.name,
    required this.id,
    this.age,
    required this.gender,
    required this.hospitalCode,
  });

  factory PatientInfo.fromJson(Map<String, dynamic> json) {
    return PatientInfo(
      name: json['name'] ?? '',
      id: json['id'] ?? '',
      age: json['age'],
      gender: json['gender'] ?? '',
      hospitalCode: json['hospital_code'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'id': id,
      'age': age,
      'gender': gender,
      'hospital_code': hospitalCode,
    };
  }
}

/// Medical information model from AI Service
class MedicalInfo {
  final String diagnosis;
  final String doctor;
  final String date;
  final String department;

  MedicalInfo({
    required this.diagnosis,
    required this.doctor,
    required this.date,
    required this.department,
  });

  factory MedicalInfo.fromJson(Map<String, dynamic> json) {
    return MedicalInfo(
      diagnosis: json['diagnosis'] ?? '',
      doctor: json['doctor'] ?? '',
      date: json['date'] ?? '',
      department: json['department'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'diagnosis': diagnosis,
      'doctor': doctor,
      'date': date,
      'department': department,
    };
  }
}

/// Comprehensive prescription data model
class ComprehensivePrescription {
  final PatientInfo patientInfo;
  final MedicalInfo medicalInfo;
  final List<MedicationInfo> medications;

  ComprehensivePrescription({
    required this.patientInfo,
    required this.medicalInfo,
    required this.medications,
  });

  factory ComprehensivePrescription.fromJson(Map<String, dynamic> json) {
    return ComprehensivePrescription(
      patientInfo: json['patient_info'] != null
          ? PatientInfo.fromJson(json['patient_info'])
          : PatientInfo(name: '', id: '', gender: '', hospitalCode: ''),
      medicalInfo: json['medical_info'] != null
          ? MedicalInfo.fromJson(json['medical_info'])
          : MedicalInfo(diagnosis: '', doctor: '', date: '', department: ''),
      medications: json['medications'] != null
          ? (json['medications'] as List)
              .map((e) => MedicationInfo.fromJson(e))
              .toList()
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'patient_info': patientInfo.toJson(),
      'medical_info': medicalInfo.toJson(),
      'medications': medications.map((e) => e.toJson()).toList(),
    };
  }
}

/// View model for UI display - wraps MedicationInfo with computed properties
class Medication {
  final String name;
  final String? dosage;
  final String? frequency;
  final List<String>? times;
  final String? instructions;
  final String? duration;

  Medication({
    required this.name,
    this.dosage,
    this.frequency,
    this.times,
    this.instructions,
    this.duration,
  });

  /// Create from MedicationInfo
  factory Medication.fromMedicationInfo(MedicationInfo info) {
    return Medication(
      name: info.name,
      dosage: info.dosage.isNotEmpty ? info.dosage : null,
      frequency: info.repeat.isNotEmpty ? info.repeat : null,
      times: info.times.isNotEmpty ? info.times : null,
      instructions: info.notes.isNotEmpty ? info.notes : null,
      duration: info.durationDays != null ? '${info.durationDays} days' : null,
    );
  }

  /// Computed property for display
  String get displayTimes => times?.join(', ') ?? '';

  /// Convert list of MedicationInfo to list of Medication
  static List<Medication> fromMedicationInfoList(List<MedicationInfo> infos) {
    return infos.map((info) => Medication.fromMedicationInfo(info)).toList();
  }
}
