/**
 * Centralized Console Logging & Production Environment Protection
 *
 * In production (import.meta.env.PROD):
 * - Suppresses console.log, console.debug, and console.info to prevent sensitive data leaks.
 * - Wraps console.error and console.warn with sanitized formatting.
 *
 * In development:
 * - Retains full console logging fidelity for debugging.
 */

const isProd = import.meta.env.PROD;

export const initLogger = () => {
  if (isProd) {
    // Retain internal references if needed for remote telemetry
    const noop = () => {};

    // Suppress non-critical logs
    window.console.log = noop;
    window.console.debug = noop;
    window.console.info = noop;

    // Sanitize warn and error outputs
    const originalWarn = window.console.warn;
    const originalError = window.console.error;

    window.console.warn = (...args) => {
      // Allow single-line sanitized warnings
      if (typeof args[0] === 'string' && !args[0].includes('password') && !args[0].includes('token')) {
        originalWarn.call(window.console, args[0]);
      }
    };

    window.console.error = (...args) => {
      // Prevent full stack traces and sensitive payload leaks
      const sanitized = args.map((arg) => {
        if (arg instanceof Error) {
          return `[AppError] ${arg.name}: ${arg.message}`;
        }
        if (typeof arg === 'string') {
          return arg.replace(/(Bearer\s+)[A-Za-z0-9\-_.]+/gi, '$1[REDACTED]');
        }
        return '[Object]';
      });
      originalError.call(window.console, ...sanitized);
    };
  }
};

export default { initLogger };

