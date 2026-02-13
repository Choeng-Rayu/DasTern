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

  /// Extract medication reminders from OCR data
  Future<ReminderResponse> extractReminders(
    Map<String, dynamic> ocrData,
  ) async {
    try {
      logger.i('Extracting medication reminders from OCR data');

      final result = await apiClient.extractReminders(ocrData);

      return ReminderResponse.fromJson(result);
    } catch (e) {
      logger.e('Error extracting reminders: $e');
      rethrow;
    }
  }

  /// Complete pipeline: OCR -> Correction -> Reminder Extraction
  Future<ReminderResponse> processFullPipeline(
    String rawOCRText,
    Map<String, dynamic> ocrMetadata, {
    String language = 'en',
  }) async {
    try {
      logger.i('Processing full pipeline: OCR -> AI -> Reminders');

      // Step 1: Correct OCR text
      final correctedResult = await correctOCRText(
        rawOCRText,
        language: language,
        context: ocrMetadata,
      );

      logger.i('Text corrected, confidence: ${correctedResult.confidence}');

      // Step 2: Extract reminders from corrected text
      final ocrDataWithCorrectedText = {
        ...ocrMetadata,
        'full_text': correctedResult.correctedText,
      };

      final reminders = await extractReminders(ocrDataWithCorrectedText);

      logger.i(
        'Extraction complete: ${reminders.medications.length} medications found',
      );

      return reminders;
    } catch (e) {
      logger.e('Error in full pipeline: $e');
      rethrow;
    }
  }

  /// Parse medication list from raw text
  List<MedicationInfo> parseMedicationsFromText(String text) {
    try {
      // This is a helper method for manual parsing if needed
      logger.i('Parsing medications from text');
      // Implementation would depend on text format
      return [];
    } catch (e) {
      logger.e('Error parsing medications: $e');
      rethrow;
    }
  }

  /// Format reminders for display
  List<String> formatReminders(ReminderResponse response) {
    try {
      return response.medications.map((med) {
        return '''
${med.name}
Dosage: ${med.dosage}
Times: ${med.times.join(', ')}
Repeat: ${med.repeat}
Duration: ${med.durationDays ?? 'Not specified'} days
Notes: ${med.notes}
        ''';
      }).toList();
    } catch (e) {
      logger.e('Error formatting reminders: $e');
      return [];
    }
  }
}
