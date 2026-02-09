import 'package:flutter/material.dart';
import '../../models/medication.dart';
import '../../data/prescription_storage.dart';

class FinalPreviewScreen extends StatelessWidget {
  final List<MedicationInfo>? medications;

  const FinalPreviewScreen({
    Key? key,
    this.medications,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final meds = medications ??
        (ModalRoute.of(context)?.settings.arguments as List<MedicationInfo>?) ??
        [];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Final Preview'),
        elevation: 0,
        backgroundColor: Colors.indigo.shade700,
      ),
      body: Column(
        children: [
          // Success Banner
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.indigo.shade700, Colors.indigo.shade500],
              ),
            ),
            child: Column(
              children: [
                const Icon(
                  Icons.check_circle_outline,
                  color: Colors.white,
                  size: 48,
                ),
                const SizedBox(height: 8),
                const Text(
                  'Prescription Ready',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${meds.length} medications processed',
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),

          // Medication List
          Expanded(
            child: meds.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: meds.length,
                    itemBuilder: (context, index) {
                      return _buildMedicationSummaryCard(meds[index], index);
                    },
                  ),
          ),

          // Action Buttons
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        icon: const Icon(Icons.edit),
                        label: const Text('Edit Again'),
                        onPressed: () {
                          Navigator.pop(context);
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      flex: 2,
                      child: ElevatedButton.icon(
                        icon: const Icon(Icons.save),
                        label: const Text('Save Prescription'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.indigo.shade700,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        onPressed: () => _savePrescription(context, meds),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                TextButton.icon(
                  icon: const Icon(Icons.home),
                  label: const Text('Start Over'),
                  onPressed: () {
                    Navigator.pushNamedAndRemoveUntil(
                      context,
                      '/home',
                      (route) => false,
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.medication_outlined, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('No Medications',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Text('No medications to save', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildMedicationSummaryCard(MedicationInfo medication, int index) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.indigo.shade50,
              Colors.white,
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.indigo.shade100,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '${index + 1}',
                      style: TextStyle(
                        color: Colors.indigo.shade700,
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          medication.name,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          medication.dosage,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    Icons.check_circle,
                    color: Colors.green.shade500,
                  ),
                ],
              ),
              const Divider(height: 24),

              // Details
              _buildDetailRow(
                Icons.access_time,
                'Times',
                medication.times.isEmpty
                    ? 'Not specified'
                    : medication.times.join(', '),
                Colors.blue,
              ),
              const SizedBox(height: 8),
              _buildDetailRow(
                Icons.repeat,
                'Frequency',
                medication.repeat,
                Colors.purple,
              ),
              if (medication.durationDays != null) ...[
                const SizedBox(height: 8),
                _buildDetailRow(
                  Icons.calendar_today,
                  'Duration',
                  '${medication.durationDays} days',
                  Colors.orange,
                ),
              ],
              if (medication.notes.isNotEmpty) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.info_outline,
                        size: 16,
                        color: Colors.grey.shade600,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          medication.notes,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey.shade700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(
      IconData icon, String label, String value, Color color) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Icon(icon, size: 16, color: color),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Future<void> _savePrescription(
      BuildContext context, List<MedicationInfo> medications) async {
    // Save to storage
    final storage = PrescriptionStorage();
    final prescription = PrescriptionData(
      id: PrescriptionData.generateId(),
      createdAt: DateTime.now(),
      medications: medications,
      patientName: null, // Can be extracted from OCR if available
      patientAge: null,
      diagnosis: null,
      rawOcrData: null,
      aiMetadata: null,
    );

    try {
      await storage.savePrescription(prescription);
      
      // Show success dialog
      if (!context.mounted) return;
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
          title: Row(
            children: [
              Icon(Icons.check_circle, color: Colors.green.shade500),
              const SizedBox(width: 12),
              const Text('Saved Successfully'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Your prescription has been saved successfully.'),
              const SizedBox(height: 16),
              Text(
                '${medications.length} medications',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Reminders will be created based on your medication schedule.',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(ctx);
                Navigator.pushNamedAndRemoveUntil(
                  context,
                  '/home',
                  (route) => false,
                );
              },
              child: const Text('Done'),
            ),
          ],
        ),
      );
    } catch (e) {
      // Show error dialog
      if (!context.mounted) return;
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Row(
            children: [
              Icon(Icons.error, color: Colors.red.shade500),
              const SizedBox(width: 12),
              const Text('Save Failed'),
            ],
          ),
          content: Text('Failed to save prescription: $e'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }
}
