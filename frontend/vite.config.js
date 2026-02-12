import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  plugins: [
    vue(),
    VitePWA({ 
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true
      },
      manifest: {
        name: 'GAE-CLIENT',
        short_name: 'GAE',
        description: 'AIoT 로봇 반려견 관리 플랫폼',
        theme_color: '#6A67CE',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  server: {
    // 백엔드 연결 설정
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // Spring Boot 포트 - AWS에서는 안되나 암튼 그런 이야기를 들음.
        changeOrigin: true,
        secure: false,
        ws: true
      },
      // 로봇 카메라 스트림 프록시 (CORS 우회)
      '/robot-stream': {
        target: 'http://192.168.100.246:8080',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/robot-stream/, '')
      },
    }
  }
})