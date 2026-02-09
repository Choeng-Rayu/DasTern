import '../models/user/user.dart';

class DummyUsers {
  // list of users
  static final List<User> users = [
    User(phoneNumber: "012345678", token: "token1"),
    User(phoneNumber: "099999999", token: "token2"),
    User( phoneNumber: "077777777", token: "token3"),
    User(phoneNumber: "000000000", token: "token4"),
  ];

  // passwords corresponding to users
  static final Map<String, String> passwords = {
    "012345678": "1234",
    "099999999": "abcd",
    "077777777": "5678",
    "000000000": "0000",
  };
}
