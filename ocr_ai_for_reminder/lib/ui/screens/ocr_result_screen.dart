import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:io';
import '../../providers/processing_provider.dart';
import '../../widgets/dialogs.dart';
import '../../widgets/custom_widgets.dart';
import '../../widgets/form_widgets.dart';

class OCRResultScreen extends StatefulWidget {
  final String imagePath;

  const OCRResultScreen({
    Key? key,
    required this.imagePath,
  }) : super(key: key);

  @override
  State<OCRResultScreen> createState() => _OCRResultScreenState();
}

class _OCRResultScreenState extends State<OCRResultScreen> {
  @override
  void initState() {
    super.initState();
    // Defer image processing until after the build phase
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _processImage();
    });
  }

  Future<void> _processImage() async {
    final ocrProvider = context.read<OCRProvider>();
    ocrProvider.setImagePath(widget.imagePath);

    final success = await ocrProvider.processImage();

    if (!mounted) return;

    if (!success) {
      showDialog(
        context: context,
        builder: (ctx) => ErrorDialog(
          title: 'OCR Processing Failed',
          message: ocrProvider.processingState.error ?? 'Unknown error occurred',
          onRetry: _processImage,
          onDismiss: () {
            Navigator.pop(context);
          },
        ),
      );
    }
  }

  void _proceedToAI() {
    final ocrProvider = context.read<OCRProvider>();
    final aiProvider = context.read<AIProvider>();

    if (ocrProvider.extractedText != null && ocrProvider.ocrResponse != null) {
      aiProvider.setRawOCRData(
        ocrProvider.extractedText!,
        ocrProvider.ocrResponse!.toJson(),
      );

      Navigator.pushNamed(context, '/ai-result');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('OCR Processing Result'),
        elevation: 0,
        backgroundColor: Colors.blue.shade700,
      ),
      body: Consumer<OCRProvider>(
        builder: (context, ocrProvider, _) {
          if (ocrProvider.processingState.isProcessing) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 16),
                  Text(ocrProvider.processingState.currentStep ?? 'Processing...'),
                  const SizedBox(height: 24),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: LinearProgressIndicator(
                        value: ocrProvider.processingState.progress,
                        minHeight: 6,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }

          if (ocrProvider.processingState.error != null) {
            return Center(
              child: EmptyStateWidget(
                icon: Icons.error_outline,
                title: 'Processing Failed',
                description: ocrProvider.processingState.error ?? 'Unknown error',
                actionLabel: 'Retry',
                onActionPressed: _processImage,
              ),
            );
          }

          if (!ocrProvider.hasOCRData) {
            return const Center(
              child: Text('No OCR data available'),
            );
          }

          return SingleChildScrollView(
            child: Column(
              children: [
                // Image preview
                Container(
                  width: double.infinity,
                  height: 200,
                  margin: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey[300]!),
                    image: DecorationImage(
                      image: FileImage(File(widget.imagePath)),
                      fit: BoxFit.cover,
                    ),
                  ),
                  child: Center(
                    child: Image.file(
                      File(widget.imagePath),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),

                // Extracted text
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Extracted Text',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.grey[100],
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              ocrProvider.extractedText ?? '',
                              style: const TextStyle(fontSize: 13),
                              maxLines: 5,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),

                // Quality metrics
                if (ocrProvider.getQualityMetrics() != null) ...[
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Builder(
                      builder: (context) {
                        final metrics = ocrProvider.getQualityMetrics()!;
                        return QualityMetricsWidget(
                          blur: metrics['blur'] ?? 'unknown',
                          blurScore: (metrics['blurScore'] ?? 0.0) as double,
                          contrast: metrics['contrast'] ?? 'unknown',
                          contrastScore: (metrics['contrastScore'] ?? 0.0) as double,
                          skewAngle: (metrics['skewAngle'] ?? 0.0) as double,
                          processingTime:
                              (metrics['processingTime'] ?? 0.0) as double,
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Action buttons
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      RoundedButton(
                        label: 'Proceed to AI Processing',
                        icon: Icons.psychology,
                        onPressed: _proceedToAI,
                        backgroundColor: Colors.green.shade700,
                      ),
                      const SizedBox(height: 12),
                      RoundedButton(
                        label: 'Back to Home',
                        onPressed: () => Navigator.pop(context),
                        backgroundColor: Colors.grey.shade600,
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
