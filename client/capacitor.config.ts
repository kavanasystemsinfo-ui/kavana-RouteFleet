import { CapacitorConfig } from '@capacitor/core';

// Configuracion de Capacitor para empaquetar la PWA del repartidor como APK nativo.
// La app web vive en /app/ (webDir: 'dist' se sirve bajo esa ruta en GitHub Pages).
const config: CapacitorConfig = {
  appId: 'com.kavanasystems.routefleet',
  appName: 'RouteFleet',
  webDir: 'dist',
  server: {
    // Permite que la WebView apunte a la URL de produccion (PWA) en vez de solo assets locales.
    // En produccion la app usa el backend real; el androidUrl apunta a la PWA publicada.
    androidScheme: 'https'
  }
};

export default config;
