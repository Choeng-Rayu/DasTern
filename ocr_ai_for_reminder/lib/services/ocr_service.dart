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
    final uri = Uri.parse('${ApiConstants.ocrBaseUrl}${ApiConstants.ocrEndpoint}');
    
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
}
