import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import '../models/medication.dart';

/// Service for storing and retrieving prescription data locally
class PrescriptionStorage {
  static const String _fileName = 'prescriptions.json';

  /// Save prescription with medications to local storage
  Future<void> savePrescription(PrescriptionData prescription) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$_fileName');

      // Load existing prescriptions
      List<PrescriptionData> prescriptions = await loadPrescriptions();

      // Add new prescription
      prescriptions.add(prescription);

      // Save to file
      final jsonData = prescriptions.map((p) => p.toJson()).toList();
      await file.writeAsString(json.encode(jsonData));
    } catch (e) {
      print('Error saving prescription: $e');
      rethrow;
    }
  }

  /// Load all prescriptions from local storage
  Future<List<PrescriptionData>> loadPrescriptions() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$_fileName');

      if (!await file.exists()) {
        return [];
      }

      final contents = await file.readAsString();
      final List<dynamic> jsonData = json.decode(contents);

      return jsonData.map((json) => PrescriptionData.fromJson(json)).toList();
    } catch (e) {
      print('Error loading prescriptions: $e');
      return [];
    }
  }

  /// Get prescription by ID
  Future<PrescriptionData?> getPrescription(String id) async {
    final prescriptions = await loadPrescriptions();
    try {
      return prescriptions.firstWhere((p) => p.id == id);
    } catch (e) {
      return null;
    }
  }

  /// Delete prescription by ID
  Future<void> deletePrescription(String id) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$_fileName');

      List<PrescriptionData> prescriptions = await loadPrescriptions();
      prescriptions.removeWhere((p) => p.id == id);

      final jsonData = prescriptions.map((p) => p.toJson()).toList();
      await file.writeAsString(json.encode(jsonData));
    } catch (e) {
      print('Error deleting prescription: $e');
      rethrow;
    }
  }

  /// Clear all prescriptions
  Future<void> clearAll() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$_fileName');

      if (await file.exists()) {
        await file.delete();
      }
    } catch (e) {
      print('Error clearing prescriptions: $e');
      rethrow;
    }
  }
}

/// Prescription data model containing medications and metadata
class PrescriptionData {
  final String id;
  final DateTime createdAt;
  final List<MedicationInfo> medications;
  final String? patientName;
  final int? patientAge;
  final String? diagnosis;
  final Map<String, dynamic>? rawOcrData;
  final Map<String, dynamic>? aiMetadata;

  PrescriptionData({
    required this.id,
    required this.createdAt,
    required this.medications,
    this.patientName,
    this.patientAge,
    this.diagnosis,
    this.rawOcrData,
    this.aiMetadata,
  });

  factory PrescriptionData.fromJson(Map<String, dynamic> json) {
    return PrescriptionData(
      id: json['id'],
      createdAt: DateTime.parse(json['created_at']),
      medications: (json['medications'] as List)
          .map((m) => MedicationInfo.fromJson(m))
          .toList(),
      patientName: json['patient_name'],
      patientAge: json['patient_age'],
      diagnosis: json['diagnosis'],
      rawOcrData: json['raw_ocr_data'],
      aiMetadata: json['ai_metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'created_at': createdAt.toIso8601String(),
      'medications': medications.map((m) => m.toJson()).toList(),
      'patient_name': patientName,
      'patient_age': patientAge,
      'diagnosis': diagnosis,
      'raw_ocr_data': rawOcrData,
      'ai_metadata': aiMetadata,
    };
  }

  /// Create a unique ID for the prescription
  static String generateId() {
    return DateTime.now().millisecondsSinceEpoch.toString();
  }
}
