import 'package:flutter/material.dart';
import 'statistics_card.dart';

class StatisticsRow extends StatelessWidget {
  final String receivedCount;
  final String pendingCount;

  const StatisticsRow({
    Key? key,
    this.receivedCount = '20',
    this.pendingCount = '04',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: StatisticsCard(
              count: receivedCount,
              label: 'អ្នកជំងឺទទួលថ្នាំរួចរាល់',
              icon: Icons.check_circle,
              iconColor: Colors.blue.shade400,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: StatisticsCard(
              count: pendingCount,
              label: 'អ្នកជំងឺមិនទាន់ទទួលថ្នាំ',
              icon: Icons.access_time,
              iconColor: Colors.orange.shade400,
            ),
          ),
        ],
      ),
    );
  }
}
