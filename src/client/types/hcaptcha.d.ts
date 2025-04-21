export {};

declare global {
  interface Window {
    hcaptcha: {
      render: (...args: any[]) => number;
      reset: (widgetId?: number) => void;
      getResponse: (widgetId?: number) => string;
    };
  }
}