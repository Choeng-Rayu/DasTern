import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../components/image_picker_button.dart';
import '../components/result_card.dart';
import '../../providers/app_provider.dart';
import '../../widgets/prescription_image_viewer.dart';
import 'ocr_result_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('OCR AI Reminder'),
        centerTitle: true,
        elevation: 0,
        backgroundColor: colorScheme.surface,
        foregroundColor: colorScheme.onSurface,
      ),
      body: Consumer<AppProvider>(
        builder: (context, provider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildHeader(context, colorScheme),
                const SizedBox(height: 24),
                if (provider.selectedImage != null) ...[
                  PrescriptionImageViewer(
                    imageFile: File(provider.selectedImage!.path),
                  ),
                  const SizedBox(height: 20),
                ],
                ImagePickerButton(
                  onImageSelected: (File file) async {
                    await provider.selectImageFile(file);
                    if (context.mounted) {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const OcrResultScreen(),
                        ),
                      );
                    }
                  },
                  isLoading: provider.isProcessingOcr,
                ),
                if (provider.hasError) ...[
                  const SizedBox(height: 20),
                  _buildErrorCard(
                      context, provider.errorMessage ?? '', colorScheme),
                ],
                const SizedBox(height: 24),
                _buildInstructions(context, colorScheme),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader(BuildContext context, ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            colorScheme.primary,
            colorScheme.primaryContainer,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Icon(
            Icons.document_scanner,
            size: 64,
            color: colorScheme.onPrimary,
          ),
          const SizedBox(height: 16),
          Text(
            'Scan Prescription',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: colorScheme.onPrimary,
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Take a photo or upload an image of your prescription to extract medication reminders',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onPrimary.withOpacity(0.9),
                ),
          ),
        ],
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
        child: Row(
          children: [
            Icon(
              Icons.error_outline,
              color: colorScheme.error,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                error,
                style: TextStyle(
                  color: colorScheme.onErrorContainer,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInstructions(BuildContext context, ColorScheme colorScheme) {
    return ResultCard(
      title: 'How it works',
      icon: Icons.info_outline,
      accentColor: colorScheme.secondary,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildStep(
            context,
            '1',
            'Select or capture an image of your prescription',
            colorScheme,
          ),
          const SizedBox(height: 12),
          _buildStep(
            context,
            '2',
            'OCR extracts the text from the image',
            colorScheme,
          ),
          const SizedBox(height: 12),
          _buildStep(
            context,
            '3',
            'AI analyzes and creates medication reminders',
            colorScheme,
          ),
        ],
      ),
    );
  }

  Widget _buildStep(
    BuildContext context,
    String number,
    String text,
    ColorScheme colorScheme,
  ) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 28,
          height: 28,
          decoration: BoxDecoration(
            color: colorScheme.primary,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              number,
              style: TextStyle(
                color: colorScheme.onPrimary,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            text,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
      ],
    );
  }
}
