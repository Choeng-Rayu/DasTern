class BoundingBox {
  final int x;
  final int y;
  final int width;
  final int height;

  BoundingBox({
    required this.x,
    required this.y,
    required this.width,
    required this.height,
  });

  factory BoundingBox.fromJson(Map<String, dynamic> json) {
    return BoundingBox(
      x: json['x'] ?? 0,
      y: json['y'] ?? 0,
      width: json['width'] ?? 0,
      height: json['height'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'x': x,
      'y': y,
      'width': width,
      'height': height,
    };
  }
}

class TextLine {
  final String text;
  final BoundingBox bbox;
  final double confidence;
  final String? language;
  final List<String> tags;

  TextLine({
    required this.text,
    required this.bbox,
    required this.confidence,
    this.language,
    required this.tags,
  });

  factory TextLine.fromJson(Map<String, dynamic> json) {
    return TextLine(
      text: json['text'] ?? '',
      bbox: json['bbox'] != null
          ? BoundingBox.fromJson(json['bbox'])
          : BoundingBox(x: 0, y: 0, width: 0, height: 0),
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      language: json['language'],
      tags: json['tags'] != null ? List<String>.from(json['tags']) : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'text': text,
      'bbox': bbox.toJson(),
      'confidence': confidence,
      'language': language,
      'tags': tags,
    };
  }
}

class Block {
  final String type;
  final BoundingBox bbox;
  final List<TextLine> lines;
  final String? rawText;

  Block({
    required this.type,
    required this.bbox,
    required this.lines,
    this.rawText,
  });

  factory Block.fromJson(Map<String, dynamic> json) {
    return Block(
      type: json['type'] ?? 'text',
      bbox: json['bbox'] != null
          ? BoundingBox.fromJson(json['bbox'])
          : BoundingBox(x: 0, y: 0, width: 0, height: 0),
      lines: json['lines'] != null
          ? (json['lines'] as List).map((e) => TextLine.fromJson(e)).toList()
          : [],
      rawText: json['raw_text'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'bbox': bbox.toJson(),
      'lines': lines.map((e) => e.toJson()).toList(),
      'raw_text': rawText,
    };
  }
}

class QualityMetrics {
  final String blur;
  final double blurScore;
  final String contrast;
  final double contrastScore;
  final double skewAngle;
  final int? dpi;
  final bool isGrayscale;

  QualityMetrics({
    required this.blur,
    required this.blurScore,
    required this.contrast,
    required this.contrastScore,
    required this.skewAngle,
    this.dpi,
    required this.isGrayscale,
  });

  factory QualityMetrics.fromJson(Map<String, dynamic> json) {
    return QualityMetrics(
      blur: json['blur'] ?? 'unknown',
      blurScore: (json['blur_score'] ?? 0.0).toDouble(),
      contrast: json['contrast'] ?? 'unknown',
      contrastScore: (json['contrast_score'] ?? 0.0).toDouble(),
      skewAngle: (json['skew_angle'] ?? 0.0).toDouble(),
      dpi: json['dpi'],
      isGrayscale: json['is_grayscale'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'blur': blur,
      'blur_score': blurScore,
      'contrast': contrast,
      'contrast_score': contrastScore,
      'skew_angle': skewAngle,
      'dpi': dpi,
      'is_grayscale': isGrayscale,
    };
  }
}

class ProcessingMeta {
  final List<String> languages;
  final int? dpi;
  final double processingTimeMs;
  final String modelVersion;
  final Map<String, dynamic> stageTimes;
  final Map<String, dynamic> imageSize;

  ProcessingMeta({
    required this.languages,
    this.dpi,
    required this.processingTimeMs,
    required this.modelVersion,
    required this.stageTimes,
    required this.imageSize,
  });

  factory ProcessingMeta.fromJson(Map<String, dynamic> json) {
    return ProcessingMeta(
      languages:
          json['languages'] != null ? List<String>.from(json['languages']) : [],
      dpi: json['dpi'],
      processingTimeMs: (json['processing_time_ms'] ?? 0.0).toDouble(),
      modelVersion: json['model_version'] ?? '',
      stageTimes: json['stage_times'] ?? {},
      imageSize: json['image_size'] ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'languages': languages,
      'dpi': dpi,
      'processing_time_ms': processingTimeMs,
      'model_version': modelVersion,
      'stage_times': stageTimes,
      'image_size': imageSize,
    };
  }
}

class OCRResponse {
  final ProcessingMeta meta;
  final QualityMetrics quality;
  final List<Block> blocks;
  final String fullText;
  final bool success;
  final String? error;

  OCRResponse({
    required this.meta,
    required this.quality,
    required this.blocks,
    required this.fullText,
    required this.success,
    this.error,
  });

  factory OCRResponse.fromJson(Map<String, dynamic> json) {
    // Handle both old and new API response formats
    if (json['raw'] != null && json['raw'] is List) {
      // Old format - convert to new format
      final rawElements = json['raw'] as List;
      final texts = rawElements
          .where((e) =>
              e['text'] != null && e['text'].toString().trim().isNotEmpty)
          .map((e) => e['text'].toString())
          .toList();

      return OCRResponse(
        meta: ProcessingMeta(
          languages: json['languages_used']?.toString().split('+') ?? ['eng'],
          processingTimeMs: 0,
          modelVersion: 'tesseract',
          stageTimes: {},
          imageSize: {
            'width': json['stats']?['image_width'] ?? 0,
            'height': json['stats']?['image_height'] ?? 0,
          },
        ),
        quality: QualityMetrics(
          blur: 'unknown',
          blurScore: 0,
          contrast: 'unknown',
          contrastScore: 0,
          skewAngle: 0,
          isGrayscale: false,
        ),
        blocks: [],
        fullText: texts.join(' '),
        success: json['success'] ?? false,
        error: json['error'],
      );
    }

    // New format
    return OCRResponse(
      meta: json['meta'] != null
          ? ProcessingMeta.fromJson(json['meta'])
          : ProcessingMeta(
              languages: [],
              processingTimeMs: 0,
              modelVersion: '',
              stageTimes: {},
              imageSize: {},
            ),
      quality: json['quality'] != null
          ? QualityMetrics.fromJson(json['quality'])
          : QualityMetrics(
              blur: 'unknown',
              blurScore: 0,
              contrast: 'unknown',
              contrastScore: 0,
              skewAngle: 0,
              isGrayscale: false,
            ),
      blocks: json['blocks'] != null
          ? (json['blocks'] as List).map((e) => Block.fromJson(e)).toList()
          : [],
      fullText: json['full_text'] ?? '',
      success: json['success'] ?? false,
      error: json['error'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'meta': meta.toJson(),
      'quality': quality.toJson(),
      'blocks': blocks.map((e) => e.toJson()).toList(),
      'full_text': fullText,
      'success': success,
      'error': error,
    };
  }

  // Helper getters
  bool get hasError => error != null && error!.isNotEmpty;
  bool get hasData => fullText.isNotEmpty;

  int get totalBlocks => blocks.length;
  int get totalLines =>
      blocks.fold(0, (sum, block) => sum + block.lines.length);
  double get avgConfidence {
    if (blocks.isEmpty) return 0.0;
    var totalConfidence = 0.0;
    var lineCount = 0;
    for (final block in blocks) {
      for (final line in block.lines) {
        totalConfidence += line.confidence;
        lineCount++;
      }
    }
    return lineCount > 0 ? totalConfidence / lineCount : 0.0;
  }

  // Backward compatibility getter
  double get confidence => avgConfidence;

  // Convert to AI request format
  Map<String, dynamic> toAiRequestJson() {
    // Extract raw elements from blocks
    final rawElements = <Map<String, dynamic>>[];
    for (final block in blocks) {
      for (final line in block.lines) {
        rawElements.add({
          'text': line.text,
          'confidence': line.confidence,
          'bbox': line.bbox.toJson(),
        });
      }
    }

    return {
      'raw_ocr_json': {
        'raw': rawElements,
        'full_text': fullText,
        'languages_used': meta.languages.join('+'),
        'success': success,
      }
    };
  }
}
