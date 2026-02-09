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
}
