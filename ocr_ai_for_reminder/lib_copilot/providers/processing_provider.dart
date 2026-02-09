import 'package:flutter/material.dart';
import 'package:logger/logger.dart';
import '../services/api_client.dart';
import '../services/ocr_service.dart';
import '../services/ai_service.dart';
import '../models/ocr_response.dart';
import '../models/ai_response.dart';
import '../models/medication.dart';

class ProcessingState {
  final bool isProcessing;
  final String? currentStep;
  final String? error;
  final double progress;

  ProcessingState({
    this.isProcessing = false,
    this.currentStep,
    this.error,
    this.progress = 0.0,
  });

  ProcessingState copyWith({
    bool? isProcessing,
    String? currentStep,
    String? error,
    double? progress,
  }) {
    return ProcessingState(
      isProcessing: isProcessing ?? this.isProcessing,
      currentStep: currentStep ?? this.currentStep,
      error: error ?? this.error,
      progress: progress ?? this.progress,
    );
  }
}

class OCRProvider extends ChangeNotifier {
  final Logger logger = Logger();
  late final OCRService _ocrService;
  late final APIClient _apiClient;

  OCRProvider({String baseUrl = 'http://localhost:8000'}) {
    _apiClient = APIClient(baseUrl: baseUrl);
    _ocrService = OCRService(apiClient: _apiClient);
  }

  // State
  String? _imagePath;
  OCRResponse? _ocrResponse;
  ProcessingState _processingState = ProcessingState();
  bool _isServiceHealthy = false;

  // Getters
  String? get imagePath => _imagePath;
  OCRResponse? get ocrResponse => _ocrResponse;
  ProcessingState get processingState => _processingState;
  bool get isServiceHealthy => _isServiceHealthy;
  bool get hasOCRData => _ocrResponse != null;
  String? get extractedText => _ocrResponse?.fullText;

  /// Check if OCR service is healthy
  Future<void> checkServiceHealth() async {
    try {
      _isServiceHealthy = await _apiClient.healthCheck();
      notifyListeners();
      if (_isServiceHealthy) {
        logger.i('OCR Service is healthy');
      } else {
        logger.w('OCR Service is not responding');
      }
    } catch (e) {
      logger.e('Error checking service health: $e');
      _isServiceHealthy = false;
      notifyListeners();
    }
  }

  /// Set image path
  void setImagePath(String path) {
    _imagePath = path;
    notifyListeners();
    logger.i('Image path set: $path');
  }

  /// Process image with OCR
  Future<bool> processImage({
    String languages = 'eng+khm+fra',
    bool skipEnhancement = false,
  }) async {
    if (_imagePath == null || _imagePath!.isEmpty) {
      _processingState = _processingState.copyWith(
        error: 'No image selected',
      );
      notifyListeners();
      return false;
    }

    try {
      _processingState = _processingState.copyWith(
        isProcessing: true,
        currentStep: 'Processing image...',
        progress: 0.2,
        error: null,
      );
      notifyListeners();

      final response = await _ocrService.processImage(
        _imagePath!,
        languages: languages,
        skipEnhancement: skipEnhancement,
      );

      _ocrResponse = response;
      _processingState = _processingState.copyWith(
        isProcessing: false,
        currentStep: 'Complete',
        progress: 1.0,
      );
      notifyListeners();
      logger.i('OCR processing completed successfully');
      return true;
    } catch (e) {
      _processingState = _processingState.copyWith(
        isProcessing: false,
        error: 'OCR processing failed: ${e.toString()}',
        progress: 0.0,
      );
      notifyListeners();
      logger.e('Error processing image: $e');
      return false;
    }
  }

  /// Get quality metrics
  Map<String, dynamic>? getQualityMetrics() {
    if (_ocrResponse == null) return null;
    return _ocrService.getQualityMetrics(_ocrResponse!);
  }

  /// Reset state
  void reset() {
    _imagePath = null;
    _ocrResponse = null;
    _processingState = ProcessingState();
    notifyListeners();
    logger.i('OCR Provider reset');
  }
}

class AIProvider extends ChangeNotifier {
  final Logger logger = Logger();
  late final AIService _aiService;
  late final APIClient _apiClient;

  AIProvider({String baseUrl = 'http://localhost:8001'}) {
    _apiClient = APIClient(baseUrl: baseUrl);
    _aiService = AIService(apiClient: _apiClient);
  }

  // State
  String? _rawOCRText;
  Map<String, dynamic>? _ocrMetadata;
  AIProcessingResult? _correctionResult;
  ReminderResponse? _reminderResponse;
  ProcessingState _processingState = ProcessingState();
  List<MedicationInfo> _medications = [];

  // Getters
  String? get rawOCRText => _rawOCRText;
  AIProcessingResult? get correctionResult => _correctionResult;
  ReminderResponse? get reminderResponse => _reminderResponse;
  ProcessingState get processingState => _processingState;
  List<MedicationInfo> get medications => _medications;
  bool get hasResults => _reminderResponse != null && _medications.isNotEmpty;

  /// Set raw OCR data
  void setRawOCRData(String text, Map<String, dynamic> metadata) {
    _rawOCRText = text;
    _ocrMetadata = metadata;
    notifyListeners();
    logger.i('Raw OCR data set');
  }

  /// Correct OCR text
  Future<bool> correctOCRText({String language = 'en'}) async {
    if (_rawOCRText == null || _rawOCRText!.isEmpty) {
      _processingState = _processingState.copyWith(
        error: 'No OCR text to correct',
      );
      notifyListeners();
      return false;
    }

    try {
      _processingState = _processingState.copyWith(
        isProcessing: true,
        currentStep: 'Correcting OCR text with AI...',
        progress: 0.3,
        error: null,
      );
      notifyListeners();

      _correctionResult = await _aiService.correctOCRText(
        _rawOCRText!,
        language: language,
        context: _ocrMetadata,
      );

      _processingState = _processingState.copyWith(
        progress: 0.6,
      );
      notifyListeners();
      logger.i('Text correction completed');
      return true;
    } catch (e) {
      _processingState = _processingState.copyWith(
        isProcessing: false,
        error: 'Text correction failed: ${e.toString()}',
        progress: 0.0,
      );
      notifyListeners();
      logger.e('Error correcting text: $e');
      return false;
    }
  }

  /// Extract medication reminders
  Future<bool> extractReminders() async {
    if (_rawOCRText == null || _ocrMetadata == null) {
      _processingState = _processingState.copyWith(
        error: 'Missing OCR data',
      );
      notifyListeners();
      return false;
    }

    try {
      _processingState = _processingState.copyWith(
        currentStep: 'Extracting medication reminders...',
        progress: 0.7,
      );
      notifyListeners();

      _reminderResponse = await _aiService.extractReminders(_ocrMetadata!);
      _medications = _reminderResponse!.medications;

      _processingState = _processingState.copyWith(
        isProcessing: false,
        currentStep: 'Complete',
        progress: 1.0,
      );
      notifyListeners();
      logger.i('Extracted ${_medications.length} medications');
      return true;
    } catch (e) {
      _processingState = _processingState.copyWith(
        isProcessing: false,
        error: 'Reminder extraction failed: ${e.toString()}',
        progress: 0.0,
      );
      notifyListeners();
      logger.e('Error extracting reminders: $e');
      return false;
    }
  }

  /// Process full pipeline
  Future<bool> processFullPipeline({String language = 'en'}) async {
    if (_rawOCRText == null || _ocrMetadata == null) {
      _processingState = _processingState.copyWith(
        error: 'Missing OCR data',
      );
      notifyListeners();
      return false;
    }

    try {
      _processingState = _processingState.copyWith(
        isProcessing: true,
        currentStep: 'Starting AI processing pipeline...',
        progress: 0.1,
        error: null,
      );
      notifyListeners();

      _reminderResponse = await _aiService.processFullPipeline(
        _rawOCRText!,
        _ocrMetadata!,
        language: language,
      );

      _medications = _reminderResponse!.medications;

      _processingState = _processingState.copyWith(
        isProcessing: false,
        currentStep: 'Complete',
        progress: 1.0,
      );
      notifyListeners();
      logger.i('Full pipeline completed with ${_medications.length} medications');
      return true;
    } catch (e) {
      _processingState = _processingState.copyWith(
        isProcessing: false,
        error: 'Pipeline processing failed: ${e.toString()}',
        progress: 0.0,
      );
      notifyListeners();
      logger.e('Error in full pipeline: $e');
      return false;
    }
  }

  /// Reset state
  void reset() {
    _rawOCRText = null;
    _ocrMetadata = null;
    _correctionResult = null;
    _reminderResponse = null;
    _medications = [];
    _processingState = ProcessingState();
    notifyListeners();
    logger.i('AI Provider reset');
  }
}
