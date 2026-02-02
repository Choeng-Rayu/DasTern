import 'package:logger/logger.dart';
import 'dart:io';
import 'dart:convert';
import 'api_client.dart';
import '../models/ocr_response.dart';

class OCRService {
  final APIClient apiClient;
  final Logger logger = Logger();

  OCRService({required this.apiClient});

  /// Process prescription image and return OCR data
  Future<OCRResponse> processImage(
    String imagePath, {
    String languages = 'eng+khm+fra',
    bool skipEnhancement = false,
  }) async {
    try {
      logger.i('Processing image: $imagePath');

      // Validate file exists
      if (!await File(imagePath).exists()) {
        throw Exception('Image file not found: $imagePath');
      }

      // Upload and process
      final response = await apiClient.uploadImageForOCR(
        imagePath,
        languages: languages,
        skipEnhancement: skipEnhancement,
      );

      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final jsonData = _parseJson(responseBody);
        logger.i('OCR processing successful');
        return OCRResponse.fromJson(jsonData);
      } else {
        final errorBody = await response.stream.bytesToString();
        throw Exception(
          'OCR processing failed: ${response.statusCode} - $errorBody',
        );
      }
    } catch (e) {
      logger.e('Error processing image: $e');
      rethrow;
    }
  }

  /// Extract text from OCR response
  String extractFullText(OCRResponse ocrResponse) {
    try {
      return ocrResponse.fullText;
    } catch (e) {
      logger.e('Error extracting text: $e');
      rethrow;
    }
  }

  /// Parse JSON with error handling
  Map<String, dynamic> _parseJson(String jsonString) {
    try {
      return Map<String, dynamic>.from(
        (jsonDecode(jsonString) as Map).cast<String, dynamic>(),
      );
    } catch (e) {
      logger.e('Error parsing JSON: $e');
      rethrow;
    }
  }

  /// Get quality metrics from OCR response
  Map<String, dynamic> getQualityMetrics(OCRResponse ocrResponse) {
    return {
      'blur': ocrResponse.quality.blur,
      'blurScore': ocrResponse.quality.blurScore,
      'contrast': ocrResponse.quality.contrast,
      'contrastScore': ocrResponse.quality.contrastScore,
      'skewAngle': ocrResponse.quality.skewAngle,
      'processingTime': ocrResponse.meta.processingTimeMs,
    };
  }
}
