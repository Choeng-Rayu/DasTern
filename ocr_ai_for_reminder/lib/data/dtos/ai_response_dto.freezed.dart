// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ai_response_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

AiResponseDto _$AiResponseDtoFromJson(Map<String, dynamic> json) {
  return _AiResponseDto.fromJson(json);
}

/// @nodoc
mixin _$AiResponseDto {
  bool get success => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  @JsonKey(name: 'patient_info')
  Map<String, dynamic>? get patientInfo => throw _privateConstructorUsedError;
  @JsonKey(name: 'medical_info')
  Map<String, dynamic>? get medicalInfo => throw _privateConstructorUsedError;
  @JsonKey(name: 'medications')
  List<MedicationItemDto>? get medications =>
      throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;

  /// Serializes this AiResponseDto to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AiResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AiResponseDtoCopyWith<AiResponseDto> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AiResponseDtoCopyWith<$Res> {
  factory $AiResponseDtoCopyWith(
          AiResponseDto value, $Res Function(AiResponseDto) then) =
      _$AiResponseDtoCopyWithImpl<$Res, AiResponseDto>;
  @useResult
  $Res call(
      {bool success,
      String? error,
      @JsonKey(name: 'patient_info') Map<String, dynamic>? patientInfo,
      @JsonKey(name: 'medical_info') Map<String, dynamic>? medicalInfo,
      @JsonKey(name: 'medications') List<MedicationItemDto>? medications,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class _$AiResponseDtoCopyWithImpl<$Res, $Val extends AiResponseDto>
    implements $AiResponseDtoCopyWith<$Res> {
  _$AiResponseDtoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AiResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? error = freezed,
    Object? patientInfo = freezed,
    Object? medicalInfo = freezed,
    Object? medications = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      patientInfo: freezed == patientInfo
          ? _value.patientInfo
          : patientInfo // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      medicalInfo: freezed == medicalInfo
          ? _value.medicalInfo
          : medicalInfo // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      medications: freezed == medications
          ? _value.medications
          : medications // ignore: cast_nullable_to_non_nullable
              as List<MedicationItemDto>?,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AiResponseDtoImplCopyWith<$Res>
    implements $AiResponseDtoCopyWith<$Res> {
  factory _$$AiResponseDtoImplCopyWith(
          _$AiResponseDtoImpl value, $Res Function(_$AiResponseDtoImpl) then) =
      __$$AiResponseDtoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      String? error,
      @JsonKey(name: 'patient_info') Map<String, dynamic>? patientInfo,
      @JsonKey(name: 'medical_info') Map<String, dynamic>? medicalInfo,
      @JsonKey(name: 'medications') List<MedicationItemDto>? medications,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class __$$AiResponseDtoImplCopyWithImpl<$Res>
    extends _$AiResponseDtoCopyWithImpl<$Res, _$AiResponseDtoImpl>
    implements _$$AiResponseDtoImplCopyWith<$Res> {
  __$$AiResponseDtoImplCopyWithImpl(
      _$AiResponseDtoImpl _value, $Res Function(_$AiResponseDtoImpl) _then)
      : super(_value, _then);

  /// Create a copy of AiResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? error = freezed,
    Object? patientInfo = freezed,
    Object? medicalInfo = freezed,
    Object? medications = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_$AiResponseDtoImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      patientInfo: freezed == patientInfo
          ? _value._patientInfo
          : patientInfo // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      medicalInfo: freezed == medicalInfo
          ? _value._medicalInfo
          : medicalInfo // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      medications: freezed == medications
          ? _value._medications
          : medications // ignore: cast_nullable_to_non_nullable
              as List<MedicationItemDto>?,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AiResponseDtoImpl implements _AiResponseDto {
  const _$AiResponseDtoImpl(
      {required this.success,
      this.error,
      @JsonKey(name: 'patient_info') final Map<String, dynamic>? patientInfo,
      @JsonKey(name: 'medical_info') final Map<String, dynamic>? medicalInfo,
      @JsonKey(name: 'medications') final List<MedicationItemDto>? medications,
      final Map<String, dynamic>? metadata})
      : _patientInfo = patientInfo,
        _medicalInfo = medicalInfo,
        _medications = medications,
        _metadata = metadata;

  factory _$AiResponseDtoImpl.fromJson(Map<String, dynamic> json) =>
      _$$AiResponseDtoImplFromJson(json);

  @override
  final bool success;
  @override
  final String? error;
  final Map<String, dynamic>? _patientInfo;
  @override
  @JsonKey(name: 'patient_info')
  Map<String, dynamic>? get patientInfo {
    final value = _patientInfo;
    if (value == null) return null;
    if (_patientInfo is EqualUnmodifiableMapView) return _patientInfo;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, dynamic>? _medicalInfo;
  @override
  @JsonKey(name: 'medical_info')
  Map<String, dynamic>? get medicalInfo {
    final value = _medicalInfo;
    if (value == null) return null;
    if (_medicalInfo is EqualUnmodifiableMapView) return _medicalInfo;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final List<MedicationItemDto>? _medications;
  @override
  @JsonKey(name: 'medications')
  List<MedicationItemDto>? get medications {
    final value = _medications;
    if (value == null) return null;
    if (_medications is EqualUnmodifiableListView) return _medications;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'AiResponseDto(success: $success, error: $error, patientInfo: $patientInfo, medicalInfo: $medicalInfo, medications: $medications, metadata: $metadata)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AiResponseDtoImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.error, error) || other.error == error) &&
            const DeepCollectionEquality()
                .equals(other._patientInfo, _patientInfo) &&
            const DeepCollectionEquality()
                .equals(other._medicalInfo, _medicalInfo) &&
            const DeepCollectionEquality()
                .equals(other._medications, _medications) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      success,
      error,
      const DeepCollectionEquality().hash(_patientInfo),
      const DeepCollectionEquality().hash(_medicalInfo),
      const DeepCollectionEquality().hash(_medications),
      const DeepCollectionEquality().hash(_metadata));

  /// Create a copy of AiResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AiResponseDtoImplCopyWith<_$AiResponseDtoImpl> get copyWith =>
      __$$AiResponseDtoImplCopyWithImpl<_$AiResponseDtoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AiResponseDtoImplToJson(
      this,
    );
  }
}

abstract class _AiResponseDto implements AiResponseDto {
  const factory _AiResponseDto(
      {required final bool success,
      final String? error,
      @JsonKey(name: 'patient_info') final Map<String, dynamic>? patientInfo,
      @JsonKey(name: 'medical_info') final Map<String, dynamic>? medicalInfo,
      @JsonKey(name: 'medications') final List<MedicationItemDto>? medications,
      final Map<String, dynamic>? metadata}) = _$AiResponseDtoImpl;

  factory _AiResponseDto.fromJson(Map<String, dynamic> json) =
      _$AiResponseDtoImpl.fromJson;

  @override
  bool get success;
  @override
  String? get error;
  @override
  @JsonKey(name: 'patient_info')
  Map<String, dynamic>? get patientInfo;
  @override
  @JsonKey(name: 'medical_info')
  Map<String, dynamic>? get medicalInfo;
  @override
  @JsonKey(name: 'medications')
  List<MedicationItemDto>? get medications;
  @override
  Map<String, dynamic>? get metadata;

  /// Create a copy of AiResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AiResponseDtoImplCopyWith<_$AiResponseDtoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

MedicationItemDto _$MedicationItemDtoFromJson(Map<String, dynamic> json) {
  return _MedicationItemDto.fromJson(json);
}

/// @nodoc
mixin _$MedicationItemDto {
  String get name => throw _privateConstructorUsedError;
  String get dosage => throw _privateConstructorUsedError;
  List<String>? get times => throw _privateConstructorUsedError;
  @JsonKey(name: 'times_24h')
  List<String>? get times24h => throw _privateConstructorUsedError;
  String? get repeat => throw _privateConstructorUsedError;
  String? get notes => throw _privateConstructorUsedError;

  /// Serializes this MedicationItemDto to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MedicationItemDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MedicationItemDtoCopyWith<MedicationItemDto> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MedicationItemDtoCopyWith<$Res> {
  factory $MedicationItemDtoCopyWith(
          MedicationItemDto value, $Res Function(MedicationItemDto) then) =
      _$MedicationItemDtoCopyWithImpl<$Res, MedicationItemDto>;
  @useResult
  $Res call(
      {String name,
      String dosage,
      List<String>? times,
      @JsonKey(name: 'times_24h') List<String>? times24h,
      String? repeat,
      String? notes});
}

/// @nodoc
class _$MedicationItemDtoCopyWithImpl<$Res, $Val extends MedicationItemDto>
    implements $MedicationItemDtoCopyWith<$Res> {
  _$MedicationItemDtoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MedicationItemDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? dosage = null,
    Object? times = freezed,
    Object? times24h = freezed,
    Object? repeat = freezed,
    Object? notes = freezed,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      dosage: null == dosage
          ? _value.dosage
          : dosage // ignore: cast_nullable_to_non_nullable
              as String,
      times: freezed == times
          ? _value.times
          : times // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      times24h: freezed == times24h
          ? _value.times24h
          : times24h // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      repeat: freezed == repeat
          ? _value.repeat
          : repeat // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MedicationItemDtoImplCopyWith<$Res>
    implements $MedicationItemDtoCopyWith<$Res> {
  factory _$$MedicationItemDtoImplCopyWith(_$MedicationItemDtoImpl value,
          $Res Function(_$MedicationItemDtoImpl) then) =
      __$$MedicationItemDtoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      String dosage,
      List<String>? times,
      @JsonKey(name: 'times_24h') List<String>? times24h,
      String? repeat,
      String? notes});
}

/// @nodoc
class __$$MedicationItemDtoImplCopyWithImpl<$Res>
    extends _$MedicationItemDtoCopyWithImpl<$Res, _$MedicationItemDtoImpl>
    implements _$$MedicationItemDtoImplCopyWith<$Res> {
  __$$MedicationItemDtoImplCopyWithImpl(_$MedicationItemDtoImpl _value,
      $Res Function(_$MedicationItemDtoImpl) _then)
      : super(_value, _then);

  /// Create a copy of MedicationItemDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? dosage = null,
    Object? times = freezed,
    Object? times24h = freezed,
    Object? repeat = freezed,
    Object? notes = freezed,
  }) {
    return _then(_$MedicationItemDtoImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      dosage: null == dosage
          ? _value.dosage
          : dosage // ignore: cast_nullable_to_non_nullable
              as String,
      times: freezed == times
          ? _value._times
          : times // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      times24h: freezed == times24h
          ? _value._times24h
          : times24h // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      repeat: freezed == repeat
          ? _value.repeat
          : repeat // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MedicationItemDtoImpl implements _MedicationItemDto {
  const _$MedicationItemDtoImpl(
      {required this.name,
      required this.dosage,
      final List<String>? times,
      @JsonKey(name: 'times_24h') final List<String>? times24h,
      this.repeat,
      this.notes})
      : _times = times,
        _times24h = times24h;

  factory _$MedicationItemDtoImpl.fromJson(Map<String, dynamic> json) =>
      _$$MedicationItemDtoImplFromJson(json);

  @override
  final String name;
  @override
  final String dosage;
  final List<String>? _times;
  @override
  List<String>? get times {
    final value = _times;
    if (value == null) return null;
    if (_times is EqualUnmodifiableListView) return _times;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final List<String>? _times24h;
  @override
  @JsonKey(name: 'times_24h')
  List<String>? get times24h {
    final value = _times24h;
    if (value == null) return null;
    if (_times24h is EqualUnmodifiableListView) return _times24h;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  final String? repeat;
  @override
  final String? notes;

  @override
  String toString() {
    return 'MedicationItemDto(name: $name, dosage: $dosage, times: $times, times24h: $times24h, repeat: $repeat, notes: $notes)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MedicationItemDtoImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.dosage, dosage) || other.dosage == dosage) &&
            const DeepCollectionEquality().equals(other._times, _times) &&
            const DeepCollectionEquality().equals(other._times24h, _times24h) &&
            (identical(other.repeat, repeat) || other.repeat == repeat) &&
            (identical(other.notes, notes) || other.notes == notes));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      name,
      dosage,
      const DeepCollectionEquality().hash(_times),
      const DeepCollectionEquality().hash(_times24h),
      repeat,
      notes);

  /// Create a copy of MedicationItemDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MedicationItemDtoImplCopyWith<_$MedicationItemDtoImpl> get copyWith =>
      __$$MedicationItemDtoImplCopyWithImpl<_$MedicationItemDtoImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MedicationItemDtoImplToJson(
      this,
    );
  }
}

abstract class _MedicationItemDto implements MedicationItemDto {
  const factory _MedicationItemDto(
      {required final String name,
      required final String dosage,
      final List<String>? times,
      @JsonKey(name: 'times_24h') final List<String>? times24h,
      final String? repeat,
      final String? notes}) = _$MedicationItemDtoImpl;

  factory _MedicationItemDto.fromJson(Map<String, dynamic> json) =
      _$MedicationItemDtoImpl.fromJson;

  @override
  String get name;
  @override
  String get dosage;
  @override
  List<String>? get times;
  @override
  @JsonKey(name: 'times_24h')
  List<String>? get times24h;
  @override
  String? get repeat;
  @override
  String? get notes;

  /// Create a copy of MedicationItemDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MedicationItemDtoImplCopyWith<_$MedicationItemDtoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
