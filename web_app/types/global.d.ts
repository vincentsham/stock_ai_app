// types/global.d.ts
declare global {
  interface Window {
    userLocale?: string;
  }
}

// required for global augmentation
export {};