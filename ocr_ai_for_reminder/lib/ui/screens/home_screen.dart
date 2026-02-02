import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../providers/processing_provider.dart';
import '../../widgets/dialogs.dart';
import '../../widgets/form_widgets.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ImagePicker _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _checkServiceHealth();
  }

  Future<void> _checkServiceHealth() async {
    final ocrProvider = context.read<OCRProvider>();
    await ocrProvider.checkServiceHealth();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final pickedFile = await _imagePicker.pickImage(
        source: source,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        if (!mounted) return;
        context.read<OCRProvider>().setImagePath(pickedFile.path);

        if (!mounted) return;
        Navigator.pushNamed(context, '/ocr-result', arguments: pickedFile.path);
      }
    } catch (e) {
      if (!mounted) return;
      showDialog(
        context: context,
        builder: (ctx) => ErrorDialog(
          title: 'Error',
          message: 'Failed to pick image: ${e.toString()}',
          onDismiss: () {},
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Prescription OCR Scanner'),
        elevation: 0,
        backgroundColor: Colors.blue.shade700,
        actions: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Consumer<OCRProvider>(
              builder: (context, ocrProvider, _) {
                return Center(
                  child: Tooltip(
                    message: ocrProvider.isServiceHealthy
                        ? 'Service is online'
                        : 'Service is offline',
                    child: Chip(
                      label: Text(
                        ocrProvider.isServiceHealthy ? 'Online' : 'Offline',
                        style: const TextStyle(color: Colors.white),
                      ),
                      backgroundColor: ocrProvider.isServiceHealthy
                          ? Colors.green
                          : Colors.red,
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Header banner
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.blue.shade700, Colors.blue.shade500],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.document_scanner,
                    size: 64,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Scan Your Prescription',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Extract medication information and set reminders',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white70,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),

            // Main content
            Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'How to use:',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  const StepCard(
                    stepNumber: '1',
                    title: 'Capture or Select',
                    description:
                        'Take a photo of your prescription or select from gallery',
                    icon: Icons.photo_camera,
                  ),
                  const SizedBox(height: 12),
                  const StepCard(
                    stepNumber: '2',
                    title: 'OCR Processing',
                    description:
                        'Our AI will scan and extract all text from the image',
                    icon: Icons.psychology,
                  ),
                  const SizedBox(height: 12),
                  const StepCard(
                    stepNumber: '3',
                    title: 'Extract Medications',
                    description:
                        'Get structured medication information and set reminders',
                    icon: Icons.medication,
                  ),
                  const SizedBox(height: 32),
                  RoundedButton(
                    label: 'Take Photo',
                    icon: Icons.camera_alt,
                    onPressed: () => _pickImage(ImageSource.camera),
                    backgroundColor: Colors.blue.shade700,
                  ),
                  const SizedBox(height: 12),
                  RoundedButton(
                    label: 'Choose from Gallery',
                    icon: Icons.image,
                    onPressed: () => _pickImage(ImageSource.gallery),
                    backgroundColor: Colors.blue.shade600,
                  ),
                  const SizedBox(height: 24),
                  // Feature highlights
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.blue.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Supported Languages:',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 8,
                          children: const [
                            Chip(label: Text('English')),
                            Chip(label: Text('Khmer')),
                            Chip(label: Text('French')),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class StepCard extends StatelessWidget {
  final String stepNumber;
  final String title;
  final String description;
  final IconData icon;

  const StepCard({
    Key? key,
    required this.stepNumber,
    required this.title,
    required this.description,
    required this.icon,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: Colors.blue.shade700,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Center(
            child: Text(
              stepNumber,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
