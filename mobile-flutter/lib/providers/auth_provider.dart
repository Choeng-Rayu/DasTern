import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthProvider with ChangeNotifier {
  String? _token;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;

  String? get token => _token;

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    notifyListeners();
  }

  Future<void> saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    notifyListeners();
  }

  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    notifyListeners();
  }
}
