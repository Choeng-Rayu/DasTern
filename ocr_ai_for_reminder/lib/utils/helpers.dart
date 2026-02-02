import 'package:intl/intl.dart';

class DateTimeUtils {
  static String formatDate(DateTime date) {
    return DateFormat('dd/MM/yyyy').format(date);
  }

  static String formatTime(DateTime dateTime) {
    return DateFormat('HH:mm').format(dateTime);
  }

  static String formatDateTime(DateTime dateTime) {
    return DateFormat('dd/MM/yyyy HH:mm').format(dateTime);
  }

  static String formatMedicationDuration(int? days) {
    if (days == null) return 'Not specified';
    if (days == 1) return '1 day';
    return '$days days';
  }

  static String formatTimeList(List<String> times) {
    return times.join(', ');
  }
}

class StringUtils {
  static String capitalize(String text) {
    if (text.isEmpty) return text;
    return '${text[0].toUpperCase()}${text.substring(1).toLowerCase()}';
  }

  static String truncate(String text, int length) {
    if (text.length <= length) return text;
    return '${text.substring(0, length)}...';
  }

  static bool isValidEmail(String email) {
    final emailRegex = RegExp(
      r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
    );
    return emailRegex.hasMatch(email);
  }

  static String removeExtraSpaces(String text) {
    return text.replaceAll(RegExp(r'\s+'), ' ').trim();
  }
}

class ValidationUtils {
  static String? validateNotEmpty(String? value, String fieldName) {
    if (value == null || value.isEmpty) {
      return '$fieldName is required';
    }
    return null;
  }

  static String? validateMedicationName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Medication name is required';
    }
    if (value.length < 2) {
      return 'Medication name must be at least 2 characters';
    }
    return null;
  }

  static String? validateDosage(String? value) {
    if (value == null || value.isEmpty) {
      return 'Dosage is required';
    }
    return null;
  }

  static String? validateDuration(String? value) {
    if (value == null || value.isEmpty) {
      return null; // Optional field
    }
    final duration = int.tryParse(value);
    if (duration == null || duration <= 0) {
      return 'Duration must be a positive number';
    }
    return null;
  }
}

class NumberUtils {
  static String formatConfidence(double confidence) {
    return '${(confidence * 100).toStringAsFixed(1)}%';
  }

  static String formatProcessingTime(double milliseconds) {
    if (milliseconds < 1000) {
      return '${milliseconds.toStringAsFixed(0)}ms';
    }
    final seconds = milliseconds / 1000;
    return '${seconds.toStringAsFixed(2)}s';
  }

  static String formatConfidenceShort(double value) {
    return (value * 100).toStringAsFixed(0);
  }
}
