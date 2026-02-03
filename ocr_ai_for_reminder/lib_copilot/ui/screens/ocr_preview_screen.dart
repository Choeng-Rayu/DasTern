import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import '../../models/ocr_response.dart';
import '../../providers/processing_provider.dart';

class OCRPreviewScreen extends StatelessWidget {
  const OCRPreviewScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final ocrProvider = context.watch<OCRProvider>();
    final ocrResponse = ocrProvider.ocrResponse;

    if (ocrResponse == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('OCR Preview'),
        ),
        body: const Center(
          child: Text('No OCR data available'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Raw OCR Preview'),
        elevation: 0,
        backgroundColor: Colors.blue.shade700,
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () => _showOCRInfo(context, ocrResponse),
          ),
        ],
      ),
      body: Column(
        children: [
          // Stats Card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            margin: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.blue.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'OCR Statistics',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                _buildStatRow('Blocks', '${ocrResponse.blocks?.length ?? 0}'),
                _buildStatRow(
                  'Lines',
                  '${ocrResponse.blocks?.fold<int>(0, (sum, b) => sum + (b.lines?.length ?? 0)) ?? 0}',
                ),
                _buildStatRow(
                  'Confidence',
                  '${_calculateAverageConfidence(ocrResponse)}%',
                ),
                _buildStatRow(
                  'Languages',
                  ocrResponse.meta?.languages?.join(', ') ?? 'Unknown',
                ),
              ],
            ),
          ),

          // Tabs for different views
          Expanded(
            child: DefaultTabController(
              length: 3,
              child: Column(
                children: [
                  TabBar(
                    labelColor: Colors.blue.shade700,
                    tabs: const [
                      Tab(text: 'Extracted Text'),
                      Tab(text: 'Structured Data'),
                      Tab(text: 'Raw JSON'),
                    ],
                  ),
                  Expanded(
                    child: TabBarView(
                      children: [
                        _buildTextView(ocrResponse),
                        _buildStructuredView(ocrResponse),
                        _buildJsonView(ocrResponse),
                      ],
                    ),
                  ),
                ],
              ),
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
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.refresh),
                    label: const Text('Re-scan'),
                    onPressed: () {
                      Navigator.pop(context);
                      ocrProvider.reset();
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  flex: 2,
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.auto_awesome),
                    label: const Text('Enhance with AI'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue.shade700,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    onPressed: () => _proceedToAI(context),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey.shade700)),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  Widget _buildTextView(ocrResponse) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey.shade50,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.grey.shade300),
        ),
        child: SelectableText(
          ocrResponse.fullText ?? 'No text extracted',
          style: const TextStyle(
            fontSize: 16,
            height: 1.5,
            fontFamily: 'monospace',
          ),
        ),
      ),
    );
  }

  Widget _buildStructuredView(ocrResponse) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: ocrResponse.blocks?.length ?? 0,
      itemBuilder: (context, index) {
        final block = ocrResponse.blocks![index];
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          child: ExpansionTile(
            title: Text('Block ${index + 1}'),
            subtitle: Text('${block.lines?.length ?? 0} lines'),
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ...?block.lines?.map((line) => Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            children: [
                              Container(
                                width: 4,
                                height: 20,
                                decoration: BoxDecoration(
                                  color: _getConfidenceColor(line.confidence),
                                  borderRadius: BorderRadius.circular(2),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  line.text ?? '',
                                  style: const TextStyle(fontSize: 14),
                                ),
                              ),
                              Text(
                                '${(line.confidence * 100).toStringAsFixed(0)}%',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        )),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildJsonView(ocrResponse) {
    final jsonString = const JsonEncoder.withIndent('  ').convert(
      ocrResponse.toJson(),
    );

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

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) return Colors.green;
    if (confidence >= 0.6) return Colors.orange;
    return Colors.red;
  }

  void _showOCRInfo(BuildContext context, ocrResponse) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('OCR Information'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildInfoRow('Processing Time',
                  '${ocrResponse.meta?.processingTimeMs ?? 0}ms'),
              _buildInfoRow('Image DPI', '${ocrResponse.meta?.dpi ?? 0}'),
              _buildInfoRow('Quality', ocrResponse.quality?.blur ?? 'Unknown'),
              _buildInfoRow(
                  'Contrast', ocrResponse.quality?.contrast ?? 'Unknown'),
              _buildInfoRow('Skew', '${ocrResponse.quality?.skewAngle ?? 0}°'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
          Text(value),
        ],
      ),
    );
  }

  String _calculateAverageConfidence(OCRResponse ocrResponse) {
    if (ocrResponse.blocks == null || ocrResponse.blocks!.isEmpty) {
      return 'N/A';
    }

    double totalConfidence = 0;
    int count = 0;

    for (var block in ocrResponse.blocks!) {
      for (var line in block.lines) {
        totalConfidence += line.confidence;
        count++;
      }
    }

    if (count == 0) return 'N/A';
    return ((totalConfidence / count) * 100).toStringAsFixed(1);
  }

  void _proceedToAI(BuildContext context) {
    final ocrProvider = context.read<OCRProvider>();
    final aiProvider = context.read<AIProvider>();

    if (ocrProvider.extractedText != null && ocrProvider.ocrResponse != null) {
      aiProvider.setRawOCRData(
        ocrProvider.extractedText!,
        ocrProvider.ocrResponse!.toJson(),
      );

      Navigator.pushNamed(context, '/ai-processing');
    }
  }
}
