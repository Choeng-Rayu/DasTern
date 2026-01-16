/// Represents a single medicine entry from a prescription
class Medicine {
  final int id;
  final String name;
  final String? nameKhmer;
  final String dosage;
  final String quantity;
  final String route;
  final String frequency;
  final String? duration;
  final String? instructions;
  final List<MedicineSchedule> schedule;

  Medicine({
    required this.id,
    required this.name,
    this.nameKhmer,
    required this.dosage,
    required this.quantity,
    required this.route,
    required this.frequency,
    this.duration,
    this.instructions,
    required this.schedule,
  });

  factory Medicine.fromJson(Map<String, dynamic> json) {
    return Medicine(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      nameKhmer: json['nameKhmer'],
      dosage: json['dosage'] ?? '',
      quantity: json['quantity'] ?? '',
      route: json['route'] ?? 'PO',
      frequency: json['frequency'] ?? '',
      duration: json['duration'],
      instructions: json['instructions'],
      schedule: (json['schedule'] as List<dynamic>?)
              ?.map((s) => MedicineSchedule.fromJson(s))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'nameKhmer': nameKhmer,
      'dosage': dosage,
      'quantity': quantity,
      'route': route,
      'frequency': frequency,
      'duration': duration,
      'instructions': instructions,
      'schedule': schedule.map((s) => s.toJson()).toList(),
    };
  }

  Medicine copyWith({
    int? id,
    String? name,
    String? nameKhmer,
    String? dosage,
    String? quantity,
    String? route,
    String? frequency,
    String? duration,
    String? instructions,
    List<MedicineSchedule>? schedule,
  }) {
    return Medicine(
      id: id ?? this.id,
      name: name ?? this.name,
      nameKhmer: nameKhmer ?? this.nameKhmer,
      dosage: dosage ?? this.dosage,
      quantity: quantity ?? this.quantity,
      route: route ?? this.route,
      frequency: frequency ?? this.frequency,
      duration: duration ?? this.duration,
      instructions: instructions ?? this.instructions,
      schedule: schedule ?? this.schedule,
    );
  }
}

/// Schedule for when to take medicine
class MedicineSchedule {
  final String time;
  final String period;
  final bool withFood;

  MedicineSchedule({
    required this.time,
    required this.period,
    required this.withFood,
  });

  factory MedicineSchedule.fromJson(Map<String, dynamic> json) {
    return MedicineSchedule(
      time: json['time'] ?? '08:00',
      period: json['period'] ?? 'morning',
      withFood: json['withFood'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'time': time,
      'period': period,
      'withFood': withFood,
    };
  }
}

/// Parsed prescription data from OCR
class PrescriptionData {
  final String? patientName;
  final String? patientAge;
  final String? patientGender;
  final String? doctorName;
  final String? hospitalName;
  final String? date;
  final List<Medicine> medicines;
  final String? rawText;

  PrescriptionData({
    this.patientName,
    this.patientAge,
    this.patientGender,
    this.doctorName,
    this.hospitalName,
    this.date,
    required this.medicines,
    this.rawText,
  });

  factory PrescriptionData.fromJson(Map<String, dynamic> json) {
    return PrescriptionData(
      patientName: json['patientName'],
      patientAge: json['patientAge'],
      patientGender: json['patientGender'],
      doctorName: json['doctorName'],
      hospitalName: json['hospitalName'],
      date: json['date'],
      medicines: (json['medicines'] as List<dynamic>?)
              ?.map((m) => Medicine.fromJson(m))
              .toList() ??
          [],
      rawText: json['rawText'],
    );
  }
}

/// Reminder data for notifications
class Reminder {
  final int medicineId;
  final String medicineName;
  final String dosage;
  final String scheduledTime;
  final String period;
  final String instructions;

  Reminder({
    required this.medicineId,
    required this.medicineName,
    required this.dosage,
    required this.scheduledTime,
    required this.period,
    required this.instructions,
  });

  factory Reminder.fromJson(Map<String, dynamic> json) {
    return Reminder(
      medicineId: json['medicineId'] ?? 0,
      medicineName: json['medicineName'] ?? '',
      dosage: json['dosage'] ?? '',
      scheduledTime: json['scheduledTime'] ?? '',
      period: json['period'] ?? '',
      instructions: json['instructions'] ?? '',
    );
  }
}

