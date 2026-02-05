import 'dart:io';

class ApiConstants {
  // IMPORTANT: Set this to your computer's local IP when testing on physical device
  // Find it with: ip addr show | grep "inet " (on Linux)
  // For emulator: use '10.0.2.2'
  // For physical device on WiFi: use your computer's IP (e.g., '192.168.0.164')
  static const String hostIpAddress = '192.168.0.164'; // UPDATE THIS FOR YOUR NETWORK
  
  // Ports must match docker-compose.yml
  static const String defaultOcrPort = 
      String.fromEnvironment('OCR_SERVICE_PORT', defaultValue: '8006');
  static const String defaultAiPort =
      String.fromEnvironment('AI_SERVICE_PORT', defaultValue: '8005');

  // Use hostIpAddress for physical device, 10.0.2.2 for emulator, 127.0.0.1 for iOS/Desktop
  static String get baseUrl {
    if (Platform.isAndroid) {
      // Change this to 'http://10.0.2.2' if using emulator
      return 'http://$hostIpAddress';
    }
    return 'http://127.0.0.1';
  }

  // OCR Service (Port configurable)
  static String get ocrBaseUrl => '$baseUrl:$defaultOcrPort/api/v1'; // http://192.168.0.164:8006/api/v1
  static const String ocrEndpoint = '/ocr'; // POST to /ocr to process images
  static const String ocrHealthEndpoint = '/health';

  // AI Service (Port configurable)
  static String get aiBaseUrl => '$baseUrl:$defaultAiPort/api/v1';
  static const String prescriptionProcessEndpoint = '/prescription/process';
  static const String chatEndpoint = '/chat';

  // Timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 60);
}
