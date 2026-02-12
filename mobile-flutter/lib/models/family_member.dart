class FamilyMember {
  final String id;
  final String name;
  final String gender;
  final int age;
  final String phone;
  final String? avatarUrl;
  final bool hasPendingPrescription;
  final String? lastActivity;
  final String? lastActivityTime;

  FamilyMember({
    required this.id,
    required this.name,
    required this.gender,
    required this.age,
    required this.phone,
    this.avatarUrl,
    this.hasPendingPrescription = false,
    this.lastActivity,
    this.lastActivityTime,
  });
}