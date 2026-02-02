import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/ocr_response.dart';
import 'api_client.dart';

class OcrService {
  final ApiClient _apiClient;

  OcrService({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient(baseUrl: 'http://localhost:8002');

  Future<OcrResponse> extractTextFromImage(File imageFile) async {
    try {
      final uri = Uri.parse('${_apiClient.baseUrl}/api/v1/ocr/extract');

      final request = http.MultipartRequest('POST', uri)
        ..files.add(await http.MultipartFile.fromPath('file', imageFile.path))
        ..fields['apply_preprocessing'] = 'true'
        ..fields['languages'] = 'khm+eng+fra'
        ..fields['include_low_confidence'] = 'true'
        ..fields['include_stats'] = 'true';

      final streamedResponse = await request.send().timeout(
            const Duration(seconds: 30),
            onTimeout: () => throw Exception('OCR request timed out'),
          );

      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        return OcrResponse.fromJson(jsonData);
      } else {
        return OcrResponse(
          rawText: '',
          error: 'OCR service error: ${response.statusCode} - ${response.body}',
        );
      }
    } on SocketException catch (_) {
      return OcrResponse(
        rawText: '',
        error:
            'Network error: Unable to connect to OCR service. Please check your connection.',
      );
    } on FormatException catch (_) {
      return OcrResponse(
        rawText: '',
        error: 'Invalid response format from OCR service',
      );
    } catch (e) {
      return OcrResponse(rawText: '', error: 'OCR processing error: $e');
    }
  }
}
