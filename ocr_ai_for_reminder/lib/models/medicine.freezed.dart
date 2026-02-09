// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'medicine.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

Medicine _$MedicineFromJson(Map<String, dynamic> json) {
  return _Medicine.fromJson(json);
}

/// @nodoc
mixin _$Medicine {
  String get name => throw _privateConstructorUsedError;
  String get dosage => throw _privateConstructorUsedError;
  String get frequency => throw _privateConstructorUsedError;
  String? get duration => throw _privateConstructorUsedError;
  String? get instructions => throw _privateConstructorUsedError;
  bool get isMorning => throw _privateConstructorUsedError;
  bool get isAfternoon => throw _privateConstructorUsedError;
  bool get isEvening => throw _privateConstructorUsedError;
  bool get isNight => throw _privateConstructorUsedError;

  /// Serializes this Medicine to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Medicine
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MedicineCopyWith<Medicine> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MedicineCopyWith<$Res> {
  factory $MedicineCopyWith(Medicine value, $Res Function(Medicine) then) =
      _$MedicineCopyWithImpl<$Res, Medicine>;
  @useResult
  $Res call(
      {String name,
      String dosage,
      String frequency,
      String? duration,
      String? instructions,
      bool isMorning,
      bool isAfternoon,
      bool isEvening,
      bool isNight});
}

/// @nodoc
class _$MedicineCopyWithImpl<$Res, $Val extends Medicine>
    implements $MedicineCopyWith<$Res> {
  _$MedicineCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Medicine
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? dosage = null,
    Object? frequency = null,
    Object? duration = freezed,
    Object? instructions = freezed,
    Object? isMorning = null,
    Object? isAfternoon = null,
    Object? isEvening = null,
    Object? isNight = null,
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
      frequency: null == frequency
          ? _value.frequency
          : frequency // ignore: cast_nullable_to_non_nullable
              as String,
      duration: freezed == duration
          ? _value.duration
          : duration // ignore: cast_nullable_to_non_nullable
              as String?,
      instructions: freezed == instructions
          ? _value.instructions
          : instructions // ignore: cast_nullable_to_non_nullable
              as String?,
      isMorning: null == isMorning
          ? _value.isMorning
          : isMorning // ignore: cast_nullable_to_non_nullable
              as bool,
      isAfternoon: null == isAfternoon
          ? _value.isAfternoon
          : isAfternoon // ignore: cast_nullable_to_non_nullable
              as bool,
      isEvening: null == isEvening
          ? _value.isEvening
          : isEvening // ignore: cast_nullable_to_non_nullable
              as bool,
      isNight: null == isNight
          ? _value.isNight
          : isNight // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MedicineImplCopyWith<$Res>
    implements $MedicineCopyWith<$Res> {
  factory _$$MedicineImplCopyWith(
          _$MedicineImpl value, $Res Function(_$MedicineImpl) then) =
      __$$MedicineImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      String dosage,
      String frequency,
      String? duration,
      String? instructions,
      bool isMorning,
      bool isAfternoon,
      bool isEvening,
      bool isNight});
}

/// @nodoc
class __$$MedicineImplCopyWithImpl<$Res>
    extends _$MedicineCopyWithImpl<$Res, _$MedicineImpl>
    implements _$$MedicineImplCopyWith<$Res> {
  __$$MedicineImplCopyWithImpl(
      _$MedicineImpl _value, $Res Function(_$MedicineImpl) _then)
      : super(_value, _then);

  /// Create a copy of Medicine
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? dosage = null,
    Object? frequency = null,
    Object? duration = freezed,
    Object? instructions = freezed,
    Object? isMorning = null,
    Object? isAfternoon = null,
    Object? isEvening = null,
    Object? isNight = null,
  }) {
    return _then(_$MedicineImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      dosage: null == dosage
          ? _value.dosage
          : dosage // ignore: cast_nullable_to_non_nullable
              as String,
      frequency: null == frequency
          ? _value.frequency
          : frequency // ignore: cast_nullable_to_non_nullable
              as String,
      duration: freezed == duration
          ? _value.duration
          : duration // ignore: cast_nullable_to_non_nullable
              as String?,
      instructions: freezed == instructions
          ? _value.instructions
          : instructions // ignore: cast_nullable_to_non_nullable
              as String?,
      isMorning: null == isMorning
          ? _value.isMorning
          : isMorning // ignore: cast_nullable_to_non_nullable
              as bool,
      isAfternoon: null == isAfternoon
          ? _value.isAfternoon
          : isAfternoon // ignore: cast_nullable_to_non_nullable
              as bool,
      isEvening: null == isEvening
          ? _value.isEvening
          : isEvening // ignore: cast_nullable_to_non_nullable
              as bool,
      isNight: null == isNight
          ? _value.isNight
          : isNight // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MedicineImpl implements _Medicine {
  const _$MedicineImpl(
      {required this.name,
      required this.dosage,
      required this.frequency,
      this.duration,
      this.instructions,
      this.isMorning = false,
      this.isAfternoon = false,
      this.isEvening = false,
      this.isNight = false});

  factory _$MedicineImpl.fromJson(Map<String, dynamic> json) =>
      _$$MedicineImplFromJson(json);

  @override
  final String name;
  @override
  final String dosage;
  @override
  final String frequency;
  @override
  final String? duration;
  @override
  final String? instructions;
  @override
  @JsonKey()
  final bool isMorning;
  @override
  @JsonKey()
  final bool isAfternoon;
  @override
  @JsonKey()
  final bool isEvening;
  @override
  @JsonKey()
  final bool isNight;

  @override
  String toString() {
    return 'Medicine(name: $name, dosage: $dosage, frequency: $frequency, duration: $duration, instructions: $instructions, isMorning: $isMorning, isAfternoon: $isAfternoon, isEvening: $isEvening, isNight: $isNight)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MedicineImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.dosage, dosage) || other.dosage == dosage) &&
            (identical(other.frequency, frequency) ||
                other.frequency == frequency) &&
            (identical(other.duration, duration) ||
                other.duration == duration) &&
            (identical(other.instructions, instructions) ||
                other.instructions == instructions) &&
            (identical(other.isMorning, isMorning) ||
                other.isMorning == isMorning) &&
            (identical(other.isAfternoon, isAfternoon) ||
                other.isAfternoon == isAfternoon) &&
            (identical(other.isEvening, isEvening) ||
                other.isEvening == isEvening) &&
            (identical(other.isNight, isNight) || other.isNight == isNight));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, name, dosage, frequency,
      duration, instructions, isMorning, isAfternoon, isEvening, isNight);

  /// Create a copy of Medicine
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MedicineImplCopyWith<_$MedicineImpl> get copyWith =>
      __$$MedicineImplCopyWithImpl<_$MedicineImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MedicineImplToJson(
      this,
    );
  }
}

abstract class _Medicine implements Medicine {
  const factory _Medicine(
      {required final String name,
      required final String dosage,
      required final String frequency,
      final String? duration,
      final String? instructions,
      final bool isMorning,
      final bool isAfternoon,
      final bool isEvening,
      final bool isNight}) = _$MedicineImpl;

  factory _Medicine.fromJson(Map<String, dynamic> json) =
      _$MedicineImpl.fromJson;

  @override
  String get name;
  @override
  String get dosage;
  @override
  String get frequency;
  @override
  String? get duration;
  @override
  String? get instructions;
  @override
  bool get isMorning;
  @override
  bool get isAfternoon;
  @override
  bool get isEvening;
  @override
  bool get isNight;

  /// Create a copy of Medicine
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MedicineImplCopyWith<_$MedicineImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
