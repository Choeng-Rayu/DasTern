import 'package:flutter/material.dart' hide DayPeriod;
import '../models/day_period.dart';
import 'time_chip.dart';

class MedicationShift extends StatelessWidget {
  final DayPeriod period;
  final String backgroundImage;
  final List<String> times;

  const MedicationShift({
    super.key,
    required this.period,
    required this.backgroundImage,
    required this.times,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 150,
      margin: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        image: DecorationImage(
          image: AssetImage(backgroundImage),
          fit: BoxFit.cover,
        ),
      ),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          color: Colors.black.withOpacity(0.35),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              period.label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children:
                  times.map<Widget>((time) => TimeChip(time: time)).toList(),
            ),
          ],
        ),
      ),
    );
  }
}
