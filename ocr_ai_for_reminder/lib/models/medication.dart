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

  factory Medication.fromJson(Map<String, dynamic> json) {
    return Medication(
      name: json['name'] ?? json['medication_name'] ?? 'Unknown',
      dosage: json['dosage'] ?? json['dose'],
      frequency: json['frequency'] ?? json['schedule'],
      times: json['times'] != null ? List<String>.from(json['times']) : null,
      instructions: json['instructions'] ?? json['notes'],
      duration: json['duration'] ?? json['period'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'dosage': dosage,
      'frequency': frequency,
      'times': times,
      'instructions': instructions,
      'duration': duration,
    };
  }

  String get displayTimes => times?.join(', ') ?? 'Not specified';
}
