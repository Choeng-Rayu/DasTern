import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import '../data/dtos/ai_response_dto.dart';
import '../utils/app_logger.dart';

class AiService {
  final http.Client _client;

  AiService({http.Client? client}) : _client = client ?? http.Client();

  Future<AiResponseDto> enhancePrescription(Map<String, dynamic> ocrData) async {
    final uri = Uri.parse('${ApiConstants.aiBaseUrl}${ApiConstants.prescriptionProcessEndpoint}');
    
    AppLogger.i('Sending OCR data to AI Service: $uri');

    try {
      final response = await _client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'raw_ocr_json': ocrData,
        }),
      );

      AppLogger.d('AI Service Response: ${response.statusCode}');
      // AppLogger.d('Body: ${response.body}'); // Log body only if needed for debug

      if (response.statusCode == 200) {
        final jsonMap = json.decode(response.body);
        return AiResponseDto.fromJson(jsonMap);
      } else {
        throw Exception('AI Service Error: ${response.statusCode} - ${response.body}');
      }
    } catch (e, stack) {
      AppLogger.e('Failed to enhance prescription', e, stack);
      rethrow;
    }
  }
}
