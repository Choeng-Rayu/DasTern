import 'medication.dart';

class AiResponse {
  final List<Medication> medications;
  final String? summary;
  final List<String>? reminders;
  final String? error;

  AiResponse({
    required this.medications,
    this.summary,
    this.reminders,
    this.error,
  });

  factory AiResponse.fromJson(Map<String, dynamic> json) {
    return AiResponse(
      medications: json['medications'] != null
          ? (json['medications'] as List)
              .map((m) => Medication.fromJson(m))
              .toList()
          : [],
      summary: json['summary'],
      reminders: json['reminders'] != null
          ? List<String>.from(json['reminders'])
          : null,
      error: json['error'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'medications': medications.map((m) => m.toJson()).toList(),
      'summary': summary,
      'reminders': reminders,
      'error': error,
    };
  }

  bool get hasError => error != null && error!.isNotEmpty;
  bool get hasMedications => medications.isNotEmpty;
}
