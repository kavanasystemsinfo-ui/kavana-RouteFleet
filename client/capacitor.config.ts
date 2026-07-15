import { CapacitorConfig } from '@capacitor/core';

// Configuracion de Capacitor para empaquetar la PWA del repartidor como APK nativo.
// La WebView carga la PWA de produccion (server.url) en vez de solo assets locales,
// asi el APK es un wrapper de la web y se actualiza al desplegar la web.
const config: CapacitorConfig = {
  appId: 'com.kavanasystems.routefleet',
  appName: 'RouteFleet',
  webDir: 'dist',
  server: {
    // URL de la PWA publicada en produccion. El APK la carga en la WebView.
    url: 'https://routefleet.kavanasystems.com/app',
    androidScheme: 'https'
  }
};

export default config;
