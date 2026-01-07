import 'package:flutter/material.dart';

// Design Reference Theme - Light Mode
// Background: #F6F7F8, Cards: #FFFFFF, Primary: #137FEC
ThemeData lightTheme = ThemeData(
  colorScheme: ColorScheme.light(
    surface: const Color(0xFFF6F7F8), // background-light
    primary: const Color(0xFF137FEC), // primary blue
    secondary: Colors.grey.shade600, // secondary text
    tertiary: Colors.white, // card-light
    inversePrimary: Colors.black87, // main text
  ),
  dialogTheme: DialogThemeData(
    titleTextStyle: const TextStyle(color: Colors.black87),
    contentTextStyle: TextStyle(color: Colors.grey.shade600),
  ),
  iconButtonTheme: const IconButtonThemeData(
    style: ButtonStyle(iconColor: WidgetStatePropertyAll(Colors.white)),
  ),
);
