import 'dart:io';

class ApiConstants {
  // Use 10.0.2.2 for Android Emulator to access localhost of the host machine.
  // Use 127.0.0.1 for iOS Simulator or Desktop.
  static String get baseUrl {
    if (Platform.isAndroid) {
      return 'http://10.0.2.2';
    }
    return 'http://127.0.0.1';
  }

  // OCR Service (Port 8000)
  static String get ocrBaseUrl => '$baseUrl:8000/api/v1';
  static const String ocrEndpoint = '/ocr';
  static const String ocrHealthEndpoint = '/health';

  // AI Service (Port 8001)
  static String get aiBaseUrl => '$baseUrl:8001/api/v1';
  static const String prescriptionProcessEndpoint = '/prescription/process';
  static const String chatEndpoint = '/chat';

  // Timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 60);
}
