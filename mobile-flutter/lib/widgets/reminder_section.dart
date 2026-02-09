import 'package:flutter/material.dart';
import 'box_card.dart';
import 'reminder_item.dart';

class ReminderSection extends StatelessWidget {
  final List<Map<String, String>> reminders;

  const ReminderSection({
    Key? key,
    required this.reminders,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BoxCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(Icons.warning, color: Colors.red.shade400),
                  const SizedBox(width: 8),
                  const Text(
                    'សារដំណឹងថ្មីៗ',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${reminders.length} 4 ដំណឹង',
                  style: TextStyle(
                    color: Colors.red.shade400,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...reminders.map((reminder) => ReminderItem(
                name: reminder['name']!,
                description: reminder['description']!,
                time: reminder['time']!,
              )),
        ],
      ),
    );
  }
}
