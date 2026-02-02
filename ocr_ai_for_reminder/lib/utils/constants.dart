class AppConstants {
  static const String appName = 'OCR AI Reminder';
  static const String appVersion = '1.0.0';

  static const int maxImageWidth = 1920;
  static const int maxImageHeight = 1920;
  static const int imageQuality = 85;

  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration connectionTimeout = Duration(seconds: 10);

  static const String ocrEndpoint = '/api/v1/ocr/extract';
  static const String aiEndpoint = '/extract-reminders';

  static const String errorNoImage = 'Please select an image first';
  static const String errorNoConnection = 'No internet connection';
  static const String errorTimeout = 'Request timed out. Please try again.';
  static const String errorUnknown = 'An unknown error occurred';
}
