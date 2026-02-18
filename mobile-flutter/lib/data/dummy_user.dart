import '../models/user/user.dart';

class DummyUsers {
  // list of users
  static final List<User> users = [
    User(phoneNumber: "012345678", token: "token1"),
    User(phoneNumber: "099999999", token: "token2"),
    User(phoneNumber: "077777777", token: "token3"),
    User(phoneNumber: "000000000", token: "token4"),
  ];

  // passwords corresponding to users
  static final Map<String, String> passwords = {
    "012345678": "1234",
    "099999999": "abcd",
    "077777777": "5678",
    "000000000": "0000",
  };

  // Doctor dummy data
  static final List<User> doctors = [
    User(
      phoneNumber: "855012345678",
      token: "doctor_token_1",
      firstName: "Haha",
      lastName: "haha",
    ),
    User(
      phoneNumber: "855090000000",
      token: "doctor_token_2",
      firstName: "ពេទ្យ",
      lastName: "ដាវីត",
    ),
    User(
      phoneNumber: "7777777",
      token: "doctor_token_3",
      firstName: "haha",
      lastName: "haha",
    ),
  ];

  // Doctor passwords corresponding to phone numbers
  static final Map<String, String> doctorPasswords = {
    "855012345678": "doctor123",
    "855090000000": "doctor456",
    "7777777": "doctor000",
  };
}
