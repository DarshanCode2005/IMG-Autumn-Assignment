import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'models/event.dart';
import 'providers/auth_provider.dart';
import 'providers/event_provider.dart';
import 'providers/photo_provider.dart';
import 'providers/websocket_provider.dart';
import 'providers/comment_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/signup_screen.dart';
import 'screens/home/home_screen.dart';
import 'screens/home/create_event_screen.dart';
import 'screens/gallery/gallery_screen.dart';
import 'screens/gallery/photo_detail_screen.dart';
import 'screens/upload/upload_screen.dart';
import 'models/photo.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => EventProvider()),
        ChangeNotifierProvider(create: (_) => PhotoProvider()),
        ChangeNotifierProvider(create: (_) => WebSocketProvider()),
        ChangeNotifierProvider(create: (_) => CommentProvider()),
      ],
      child: const AppRouter(),
    );
  }
}

class AppRouter extends StatelessWidget {
  const AppRouter({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    final router = GoRouter(
      refreshListenable: authProvider,
      initialLocation: '/',
      redirect: (context, state) {
        final isAuthenticated = authProvider.isAuthenticated;
        final isAuthRoute = state.uri.toString() == '/login' || 
                            state.uri.toString() == '/signup';

        if (!isAuthenticated && !isAuthRoute) return '/login';
        if (isAuthenticated && isAuthRoute) return '/';
        return null;
      },
      routes: [
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/signup',
          builder: (context, state) => const SignUpScreen(),
        ),
        GoRoute(
          path: '/',
          builder: (context, state) => const HomeScreen(),
        ),
        GoRoute(
          path: '/create-event',
          builder: (context, state) {
            final event = state.extra as Event?;
            return EventFormScreen(event: event);
          },
        ),
        GoRoute(
          path: '/gallery/:eventId',
          builder: (context, state) {
            final eventId = int.parse(state.pathParameters['eventId']!);
            return GalleryScreen(eventId: eventId);
          },
          routes: [
            GoRoute(
              path: 'photo',
              builder: (context, state) {
                final photo = state.extra as Photo;
                return PhotoDetailScreen(photo: photo);
              },
            ),
            GoRoute(
              path: 'upload',
              builder: (context, state) {
                final eventId = int.parse(state.pathParameters['eventId']!);
                return UploadScreen(eventId: eventId);
              },
            ),
          ],
        ),
      ],
    );

    return MaterialApp.router(
      title: 'IMG Project App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      routerConfig: router,
    );
  }
}
