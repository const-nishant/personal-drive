import 'package:flutter/material.dart';
import 'package:personal_drive/ui/screens/home_screen.dart';

class AppNavbar extends StatefulWidget {
  const AppNavbar({super.key});

  @override
  State<AppNavbar> createState() => _AppNavbarState();
}

class _AppNavbarState extends State<AppNavbar> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    Center(child: Text('Files Screen')),
    Center(child: Text('Photos Screen')),
    Center(child: Text('Settings Screen')),
  ];

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: colorScheme.surface,
          border: Border(
            top: BorderSide(
              color: isDark ? const Color(0xFF2D3748) : const Color(0xFFE5E7EB),
              width: 1,
            ),
          ),
          boxShadow: [
            BoxShadow(
              color: isDark ? Colors.transparent : Colors.black45,
              blurRadius: 20,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildNavItem(
                  icon: Icons.home,
                  label: 'Home',
                  index: 0,
                  colorScheme: colorScheme,
                ),
                _buildNavItem(
                  icon: Icons.folder_outlined,
                  label: 'Files',
                  index: 1,
                  colorScheme: colorScheme,
                ),
                _buildNavItem(
                  icon: Icons.photo_library_outlined,
                  label: 'Photos',
                  index: 2,
                  colorScheme: colorScheme,
                ),
                _buildNavItem(
                  icon: Icons.settings_outlined,
                  label: 'Settings',
                  index: 3,
                  colorScheme: colorScheme,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required IconData icon,
    required String label,
    required int index,
    required ColorScheme colorScheme,
  }) {
    final isSelected = _selectedIndex == index;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return InkWell(
      onTap: () {
        setState(() {
          _selectedIndex = index;
        });
      },
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 24,
              color: isSelected
                  ? colorScheme.primary
                  : (isDark
                        ? const Color(0xFF9CA3AF)
                        : const Color(0xFF9CA3AF)),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w500,
                color: isSelected
                    ? colorScheme.primary
                    : (isDark
                          ? const Color(0xFF9CA3AF)
                          : const Color(0xFF9CA3AF)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
