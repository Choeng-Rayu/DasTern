<<<<<<< HEAD
=======

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

>>>>>>> c04fb50ce3d62100ad607cc395b368e4045989f9
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart'; // Add http_parser to pubspec if needed, usually exported by http or needed separately
import '../core/constants/api_constants.dart';
import '../data/dtos/ocr_response_dto.dart';
import '../utils/app_logger.dart';

class OcrService {
  final http.Client _client;

  OcrService({http.Client? client}) : _client = client ?? http.Client();

  Future<OcrResponseDto> processImage(File imageFile) async {
    final uri = Uri.parse('${ApiConstants.ocrBaseUrl}${ApiConstants.ocrEndpoint}'); // http://192.168.0.164:8006/api/v1/ocr
    
    AppLogger.i('Uploading image to OCR Service: $uri');

    try {
      final request = http.MultipartRequest('POST', uri);
      
      // Attach file
      request.files.add(await http.MultipartFile.fromPath(
        'file',
        imageFile.path,
        contentType: MediaType('image', 'jpeg'), // Adjust based on file type if needed
      ));

      // Optional: Add params
      // request.fields['languages'] = 'eng+khm'; 

      final streamedResponse = await _client.send(request);
      final response = await http.Response.fromStream(streamedResponse);

      AppLogger.d('OCR Service Response: ${response.statusCode}');
      AppLogger.d('Body: ${response.body}');

      if (response.statusCode == 200) {
        final jsonMap = json.decode(response.body);
        return OcrResponseDto.fromJson(jsonMap);
      } else {
        throw Exception('OCR Service Error: ${response.statusCode} - ${response.body}');
      }
    } catch (e, stack) {
      AppLogger.e('Failed to process image', e, stack);
      rethrow;
    }
  }
<<<<<<< HEAD
=======

>>>>>>> c04fb50ce3d62100ad607cc395b368e4045989f9
}
