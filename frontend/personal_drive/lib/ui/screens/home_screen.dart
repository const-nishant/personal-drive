import 'package:flutter/material.dart';
import 'package:personal_drive/core/utils/utils.dart';
import 'package:personal_drive/model/file_item.dart';
import 'package:personal_drive/services/auth_service.dart';
import 'package:personal_drive/ui/widgets/file_card.dart';
import 'package:personal_drive/ui/widgets/search_bar.dart';
import 'package:personal_drive/ui/widgets/storage_usage.dart';
import 'package:provider/provider.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final List<FileItem> recentFiles = [
    FileItem(
      name: 'Project Alpha Contract.pdf',
      type: 'PDF',
      icon: Icons.picture_as_pdf,
      iconColor: Colors.red,
      backgroundColor: const Color(0xFFfee2e2),
      darkBackgroundColor: const Color(0xFF7f1d1d),
      timeAgo: 'Edited 2h ago',
    ),
    FileItem(
      name: 'Family_Vacation_04.jpg',
      type: 'Image',
      icon: Icons.image,
      iconColor: Colors.purple,
      backgroundColor: const Color(0xFFf3e8ff),
      darkBackgroundColor: const Color(0xFF4c1d95),
      timeAgo: 'Uploaded Yesterday',
    ),
    FileItem(
      name: 'Q3 Financials.docx',
      type: 'DOCX',
      icon: Icons.article,
      iconColor: Colors.blue,
      backgroundColor: const Color(0xFFdbeafe),
      darkBackgroundColor: const Color(0xFF1e3a8a),
      timeAgo: 'Edited Monday',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(74),
        child: Container(
          color: Theme.of(context).colorScheme.surface,
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Greeting and Profile
              Padding(
                padding: const EdgeInsets.only(top: 22.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Good Morning, {user}',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Theme.of(context).colorScheme.inversePrimary,
                            letterSpacing: -0.015,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          getFormattedDate(),
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: Theme.of(context).colorScheme.secondary,
                          ),
                        ),
                      ],
                    ),
                    // Profile Button
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: Theme.of(context).colorScheme.primary,
                          width: 2,
                        ),
                        image: const DecorationImage(
                          image: NetworkImage(
                            'https://ui-avatars.com/api/?name={user}&bold=true',
                          ),
                          fit: BoxFit.cover,
                        ),
                      ),
                      child: Stack(
                        children: [
                          Positioned(
                            bottom: 0,
                            right: 0,
                            child: Container(
                              width: 10,
                              height: 10,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.green.shade500,
                                border: Border.all(
                                  color: Theme.of(context).colorScheme.tertiary,
                                  width: 2,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      body: Stack(
        children: [
          Column(
            children: [
              // Top App Bar

              // Scrollable Content
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.only(bottom: 140),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 16),
                        // AI Search Bar
                        const AiSearchBar(),
                        const SizedBox(height: 24),
                        // Storage Widget
                        StorageUsage(usedGB: 48, totalGB: 100),

                        const SizedBox(height: 32),
                        // Recent Activity Header
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Recent Activity',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Theme.of(
                                  context,
                                ).colorScheme.inversePrimary,
                              ),
                            ),
                            TextButton(
                              onPressed: () {},
                              child: Text(
                                'View All',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                  color: Theme.of(context).colorScheme.primary,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        // Recent Files
                        ...recentFiles.map((file) {
                          return FileCard(file: file);
                        }),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
          // FAB
          Positioned(
            bottom: 16,
            right: 16,
            child: FloatingActionButton(
              backgroundColor: Theme.of(context).colorScheme.primary,
              elevation: 8,
              shape: const CircleBorder(),
              onPressed: () async {
                //temp logout action
                await Provider.of<AuthService>(context, listen: false).logout();
              },
              child: const Icon(Icons.add, color: Colors.white, size: 28),
            ),
          ),
        ],
      ),
    );
  }
}
