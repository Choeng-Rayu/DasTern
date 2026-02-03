import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import '../../providers/processing_provider.dart';
import '../../models/medication.dart';

class AIEnhancedPreviewScreen extends StatelessWidget {
  const AIEnhancedPreviewScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Enhanced Preview'),
        elevation: 0,
        backgroundColor: Colors.green.shade700,
      ),
      body: Consumer<AIProvider>(
        builder: (context, aiProvider, _) {
          if (aiProvider.processingState.isProcessing) {
            return _buildProcessingView(aiProvider);
          }

          if (aiProvider.processingState.error != null) {
            return _buildErrorView(context, aiProvider);
          }

          if (aiProvider.medications.isEmpty) {
            return _buildEmptyView(context);
          }

          return _buildEnhancedView(context, aiProvider);
        },
      ),
    );
  }

  Widget _buildProcessingView(AIProvider aiProvider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 24),
          Text(
            aiProvider.processingState.currentStep ?? 'Processing with AI...',
            style: const TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 48),
            child: LinearProgressIndicator(
              value: aiProvider.processingState.progress,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'This may take a few minutes for complex prescriptions',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView(BuildContext context, AIProvider aiProvider) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
            const SizedBox(height: 16),
            Text(
              'AI Processing Failed',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.red.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              aiProvider.processingState.error ?? 'Unknown error',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              onPressed: () {
                // Trigger reprocessing
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyView(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.medication_outlined,
                size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            const Text(
              'No Medications Found',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'The AI could not extract any medication information from the prescription.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEnhancedView(BuildContext context, AIProvider aiProvider) {
    return Column(
      children: [
        // Success Banner
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          color: Colors.green.shade50,
          child: Row(
            children: [
              Icon(Icons.check_circle, color: Colors.green.shade700),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI Enhancement Complete',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.green.shade700,
                      ),
                    ),
                    Text(
                      '${aiProvider.medications.length} medications extracted',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.green.shade600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // Tabs
        Expanded(
          child: DefaultTabController(
            length: 2,
            child: Column(
              children: [
                TabBar(
                  labelColor: Colors.green.shade700,
                  tabs: const [
                    Tab(text: 'Medications', icon: Icon(Icons.medication)),
                    Tab(text: 'Raw Data', icon: Icon(Icons.code)),
                  ],
                ),
                Expanded(
                  child: TabBarView(
                    children: [
                      _buildMedicationsTab(aiProvider),
                      _buildRawDataTab(aiProvider),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),

        // Action Button
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
          child: Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('Back to OCR'),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                flex: 2,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.edit),
                  label: const Text('Edit & Finalize'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green.shade700,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  onPressed: () {
                    Navigator.pushNamed(
                      context,
                      '/edit-prescription',
                      arguments: aiProvider.medications,
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMedicationsTab(AIProvider aiProvider) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: aiProvider.medications.length,
      itemBuilder: (context, index) {
        final medication = aiProvider.medications[index];
        return _buildMedicationCard(medication, index);
      },
    );
  }

  Widget _buildMedicationCard(MedicationInfo medication, int index) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '#${index + 1}',
                    style: TextStyle(
                      color: Colors.green.shade700,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    medication.name,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            _buildInfoRow(Icons.medication_liquid, 'Dosage', medication.dosage),
            _buildInfoRow(Icons.schedule, 'Times', medication.times.join(', ')),
            _buildInfoRow(Icons.repeat, 'Frequency', medication.repeat),
            if (medication.durationDays != null)
              _buildInfoRow(Icons.calendar_today, 'Duration',
                  '${medication.durationDays} days'),
            if (medication.notes.isNotEmpty)
              _buildInfoRow(Icons.note, 'Notes', medication.notes),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18, color: Colors.grey.shade600),
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
      ),
    );
  }

  Widget _buildRawDataTab(AIProvider aiProvider) {
    final jsonString = const JsonEncoder.withIndent('  ').convert({
      'medications': aiProvider.medications
          .map((m) => {
                'name': m.name,
                'dosage': m.dosage,
                'times': m.times,
                'repeat': m.repeat,
                'duration_days': m.durationDays,
                'notes': m.notes,
              })
          .toList(),
      'metadata': aiProvider.reminderResponse?.metadata,
    });

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey.shade900,
          borderRadius: BorderRadius.circular(8),
        ),
        child: SelectableText(
          jsonString,
          style: const TextStyle(
            fontSize: 12,
            fontFamily: 'monospace',
            color: Colors.greenAccent,
          ),
        ),
      ),
    );
  }
}
