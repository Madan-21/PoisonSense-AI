// Auth API
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// ---------- SIGNUP ----------
export async function signupRequest(formData) {
  const res = await fetch(`${BASE_URL}/auth/signup`, {
    method: "POST",
    body: formData, // ✅ FormData supports file upload
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data?.message || "Signup failed");
  }

  return data;
}

// ---------- LOGIN ----------
export async function loginRequest(payload) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload), // ✅ JSON for login
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data?.message || "Login failed");
  }

  return data;
}
