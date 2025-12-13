// Install jwt-decode: npm install jwt-decode
import { jwtDecode } from 'jwt-decode';

// Define a function getUserRole()
// It should read the 'access_token' from localStorage.
// If no token exists, return null.
// Use jwtDecode(token) to get the payload. The role is stored under 'role'.
// Return the role string (e.g., 'admin' or 'customer').
export function getUserRole() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        return null;
    }
    try {
        const decoded = jwtDecode(token);
        return decoded.role || null;
    } catch (error) {
        console.error("Invalid token:", error);
        return null;
    }
}
