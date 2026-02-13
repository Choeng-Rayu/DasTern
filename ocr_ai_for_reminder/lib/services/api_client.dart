import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:logger/logger.dart';
import '../core/constants/api_constants.dart';

class APIClient {
  final String baseUrl;
  final Logger logger = Logger();

  APIClient({
    String? baseUrl,
  }) : baseUrl = baseUrl ?? ApiConstants.aiBaseUrl;

  /// Upload image for OCR processing
  Future<http.StreamedResponse> uploadImageForOCR(
    String imagePath, {
    String? languages,
    bool skipEnhancement = false,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/ocr');
      final request = http.MultipartRequest('POST', uri);

      // Add file
      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          imagePath,
        ),
      );

      // Add optional parameters
      if (languages != null) {
        request.fields['languages'] = languages;
      }
      request.fields['skip_enhancement'] = skipEnhancement.toString();

      logger.i('Sending OCR request to $baseUrl/api/v1/ocr');
      final response = await request.send();
      return response;
    } catch (e) {
      logger.e('Error uploading image: $e');
      rethrow;
    }
  }

  /// Send raw OCR text for AI correction
  Future<Map<String, dynamic>> correctOCRText(
    String rawText, {
    String language = 'en',
    Map<String, dynamic>? context,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/correct');
      final body = {
        'raw_text': rawText,
        'language': language,
        if (context != null) 'context': context,
      };

      logger.i('Sending OCR correction request');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception(
          'Failed to correct OCR text: ${response.statusCode} - ${response.body}',
        );
      }
    } catch (e) {
      logger.e('Error correcting OCR text: $e');
      rethrow;
    }
  }

  /// Extract medication reminders from OCR data
  Future<Map<String, dynamic>> extractReminders(
    Map<String, dynamic> ocrData,
  ) async {
    try {
      // Use the simpler extract-reminders endpoint (works with main_ollama.py)
      final uri = Uri.parse('$baseUrl/extract-reminders');
      final body = {
        'raw_ocr_json': ocrData,
      };

      logger.i('Sending reminder extraction request to $uri');
      logger.d('OCR data keys: ${ocrData.keys.toList()}');

      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      logger.i('Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        logger.i(
            'Extraction result - Success: ${result['success']}, Medications: ${result['medications']?.length ?? 0}');

        // The /extract-reminders endpoint returns {medications: [...], success: bool}
        return result;
      } else {
        logger.e(
            'Failed to extract reminders: ${response.statusCode} - ${response.body}');
        throw Exception(
          'Failed to extract reminders: ${response.statusCode} - ${response.body}',
        );
      }
    } catch (e) {
      logger.e('Error extracting reminders: $e');
      rethrow;
    }
  }

  /// Health check endpoint
  Future<bool> healthCheck() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await http.get(uri).timeout(
            const Duration(seconds: 5),
            onTimeout: () => http.Response('timeout', 408),
          );
      logger.i('Health check response from $uri: ${response.statusCode}');
      return response.statusCode == 200;
    } catch (e) {
      logger.w('Health check failed: $e');
      return false;
    }
  }

  /// Get service info
  Future<Map<String, dynamic>> getServiceInfo() async {
    try {
      final uri = Uri.parse('$baseUrl/');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get service info: ${response.statusCode}');
      }
    } catch (e) {
      logger.e('Error getting service info: $e');
      rethrow;
    }
  }
}
