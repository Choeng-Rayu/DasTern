import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../../models/prescription.dart';
import '../../../providers/scan_provider.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/loading_overlay.dart';
import '../preview/preview_view.dart';

class ScanView extends StatefulWidget {
  const ScanView({super.key});

  @override
  State<ScanView> createState() => _ScanViewState();
}

class _ScanViewState extends State<ScanView> {
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    final XFile? image = await _picker.pickImage(source: source);
    if (image != null) {
      if (!mounted) return;
      context.read<ScanProvider>().setImage(File(image.path));
    }
  }

  void _processImage() {
    final provider = context.read<ScanProvider>();
    provider.processPrescription().then((_) {
      if (mounted && provider.status == ProcessStatus.analyzed) {
         Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const PreviewView()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ScanProvider>(
      builder: (context, provider, child) {
        return LoadingOverlay(
          isLoading: provider.isLoading,
          message: provider.statusMessage,
          child: Scaffold(
            appBar: AppBar(
              title: const Text('Scan Prescription'),
            ),
            body: Column(
              children: [
                Expanded(
                  child: Container(
                    width: double.infinity,
                    margin: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: provider.imageFile != null
                        ? ClipRRect(
                            borderRadius: BorderRadius.circular(16),
                            child: Image.file(
                              provider.imageFile!,
                              fit: BoxFit.contain,
                            ),
                          )
                        : Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.add_a_photo,
                                size: 64,
                                color: Colors.grey.shade400,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'Tap below to capture or upload',
                                style: TextStyle(
                                  color: Colors.grey.shade600,
                                  fontSize: 16,
                                ),
                              ),
                            ],
                          ),
                  ),
                ),
                if (provider.errorMessage != null)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red.shade200),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline, color: Colors.red),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              provider.errorMessage!,
                              style: const TextStyle(color: Colors.red),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: CustomButton(
                              text: 'Camera',
                              icon: Icons.camera_alt,
                              isOutlined: true,
                              onPressed: () => _pickImage(ImageSource.camera),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: CustomButton(
                              text: 'Gallery',
                              icon: Icons.photo_library,
                              isOutlined: true,
                              onPressed: () => _pickImage(ImageSource.gallery),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: CustomButton(
                          text: 'Scan Now',
                          icon: Icons.document_scanner,
                          onPressed: provider.imageFile != null
                              ? _processImage
                              : null,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
