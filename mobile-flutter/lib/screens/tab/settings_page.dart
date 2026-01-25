import 'package:flutter/material.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  bool _notificationsEnabled = true;
  bool _soundEnabled = true;
  bool _vibrationEnabled = true;
  bool _darkMode = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        children: [
          // Profile Section
          Container(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 40,
                  backgroundColor:
                      Theme.of(context).primaryColor.withOpacity(0.1),
                  child: Icon(
                    Icons.person,
                    size: 40,
                    color: Theme.of(context).primaryColor,
                  ),
                ),
                const SizedBox(width: 16),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Dr. John Doe',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'john.doe@example.com',
                        style: TextStyle(
                          color: Colors.grey,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Premium Member',
                        style: TextStyle(
                          color: Colors.green,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: () {
                    // TODO: Edit profile
                  },
                ),
              ],
            ),
          ),
          const Divider(),

          // Account Settings
          _buildSectionHeader('Account Settings'),
          _buildListTile(
            Icons.person_outline,
            'Edit Profile',
            'Update your personal information',
            () {
              // TODO: Navigate to edit profile
            },
          ),
          _buildListTile(
            Icons.lock_outline,
            'Change Password',
            'Update your password',
            () {
              // TODO: Navigate to change password
            },
          ),
          _buildListTile(
            Icons.security,
            'Privacy & Security',
            'Manage your privacy settings',
            () {
              // TODO: Navigate to privacy settings
            },
          ),
          const Divider(),

          // Notification Settings
          _buildSectionHeader('Notifications'),
          _buildSwitchTile(
            Icons.notifications_outlined,
            'Push Notifications',
            'Receive medication reminders',
            _notificationsEnabled,
            (value) {
              setState(() {
                _notificationsEnabled = value;
              });
            },
          ),
          _buildSwitchTile(
            Icons.volume_up_outlined,
            'Sound',
            'Play sound for reminders',
            _soundEnabled,
            (value) {
              setState(() {
                _soundEnabled = value;
              });
            },
          ),
          _buildSwitchTile(
            Icons.vibration,
            'Vibration',
            'Vibrate for reminders',
            _vibrationEnabled,
            (value) {
              setState(() {
                _vibrationEnabled = value;
              });
            },
          ),
          const Divider(),

          // App Settings
          _buildSectionHeader('App Settings'),
          _buildSwitchTile(
            Icons.dark_mode_outlined,
            'Dark Mode',
            'Use dark theme',
            _darkMode,
            (value) {
              setState(() {
                _darkMode = value;
              });
            },
          ),
          _buildListTile(
            Icons.language,
            'Language',
            'English',
            () {
              // TODO: Show language picker
            },
          ),
          _buildListTile(
            Icons.access_time,
            'Reminder Defaults',
            'Set default reminder times',
            () {
              // TODO: Navigate to reminder settings
            },
          ),
          const Divider(),

          // Data & Storage
          _buildSectionHeader('Data & Storage'),
          _buildListTile(
            Icons.cloud_download,
            'Backup Data',
            'Backup your prescriptions',
            () {
              // TODO: Initiate backup
            },
          ),
          _buildListTile(
            Icons.download,
            'Export Data',
            'Download your data',
            () {
              // TODO: Export data
            },
          ),
          _buildListTile(
            Icons.delete_outline,
            'Clear Cache',
            'Free up storage space',
            () {
              _showClearCacheDialog();
            },
          ),
          const Divider(),

          // Support & About
          _buildSectionHeader('Support & About'),
          _buildListTile(
            Icons.help_outline,
            'Help & Support',
            'Get help or contact us',
            () {
              // TODO: Navigate to help
            },
          ),
          _buildListTile(
            Icons.description_outlined,
            'Terms of Service',
            'Read our terms',
            () {
              // TODO: Show terms
            },
          ),
          _buildListTile(
            Icons.privacy_tip_outlined,
            'Privacy Policy',
            'Read our privacy policy',
            () {
              // TODO: Show privacy policy
            },
          ),
          _buildListTile(
            Icons.info_outline,
            'About',
            'Version 1.0.0',
            () {
              _showAboutDialog();
            },
          ),
          const Divider(),

          // Logout
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: _showLogoutDialog,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
              child: const Text('Logout'),
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Theme.of(context).primaryColor,
        ),
      ),
    );
  }

  Widget _buildListTile(
    IconData icon,
    String title,
    String subtitle,
    VoidCallback onTap,
  ) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: onTap,
    );
  }

  Widget _buildSwitchTile(
    IconData icon,
    String title,
    String subtitle,
    bool value,
    Function(bool) onChanged,
  ) {
    return SwitchListTile(
      secondary: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle),
      value: value,
      onChanged: onChanged,
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Perform logout
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Logged out successfully'),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }

  void _showClearCacheDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Cache'),
        content: const Text(
            'This will remove temporary files and free up storage space. Continue?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Cache cleared successfully'),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog() {
    showAboutDialog(
      context: context,
      applicationName: 'DasTern',
      applicationVersion: '1.0.0',
      applicationIcon: Icon(
        Icons.medication,
        size: 48,
        color: Theme.of(context).primaryColor,
      ),
      children: [
        const Text('Medical Prescription Reminder App'),
        const SizedBox(height: 8),
        const Text('© 2026 DasTern Team'),
      ],
    );
  }
}
