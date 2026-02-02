class Constants {
  // API Configuration
  static const String apiBaseUrl = 'http://localhost:8000';
  static const Duration apiTimeout = Duration(seconds: 30);

  // OCR Configuration
  static const String defaultLanguages = 'eng+khm+fra';
  static const bool skipEnhancementDefault = false;

  // Languages
  static const Map<String, String> supportedLanguages = {
    'en': 'English',
    'km': 'Khmer',
    'fr': 'French',
  };

  // UI
  static const double borderRadius = 8.0;
  static const double buttonHeight = 50.0;
  static const double cardElevation = 2.0;

  // Error messages
  static const String errorServiceUnavailable =
      'Service is currently unavailable. Please check your connection and try again.';
  static const String errorInvalidImage = 'Invalid image selected.';
  static const String errorProcessingFailed = 'Processing failed. Please try again.';
  static const String errorNoMedications =
      'No medications found in the prescription.';

  // Success messages
  static const String successOCRProcessing = 'OCR processing completed successfully.';
  static const String successAIProcessing = 'Medication extraction completed successfully.';
  static const String successReminderSaved = 'Reminders saved successfully.';
}

class AppConfig {
  static const bool enableDebugLogging = true;
  static const bool enableAnalytics = false;
  static const String appVersion = '1.0.0';
  static const String appName = 'Prescription OCR Scanner';
}
