import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../components/loading_indicator.dart';
import '../components/result_card.dart';
import '../../providers/app_provider.dart';
import '../../widgets/ocr_text_display.dart';
import 'ai_result_screen.dart';

class OcrResultScreen extends StatelessWidget {
  const OcrResultScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('OCR Results'),
        centerTitle: true,
      ),
      body: Consumer<AppProvider>(
        builder: (context, provider, child) {
          if (provider.isProcessingOcr) {
            return const Center(
              child: LoadingIndicator(
                message: 'Extracting text from image...',
              ),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                ResultCard(
                  title: 'Extracted Text',
                  icon: Icons.text_snippet,
                  content: OcrTextDisplay(
                    text: provider.ocrResponse?.rawText ?? '',
                    confidence: provider.ocrResponse?.confidence ?? 0.0,
                  ),
                ),
                const SizedBox(height: 20),
                if (provider.ocrResponse?.hasError ?? false)
                  _buildErrorCard(
                    context,
                    provider.ocrResponse!.error!,
                    colorScheme,
                  ),
                if (!(provider.ocrResponse?.hasError ?? false)) ...[
                  ElevatedButton.icon(
                    onPressed: provider.isProcessingAi
                        ? null
                        : () async {
                            await provider.processAi();
                            if (context.mounted) {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => const AiResultScreen(),
                                ),
                              );
                            }
                          },
                    icon: provider.isProcessingAi
                        ? SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                colorScheme.onPrimary,
                              ),
                            ),
                          )
                        : const Icon(Icons.smart_toy),
                    label: Text(
                      provider.isProcessingAi
                          ? 'Analyzing with AI...'
                          : 'Analyze with AI',
                    ),
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
                const SizedBox(height: 20),
                OutlinedButton.icon(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('Back to Home'),
                  style: OutlinedButton.styleFrom(
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
              'OCR Error',
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
