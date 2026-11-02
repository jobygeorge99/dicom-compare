// Where the login token lives in the browser.
//
// sessionStorage: survives a page refresh, cleared when the tab closes.
// Trade-offs, briefly:
// - localStorage: survives closing the browser, so a stolen token stays
//   useful longer on a shared hospital PC.
// - httpOnly cookie: JavaScript can't read it at all (best against XSS),
//   but needs backend changes and CSRF protection. A good later upgrade.
// sessionStorage is also MSAL's default, the library we'll use for Entra ID.
//
// Every access is wrapped in try/catch: some browsers (private modes,
// strict settings) throw instead of storing.

const KEY = "dicom-compare.token";

export function getToken(): string | null {
  try {
    return sessionStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    sessionStorage.setItem(KEY, token);
  } catch {
    // Storage unavailable: the user stays logged in until refresh.
  }
}

export function clearToken(): void {
  try {
    sessionStorage.removeItem(KEY);
  } catch {
    // Nothing stored, nothing to clear.
  }
}
