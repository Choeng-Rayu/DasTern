import 'package:flutter/material.dart';

class DoctorHeader extends StatelessWidget {
  final String userName;
  final VoidCallback? onNotificationTap;

  const DoctorHeader({
    Key? key,
    this.userName = 'សូស្តី ឧត្តមហេង !',
    this.onNotificationTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: Colors.white,
            child: Icon(Icons.person, color: Colors.blue.shade400),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              userName,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.notifications, color: Colors.white),
            onPressed: onNotificationTap ?? () {},
          ),
        ],
      ),
    );
  }
}
