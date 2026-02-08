import 'dart:io';
import '../dtos/ocr_response_dto.dart';
import '../dtos/ai_response_dto.dart';
import '../../models/prescription.dart';
import '../../models/medicine.dart';
import '../../services/ocr_service.dart';
import '../../services/ai_service.dart';
import '../../utils/app_logger.dart';

class PrescriptionRepository {
  final OcrService _ocrService;
  final AiService _aiService;

  PrescriptionRepository({
    OcrService? ocrService,
    AiService? aiService,
  })  : _ocrService = ocrService ?? OcrService(),
        _aiService = aiService ?? AiService();

  /// Step 1: Send image to OCR service and get raw data
  Future<OcrResponseDto> scanPrescription(File imageFile) async {
    return await _ocrService.processImage(imageFile);
  }

  /// Step 2: Send OCR data to AI service and get structured prescription
  Future<Prescription> analyzePrescription(OcrResponseDto ocrData) async {
    try {
      // Convert DTO to Map for AI Service (it expects raw json structure)
      // We'll rely on json_serializable or manual conversion if needed, 
      // but here we can re-serialize the DTO.
      final ocrJson = ocrData.toJson();
      
      final aiResponse = await _aiService.enhancePrescription(ocrJson);

      if (aiResponse.success) {
        return _mapToDomain(aiResponse);
      } else {
        throw Exception(aiResponse.error ?? 'AI Analysis failed');
      }
    } catch (e) {
      AppLogger.e('Repository Analysis Error', e);
      rethrow;
    }
  }

  Prescription _mapToDomain(AiResponseDto dto) {
    if (dto.medications == null) {
      return Prescription(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        medications: [],
        status: ProcessStatus.error,
      );
    }

    final meds = dto.medications!.map((m) {
      final times = m.times ?? [];
      // Basic fuzzy matching for the list of times
      final isMorning = times.any((t) => t.toLowerCase().contains('morning'));
      final isAfternoon = times.any((t) => t.toLowerCase().contains('noon') || t.toLowerCase().contains('afternoon'));
      final isEvening = times.any((t) => t.toLowerCase().contains('evening'));
      final isNight = times.any((t) => t.toLowerCase().contains('night'));

      return Medicine(
        name: m.name,
        dosage: m.dosage,
        frequency: m.repeat ?? 'Daily', // Default or map from Repeat
        duration: null, // API doesn't seem to return duration string formatted, assume part of notes or repeat
        instructions: m.notes,
        isMorning: isMorning,
        isAfternoon: isAfternoon,
        isEvening: isEvening,
        isNight: isNight,
      );
    }).toList();

    return Prescription(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      medications: meds,
      patientName: dto.patientInfo?['name'],
      date: dto.medicalInfo?['date'] ?? DateTime.now().toIso8601String(),
      status: ProcessStatus.analyzed,
    );
  }
}
