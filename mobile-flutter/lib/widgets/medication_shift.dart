import 'package:flutter/material.dart' hide DayPeriod;
import '../models/day_period.dart';
import 'scedule_widget.dart';

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

  static const double cardWidth = 280;
  static const double cardHeight = 140;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: cardWidth,
      height: cardHeight,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Background Image
            Image.asset(
              backgroundImage,
              fit: BoxFit.cover,
            ),

            // Dark overlay for readability (optional but recommended)
            Container(
              color: Colors.black.withOpacity(0.25),
            ),

            // Content
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    period.label,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children:
                        times.map((time) => TimeChip(time: time)).toList(),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
