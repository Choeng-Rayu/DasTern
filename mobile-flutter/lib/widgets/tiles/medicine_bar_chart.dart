import 'package:flutter/material.dart';

class MedicineBarChart extends StatelessWidget {
  final List<Map<String, dynamic>> data;

  const MedicineBarChart({
    Key? key,
    required this.data,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: data.map((item) {
        return Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Container(
                  width: 12,
                  height: (item['received'] as int) * 15.0,
                  decoration: BoxDecoration(
                    color: Colors.blue.shade400,
                    borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(4),
                    ),
                  ),
                ),
                const SizedBox(width: 4),
                Container(
                  width: 12,
                  height: (item['missed'] as int) * 15.0,
                  decoration: BoxDecoration(
                    color: Colors.red.shade400,
                    borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(4),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              item['day'] as String,
              style: TextStyle(
                fontSize: 10,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        );
      }).toList(),
    );
  }
}
