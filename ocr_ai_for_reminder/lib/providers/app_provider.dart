import 'dart:io';
import 'package:flutter/material.dart';
import '../models/ocr_response.dart';
import '../models/ai_response.dart';
import '../services/ocr_service.dart';
import '../services/ai_service.dart';
import 'package:image_picker/image_picker.dart';

class AppProvider extends ChangeNotifier {
  final OcrService _ocrService;
  final AiService _aiService;

  XFile? _selectedImage;
  OcrResponse? _ocrResponse;
  AiResponse? _aiResponse;
  bool _isProcessingOcr = false;
  bool _isProcessingAi = false;
  String? _errorMessage;

  AppProvider({
    OcrService? ocrService,
    AiService? aiService,
  })  : _ocrService = ocrService ?? OcrService(),
        _aiService = aiService ?? AiService();

  XFile? get selectedImage => _selectedImage;
  OcrResponse? get ocrResponse => _ocrResponse;
  AiResponse? get aiResponse => _aiResponse;
  bool get isProcessingOcr => _isProcessingOcr;
  bool get isProcessingAi => _isProcessingAi;
  String? get errorMessage => _errorMessage;
  bool get hasError => _errorMessage != null;

  Future<void> selectImage(XFile image) async {
    _selectedImage = image;
    _ocrResponse = null;
    _aiResponse = null;
    _errorMessage = null;
    notifyListeners();

    await _processOcr();
  }

  Future<void> selectImageFile(File file) async {
    _selectedImage = XFile(file.path);
    _ocrResponse = null;
    _aiResponse = null;
    _errorMessage = null;
    notifyListeners();

    await _processOcr();
  }

  Future<void> _processOcr() async {
    if (_selectedImage == null) return;

    _isProcessingOcr = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final file = File(_selectedImage!.path);
      _ocrResponse = await _ocrService.extractTextFromImage(file);

      if (_ocrResponse?.hasError ?? false) {
        _errorMessage = _ocrResponse?.error;
      }
    } catch (e) {
      _errorMessage = 'Failed to process OCR: $e';
      _ocrResponse = null;
    } finally {
      _isProcessingOcr = false;
      notifyListeners();
    }
  }

  Future<void> processAi() async {
    if (_ocrResponse == null || _ocrResponse!.hasError) {
      _errorMessage = 'No valid OCR data to process';
      notifyListeners();
      return;
    }

    _isProcessingAi = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _aiResponse = await _aiService.extractReminders(_ocrResponse!);

      if (_aiResponse?.hasError ?? false) {
        _errorMessage = _aiResponse?.error;
      }
    } catch (e) {
      _errorMessage = 'Failed to process AI analysis: $e';
      _aiResponse = null;
    } finally {
      _isProcessingAi = false;
      notifyListeners();
    }
  }

  void clear() {
    _selectedImage = null;
    _ocrResponse = null;
    _aiResponse = null;
    _errorMessage = null;
    _isProcessingOcr = false;
    _isProcessingAi = false;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
