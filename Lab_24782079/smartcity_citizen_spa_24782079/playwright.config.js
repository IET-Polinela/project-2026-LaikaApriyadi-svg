// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  // PERUBAHAN UTAMA: Ubah './tests' menjadi './playwright' 
  // agar sinkron dengan struktur folder kamu
  testDir: './playwright', 
  
  fullyParallel: false, 
  workers: 1,           
  reporter: [['list'], ['html']], 
  
  use: {
    baseURL: 'http://127.0.0.1:5500', 
    headless: false,
    trace: 'on-first-retry',
  },

  projects: [
    { 
      name: 'chromium', 
      use: { ...devices['Desktop Chrome'] } 
    },
  ],
});