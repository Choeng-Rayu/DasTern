// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ocr_response_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$OcrResponseDtoImpl _$$OcrResponseDtoImplFromJson(Map<String, dynamic> json) =>
    _$OcrResponseDtoImpl(
      rawText: json['raw_text'] as String?,
      blocks: (json['blocks'] as List<dynamic>?)
              ?.map((e) => OcrBlockDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$OcrResponseDtoImplToJson(
        _$OcrResponseDtoImpl instance) =>
    <String, dynamic>{
      'raw_text': instance.rawText,
      'blocks': instance.blocks,
    };

_$OcrBlockDtoImpl _$$OcrBlockDtoImplFromJson(Map<String, dynamic> json) =>
    _$OcrBlockDtoImpl(
      type: json['type'] as String? ?? 'unknown',
      bbox: json['bbox'] == null
          ? null
          : OcrBoundingBoxDto.fromJson(json['bbox'] as Map<String, dynamic>),
      lines: (json['lines'] as List<dynamic>?)
              ?.map((e) => OcrLineDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      rawText: json['raw_text'] as String?,
    );

Map<String, dynamic> _$$OcrBlockDtoImplToJson(_$OcrBlockDtoImpl instance) =>
    <String, dynamic>{
      'type': instance.type,
      'bbox': instance.bbox,
      'lines': instance.lines,
      'raw_text': instance.rawText,
    };

_$OcrLineDtoImpl _$$OcrLineDtoImplFromJson(Map<String, dynamic> json) =>
    _$OcrLineDtoImpl(
      text: json['text'] as String? ?? '',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      bbox: json['bbox'] == null
          ? null
          : OcrBoundingBoxDto.fromJson(json['bbox'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$OcrLineDtoImplToJson(_$OcrLineDtoImpl instance) =>
    <String, dynamic>{
      'text': instance.text,
      'confidence': instance.confidence,
      'bbox': instance.bbox,
    };

_$OcrBoundingBoxDtoImpl _$$OcrBoundingBoxDtoImplFromJson(
        Map<String, dynamic> json) =>
    _$OcrBoundingBoxDtoImpl(
      x: (json['x'] as num).toInt(),
      y: (json['y'] as num).toInt(),
      width: (json['width'] as num).toInt(),
      height: (json['height'] as num).toInt(),
    );

Map<String, dynamic> _$$OcrBoundingBoxDtoImplToJson(
        _$OcrBoundingBoxDtoImpl instance) =>
    <String, dynamic>{
      'x': instance.x,
      'y': instance.y,
      'width': instance.width,
      'height': instance.height,
    };
