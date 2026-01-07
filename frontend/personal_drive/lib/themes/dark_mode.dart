import 'package:flutter/material.dart';

// Design Reference Theme - Dark Mode
// Background: #101922, Cards: #1C2630, Primary: #137FEC
ThemeData darkTheme = ThemeData(
  colorScheme: ColorScheme.dark(
    surface: const Color(0xFF101922), // background-dark
    primary: const Color(0xFF137FEC), // primary blue
    secondary: Colors.grey.shade500, // secondary text
    tertiary: const Color(0xFF1C2630), // card-dark
    inversePrimary: Colors.white, // main text
  ),
  dialogTheme: DialogThemeData(
    titleTextStyle: const TextStyle(color: Colors.white),
    contentTextStyle: TextStyle(color: Colors.grey.shade400),
    backgroundColor: const Color(0xFF1C2630),
  ),
  iconTheme: IconThemeData(color: Colors.grey.shade200),
);
