import 'package:flutter/material.dart';
import '../models/medication.dart';

class MedicationList extends StatelessWidget {
  final List<Medication> medications;

  const MedicationList({
    Key? key,
    required this.medications,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    if (medications.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Column(
            children: [
              Icon(
                Icons.medication_outlined,
                size: 48,
                color: colorScheme.onSurfaceVariant,
              ),
              const SizedBox(height: 12),
              Text(
                'No medications found',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: medications.length,
      separatorBuilder: (context, index) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final medication = medications[index];
        return _buildMedicationCard(context, medication, colorScheme);
      },
    );
  }

  Widget _buildMedicationCard(
    BuildContext context,
    Medication medication,
    ColorScheme colorScheme,
  ) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: colorScheme.primary.withOpacity(0.2),
            width: 1,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: colorScheme.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      Icons.medication,
                      color: colorScheme.primary,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      medication.name,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                ],
              ),
              if (medication.dosage != null) ...[
                const SizedBox(height: 12),
                _buildInfoRow(
                  context,
                  Icons.straighten,
                  'Dosage: ${medication.dosage}',
                  colorScheme,
                ),
              ],
              if (medication.frequency != null) ...[
                const SizedBox(height: 8),
                _buildInfoRow(
                  context,
                  Icons.schedule,
                  'Frequency: ${medication.frequency}',
                  colorScheme,
                ),
              ],
              if (medication.times != null && medication.times!.isNotEmpty) ...[
                const SizedBox(height: 8),
                _buildInfoRow(
                  context,
                  Icons.access_time,
                  'Times: ${medication.displayTimes}',
                  colorScheme,
                ),
              ],
              if (medication.instructions != null) ...[
                const SizedBox(height: 8),
                _buildInfoRow(
                  context,
                  Icons.notes,
                  'Instructions: ${medication.instructions}',
                  colorScheme,
                ),
              ],
              if (medication.duration != null) ...[
                const SizedBox(height: 8),
                _buildInfoRow(
                  context,
                  Icons.date_range,
                  'Duration: ${medication.duration}',
                  colorScheme,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoRow(
    BuildContext context,
    IconData icon,
    String text,
    ColorScheme colorScheme,
  ) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(
          icon,
          size: 18,
          color: colorScheme.onSurfaceVariant,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
          ),
        ),
      ],
    );
  }
}
