import 'package:flutter/material.dart';
import 'box_card.dart';
import 'medicine_bar_chart.dart';

class ChartSection extends StatelessWidget {
  final List<Map<String, dynamic>> chartData;
  final VoidCallback? onDayTap;
  final VoidCallback? onMonthTap;

  const ChartSection({
    Key? key,
    required this.chartData,
    this.onDayTap,
    this.onMonthTap,
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
              const Text(
                'ក្រាបទិន្នន័យ',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Row(
                children: [
                  TextButton(
                    onPressed: onDayTap ?? () {},
                    child: Text(
                      'ថ្ងៃ',
                      style: TextStyle(color: Colors.grey.shade400),
                    ),
                  ),
                  TextButton(
                    onPressed: onMonthTap ?? () {},
                    child: Text(
                      'ខែ',
                      style: TextStyle(color: Colors.grey.shade400),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Row(
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: Colors.blue.shade400,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 4),
                  const Text('បានទទួល', style: TextStyle(fontSize: 12)),
                ],
              ),
              const SizedBox(width: 16),
              Row(
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: Colors.red.shade400,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 4),
                  const Text('មិនបានទទួល', style: TextStyle(fontSize: 12)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 150,
            child: MedicineBarChart(data: chartData),
          ),
        ],
      ),
    );
  }
}
