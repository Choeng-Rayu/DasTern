import 'day_period.dart';

class MedicationScheduleModel {
  final DayPeriod period;
  final List<String> times;
  final String backgroundImage;

  MedicationScheduleModel({
    required this.period,
    required this.times,
    required this.backgroundImage,
  });
}
