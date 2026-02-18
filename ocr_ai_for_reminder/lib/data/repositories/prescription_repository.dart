import '../../models/prescription.dart';
import '../../models/medicine.dart';
import '../../models/ocr_response.dart';
import '../../models/ai_response.dart';
import '../../services/ocr_service.dart';
import '../../services/ai_service.dart';
import '../../utils/app_logger.dart';

class PrescriptionRepository {
  final OCRService _ocrService;
  final AIService _aiService;

  PrescriptionRepository({
    required OCRService ocrService,
    required AIService aiService,
  })  : _ocrService = ocrService,
        _aiService = aiService;

  /// Step 1: Send image to OCR service and get raw data
  Future<OCRResponse> scanPrescription(String imagePath) async {
    return await _ocrService.processImage(imagePath);
  }

  /// Step 2: Send OCR data to AI service and get structured prescription
  Future<Prescription> analyzePrescription(OCRResponse ocrData) async {
    try {
      // Use the full pipeline method from AI service
      final aiResponse = await _aiService.processFullPipeline(
        ocrData.fullText,
        {'metadata': ocrData.meta},
      );

      return _mapToDomain(aiResponse);
    } catch (e) {
      AppLogger.e('Repository Analysis Error', e);
      rethrow;
    }
  }

  Prescription _mapToDomain(ReminderResponse response) {
    final meds = response.medications.map((m) {
      // Basic fuzzy matching for the list of times
      final times = m.times;
      final isMorning = times.any((t) => t.toLowerCase().contains('morning'));
      final isAfternoon = times.any((t) =>
          t.toLowerCase().contains('noon') ||
          t.toLowerCase().contains('afternoon'));
      final isEvening = times.any((t) => t.toLowerCase().contains('evening'));
      final isNight = times.any((t) => t.toLowerCase().contains('night'));

      return Medicine(
        name: m.name,
        dosage: m.dosage,
        frequency: m.repeat,
        duration: m.durationDays != null ? '${m.durationDays} days' : null,
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
      date: DateTime.now().toIso8601String(),
      status: response.success ? ProcessStatus.analyzed : ProcessStatus.error,
    );
  }
}
