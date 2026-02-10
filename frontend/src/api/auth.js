import api from "./axios";

export async function logoutRequest() {
  try {
    await api.post("/auth/logout", {}, { skipAuthRedirect: true });
  } catch (e) {
    // ignore logout errors
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  }
}

// // Auth API
// const BASE_URL =
//   import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";


// // ---------- SIGNUP ----------
// export async function signupRequest(formData) {
//   const res = await fetch(`${BASE_URL}/auth/signup`, {
//     method: "POST",
//     body: formData, // ✅ FormData supports file upload
//   });

//   const data = await res.json().catch(() => ({}));

//   if (!res.ok) {
//     throw new Error(data?.message || "Signup failed");
//   }

//   return data;
// }

// // ---------- LOGIN ----------
// export async function loginRequest(payload) {
//   const res = await fetch(`${BASE_URL}/auth/login`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify(payload), // ✅ JSON for login
//   });

//   const data = await res.json().catch(() => ({}));

//   if (!res.ok) {
//     throw new Error(data?.message || "Login failed");
//   }

//   return data;
// }
// /// ---------- LOGOUT ----------
// export async function logoutRequest() {
//   const token = localStorage.getItem("access_token");

//   try {
//     await fetch(`${BASE_URL}/auth/logout`, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         Authorization: token ? `Bearer ${token}` : "",
//       },
//     });
//   } catch (error) {
//     console.log("Backend logout failed (safe to ignore):", error);
//   } finally {
//     // Always clear local auth data
//     localStorage.removeItem("access_token");
//     localStorage.removeItem("user");
//   }
// }
