import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../components/loading_indicator.dart';
import '../components/result_card.dart';
import '../../providers/app_provider.dart';
import '../../widgets/medication_list.dart';

class AiResultScreen extends StatelessWidget {
  const AiResultScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Analysis'),
        centerTitle: true,
      ),
      body: Consumer<AppProvider>(
        builder: (context, provider, child) {
          if (provider.isProcessingAi) {
            return const Center(
              child: LoadingIndicator(
                message: 'AI is analyzing your prescription...',
              ),
            );
          }

          final aiResponse = provider.aiResponse;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (aiResponse?.hasError ?? false)
                  _buildErrorCard(
                    context,
                    aiResponse!.error!,
                    colorScheme,
                  )
                else ...[
                  if (aiResponse?.summary != null) ...[
                    ResultCard(
                      title: 'Summary',
                      icon: Icons.summarize,
                      accentColor: colorScheme.tertiary,
                      content: Text(
                        aiResponse!.summary!,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],
                  ResultCard(
                    title: 'Medications',
                    icon: Icons.medication,
                    accentColor: colorScheme.primary,
                    content: MedicationList(
                      medications: aiResponse?.medications ?? [],
                    ),
                  ),
                  if (aiResponse?.reminders != null &&
                      aiResponse!.reminders!.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    ResultCard(
                      title: 'Reminders',
                      icon: Icons.notifications_active,
                      accentColor: colorScheme.secondary,
                      content: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: aiResponse.reminders!.map((reminder) {
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.check_circle,
                                  size: 20,
                                  color: colorScheme.secondary,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    reminder,
                                    style:
                                        Theme.of(context).textTheme.bodyMedium,
                                  ),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                  ],
                ],
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () {
                    Navigator.popUntil(context, (route) => route.isFirst);
                  },
                  icon: const Icon(Icons.home),
                  label: const Text('Back to Home'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 16,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildErrorCard(
    BuildContext context,
    String error,
    ColorScheme colorScheme,
  ) {
    return Card(
      color: colorScheme.errorContainer,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(
              Icons.error_outline,
              color: colorScheme.error,
              size: 48,
            ),
            const SizedBox(height: 12),
            Text(
              'AI Analysis Error',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: colorScheme.error,
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: colorScheme.onErrorContainer,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
