import '../models/user/user.dart';
import '../data/dummy_user.dart';

class AuthService {
  static Future<User?> login(String phoneNumber, String password) async {
    await Future.delayed(const Duration(seconds: 1));

    // find the user in the list
    try {
      final user = DummyUsers.users.firstWhere(
          (u) => u.phoneNumber == phoneNumber,
          orElse: () => throw Exception("User not fount"));

      // check password
      if (DummyUsers.passwords[phoneNumber] == password) {
        return user;
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  static Future<User?> doctorLogin(String phoneNumber, String password,
      String firstName, String lastName) async {
    await Future.delayed(const Duration(seconds: 1));

    // find the doctor in the list
    try {
      final doctor = DummyUsers.doctors.firstWhere(
          (d) =>
              d.phoneNumber == phoneNumber &&
              d.firstName == firstName &&
              d.lastName == lastName,
          orElse: () => throw Exception("Doctor not found"));

      // check password
      if (DummyUsers.doctorPasswords[phoneNumber] == password) {
        return doctor;
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }
}
