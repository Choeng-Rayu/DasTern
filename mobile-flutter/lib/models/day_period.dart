import 'package:flutter/material.dart';

enum DayPeriod {
  morning,
  afternoon,
  night,
}

extension DayPeriodExtension on DayPeriod {
  /// Human-readable text
  String get label {
    switch (this) {
      case DayPeriod.morning:
        return 'Morning';
      case DayPeriod.afternoon:
        return 'Afternoon';
      case DayPeriod.night:
        return 'Night';
    }
  }

  /// Value saved to database / API
  String get dbValue {
    switch (this) {
      case DayPeriod.morning:
        return 'morning';
      case DayPeriod.afternoon:
        return 'afternoon';
      case DayPeriod.night:
        return 'night';
    }
  }

  /// Validation rules (business logic)
  bool isValidHour(int hour) {
    switch (this) {
      case DayPeriod.morning:
        return hour >= 5 && hour < 12;
      case DayPeriod.afternoon:
        return hour >= 12 && hour < 18;
      case DayPeriod.night:
        return hour >= 18 || hour < 5;
    }
  }
}
