/// Environment configuration for the application
class Environment {
  // API Configuration
  static const String apiBaseUrl = 'http://localhost:8000';
  static const Duration apiTimeout = Duration(seconds: 30);

  // Feature Flags
  static const bool enableDebugMode = true;
  static const bool enableLogging = true;
  static const bool enableAnalytics = false;

  // Supported Languages
  static const List<String> supportedLanguages = ['eng', 'khm', 'fra'];
  static const String defaultLanguages = 'eng+khm+fra';

  // OCR Configuration
  static const bool skipEnhancementByDefault = false;
  static const int maxImageSize = 10 * 1024 * 1024; // 10 MB

  // Quality Thresholds
  static const double blurThreshold = 100.0;
  static const double contrastThreshold = 10.0;

  // UI Configuration
  static const double defaultBorderRadius = 8.0;
  static const Duration animationDuration = Duration(milliseconds: 300);

  /// Get the appropriate API base URL based on environment
  static String getApiUrl() {
    // You can add environment-specific logic here
    // For example, using --dart-define during build
    return apiBaseUrl;
  }

  /// Check if running in debug mode
  static bool isDebugMode() {
    return enableDebugMode;
  }

  /// Get timeout duration
  static Duration getTimeout() {
    return apiTimeout;
  }
}
