import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/ai_response.dart';
import '../models/ocr_response.dart';
import 'api_client.dart';

class AiService {
  final ApiClient _apiClient;

  AiService({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient(baseUrl: 'http://localhost:8001');

  Future<AiResponse> extractReminders(OcrResponse ocrResponse) async {
    try {
      if (ocrResponse.hasError || !ocrResponse.hasData) {
        return AiResponse(
          medications: [],
          error: 'Cannot process: OCR had errors or no data found',
        );
      }

      final uri = Uri.parse('${_apiClient.baseUrl}/extract-reminders');

      // Prepare the request body according to ReminderRequest schema
      final requestBody = ocrResponse.toAiRequestJson();

      print('Sending to AI service: ${jsonEncode(requestBody)}');

      final response = await http
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            body: jsonEncode(requestBody),
          )
          .timeout(
            const Duration(seconds: 120), // 2 minutes for LLM processing
            onTimeout: () =>
                throw Exception('AI service request timed out after 120s'),
          );

      print('AI service response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        return AiResponse.fromJson(jsonData);
      } else {
        return AiResponse(
          medications: [],
          error: 'AI service error: ${response.statusCode} - ${response.body}',
        );
      }
    } on SocketException catch (_) {
      return AiResponse(
        medications: [],
        error:
            'Network error: Unable to connect to AI service at localhost:8001. Please check if the service is running.',
      );
    } on FormatException catch (_) {
      return AiResponse(
        medications: [],
        error: 'Invalid response format from AI service',
      );
    } catch (e) {
      return AiResponse(
        medications: [],
        error: 'AI processing error: $e',
      );
    }
  }

  // Alternative endpoint for simple OCR correction
  Future<AiResponse> correctOcrText(String rawText) async {
    try {
      final uri = Uri.parse('${_apiClient.baseUrl}/correct-ocr');

      final response = await http
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            body: jsonEncode({
              'text': rawText,
              'language': 'en',
            }),
          )
          .timeout(
            const Duration(seconds: 30),
            onTimeout: () => throw Exception('AI service request timed out'),
          );

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        // Wrap in AiResponse format
        return AiResponse(
          medications: [],
          summary: jsonData['corrected_text'] ?? '',
          reminders: [jsonData['corrected_text'] ?? ''],
        );
      } else {
        return AiResponse(
          medications: [],
          error:
              'AI correction error: ${response.statusCode} - ${response.body}',
        );
      }
    } catch (e) {
      return AiResponse(
        medications: [],
        error: 'AI correction error: $e',
      );
    }
  }
}
