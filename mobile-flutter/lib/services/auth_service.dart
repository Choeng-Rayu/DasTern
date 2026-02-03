import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final String baseUrl;
  AuthService({required this.baseUrl});

  Future<String?> login(String username, String password) async {
    final resp = await http.post(Uri.parse('$baseUrl/login'), body: {
      'username': username,
      'password': password,
    });

    if (resp.statusCode == 200) {
      final data = json.decode(resp.body);
      final token = data['token'] as String?;
      if (token != null) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', token);
        return token;
      }
    }

    return null;
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }
}
