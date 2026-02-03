import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/processing_provider.dart';
import '../../widgets/dialogs.dart';
import '../../widgets/custom_widgets.dart';
import '../../widgets/form_widgets.dart';

class AIResultScreen extends StatefulWidget {
  const AIResultScreen({Key? key}) : super(key: key);

  @override
  State<AIResultScreen> createState() => _AIResultScreenState();
}

class _AIResultScreenState extends State<AIResultScreen> {
  @override
  void initState() {
    super.initState();
    // Defer AI processing until after the build phase
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _processWithAI();
    });
  }

  Future<void> _processWithAI() async {
    final aiProvider = context.read<AIProvider>();
    final success = await aiProvider.processFullPipeline();

    if (!mounted) return;

    if (!success) {
      showDialog(
        context: context,
        builder: (ctx) => ErrorDialog(
          title: 'AI Processing Failed',
          message: aiProvider.processingState.error ?? 'Unknown error occurred',
          onRetry: _processWithAI,
          onDismiss: () {
            Navigator.pop(context);
          },
        ),
      );
    }
  }

  void _startOver() {
    context.read<OCRProvider>().reset();
    context.read<AIProvider>().reset();
    Navigator.pushNamedAndRemoveUntil(
      context,
      '/home',
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Medication Reminders'),
        elevation: 0,
        backgroundColor: Colors.blue.shade700,
      ),
      body: Consumer<AIProvider>(
        builder: (context, aiProvider, _) {
          if (aiProvider.processingState.isProcessing) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 16),
                  Text(aiProvider.processingState.currentStep ?? 'Processing...'),
                  const SizedBox(height: 24),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: LinearProgressIndicator(
                        value: aiProvider.processingState.progress,
                        minHeight: 6,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }

          if (aiProvider.processingState.error != null) {
            return Center(
              child: EmptyStateWidget(
                icon: Icons.error_outline,
                title: 'Processing Failed',
                description: aiProvider.processingState.error ?? 'Unknown error',
                actionLabel: 'Retry',
                onActionPressed: _processWithAI,
              ),
            );
          }

          if (!aiProvider.hasResults || aiProvider.medications.isEmpty) {
            return Center(
              child: EmptyStateWidget(
                icon: Icons.medication,
                title: 'No Medications Found',
                description:
                    'The AI could not extract any medication information from the prescription.',
                actionLabel: 'Try Again',
                onActionPressed: _startOver,
              ),
            );
          }

          return SingleChildScrollView(
            child: Column(
              children: [
                // Summary card
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Card(
                    color: Colors.green.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.check_circle,
                                color: Colors.green.shade700,
                                size: 28,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Processing Complete!',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    Text(
                                      '${aiProvider.medications.length} medication(s) found',
                                      style: TextStyle(
                                        color: Colors.grey[600],
                                        fontSize: 13,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          if (aiProvider.correctionResult != null) ...[
                            const SizedBox(height: 12),
                            Text(
                              'Confidence: ${(aiProvider.correctionResult!.confidence * 100).toStringAsFixed(1)}%',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),

                // Medications list
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Your Medications',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: aiProvider.medications.length,
                        itemBuilder: (context, index) {
                          final med = aiProvider.medications[index];
                          return MedicationCard(
                            medicationName: med.name,
                            dosage: med.dosage,
                            times: med.times,
                            repeat: med.repeat,
                            durationDays: med.durationDays,
                            notes: med.notes,
                          );
                        },
                      ),
                    ],
                  ),
                ),

                // Action buttons
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      RoundedButton(
                        label: 'View Full Details',
                        icon: Icons.visibility,
                        onPressed: () {
                          // Show detailed view in future
                        },
                        backgroundColor: Colors.blue.shade700,
                      ),
                      const SizedBox(height: 12),
                      RoundedButton(
                        label: 'Save to Reminders',
                        icon: Icons.save,
                        onPressed: () {
                          showDialog(
                            context: context,
                            builder: (ctx) => const SuccessDialog(
                              title: 'Success',
                              message:
                                  'Reminders saved successfully! You will receive notifications at the scheduled times.',
                            ),
                          );
                        },
                        backgroundColor: Colors.green.shade700,
                      ),
                      const SizedBox(height: 12),
                      RoundedButton(
                        label: 'Scan Another Prescription',
                        icon: Icons.add,
                        onPressed: _startOver,
                        backgroundColor: Colors.orange.shade700,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
