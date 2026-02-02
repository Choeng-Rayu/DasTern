import 'package:flutter/material.dart';

class MedicationCard extends StatelessWidget {
  final String medicationName;
  final String dosage;
  final List<String> times;
  final String repeat;
  final int? durationDays;
  final String notes;
  final VoidCallback? onTap;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const MedicationCard({
    Key? key,
    required this.medicationName,
    required this.dosage,
    required this.times,
    required this.repeat,
    this.durationDays,
    required this.notes,
    this.onTap,
    this.onEdit,
    this.onDelete,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          medicationName,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          dosage,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  PopupMenuButton(
                    itemBuilder: (context) => [
                      PopupMenuItem(
                        child: const Text('Edit'),
                        onTap: onEdit,
                      ),
                      PopupMenuItem(
                        child: const Text('Delete'),
                        onTap: onDelete,
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                children: times
                    .map(
                      (time) => Chip(
                        label: Text(time),
                        backgroundColor: Colors.blue[100],
                        labelStyle: TextStyle(color: Colors.blue[900]),
                        avatar: const Icon(Icons.access_time),
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.repeat, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text('$repeat', style: TextStyle(color: Colors.grey[600])),
                  if (durationDays != null) ...[
                    const SizedBox(width: 16),
                    Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 4),
                    Text('$durationDays days', style: TextStyle(color: Colors.grey[600])),
                  ],
                ],
              ),
              if (notes.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  'Notes: $notes',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[500],
                    fontStyle: FontStyle.italic,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class QualityMetricsWidget extends StatelessWidget {
  final String blur;
  final double blurScore;
  final String contrast;
  final double contrastScore;
  final double skewAngle;
  final double processingTime;

  const QualityMetricsWidget({
    Key? key,
    required this.blur,
    required this.blurScore,
    required this.contrast,
    required this.contrastScore,
    required this.skewAngle,
    required this.processingTime,
  }) : super(key: key);

  Color _getQualityColor(String quality) {
    switch (quality.toLowerCase()) {
      case 'low':
        return Colors.red;
      case 'medium':
      case 'ok':
        return Colors.orange;
      case 'high':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Image Quality Metrics',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _MetricRow(
              label: 'Blur Level',
              value: blur,
              color: _getQualityColor(blur),
            ),
            _MetricRow(
              label: 'Blur Score',
              value: blurScore.toStringAsFixed(2),
              color: Colors.blue,
            ),
            _MetricRow(
              label: 'Contrast Level',
              value: contrast,
              color: _getQualityColor(contrast),
            ),
            _MetricRow(
              label: 'Contrast Score',
              value: contrastScore.toStringAsFixed(2),
              color: Colors.blue,
            ),
            _MetricRow(
              label: 'Skew Angle',
              value: '${skewAngle.toStringAsFixed(2)}°',
              color: Colors.blue,
            ),
            _MetricRow(
              label: 'Processing Time',
              value: '${processingTime.toStringAsFixed(0)}ms',
              color: Colors.blue,
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricRow extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _MetricRow({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 14)),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              value,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
