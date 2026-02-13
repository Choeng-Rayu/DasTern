import 'dart:io';
import 'package:flutter/foundation.dart';
import '../data/repositories/prescription_repository.dart';
import '../models/prescription.dart';
import '../models/medicine.dart';
import '../services/ocr_service.dart';
import '../services/ai_service.dart';
import '../services/api_client.dart';
import '../utils/app_logger.dart';

class ScanProvider with ChangeNotifier {
  final PrescriptionRepository _repository;

  ScanProvider({PrescriptionRepository? repository})
      : _repository = repository ?? _createDefaultRepository();

  static PrescriptionRepository _createDefaultRepository() {
    final apiClient = APIClient();
    return PrescriptionRepository(
      ocrService: OCRService(apiClient: apiClient),
      aiService: AIService(apiClient: apiClient),
    );
  }

  File? _imageFile;
  ProcessStatus _status = ProcessStatus.initial;
  String? _statusMessage;
  Prescription? _prescription;
  String? _errorMessage;

  // Getters
  File? get imageFile => _imageFile;
  ProcessStatus get status => _status;
  String? get statusMessage => _statusMessage;
  Prescription? get prescription => _prescription;
  String? get errorMessage => _errorMessage;

  bool get isLoading =>
      _status == ProcessStatus.scanning || _status == ProcessStatus.analyzing;

  void reset() {
    _imageFile = null;
    _status = ProcessStatus.initial;
    _statusMessage = null;
    _prescription = null;
    _errorMessage = null;
    notifyListeners();
  }

  Future<void> setImage(File file) async {
    _imageFile = file;
    _status = ProcessStatus.scanned; // Ready to scan
    _errorMessage = null;
    notifyListeners();
  }

  Future<void> processPrescription() async {
    if (_imageFile == null) return;

    try {
      // Step 1: OCR
      _status = ProcessStatus.scanning;
      _statusMessage = "Reading prescription...";
      _errorMessage = null;
      notifyListeners();

      final ocrResult = await _repository.scanPrescription(_imageFile!.path);

      // Step 2: AI Analysis
      _status = ProcessStatus.analyzing;
      _statusMessage = "Understanding prescription...";
      notifyListeners();

      final prescription = await _repository.analyzePrescription(ocrResult);
      _prescription = prescription;
      _status = ProcessStatus.analyzed;
      _statusMessage = "Complete!";
      notifyListeners();
    } catch (e) {
      AppLogger.e("Processing failed", e);
      _status = ProcessStatus.error;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
    }
  }

  void updateMedicalDetails(int index, Medicine updatedMedicine) {
    if (_prescription == null) return;

    final currentMeds = List<Medicine>.from(_prescription!.medications);
    if (index >= 0 && index < currentMeds.length) {
      currentMeds[index] = updatedMedicine;
      _prescription = _prescription!.copyWith(medications: currentMeds);
      notifyListeners();
    }
  }

  Future<void> confirmPrescription() async {
    // Save to DB or backend would go here
    _status = ProcessStatus.confirmed;
    notifyListeners();
  }
}
