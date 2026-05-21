import axios from "axios";

let getCredentials = () => ({ username: "", password: "" });

export function setGetCredentials(callback) {
    getCredentials = callback;
}

export const apiClient = axios.create({
    baseURL: "http://localhost:8000/api"
});

apiClient.interceptors.request.use((config) => {
    const credentials = getCredentials();

    const protectedEndpoints = [
        "/test_auth/",
        "/get_parking_stats/"
    ];

    const requiresAuth = protectedEndpoints.some(endpoint =>
        config.url.includes(endpoint)
    );

    if (credentials && credentials.username && requiresAuth) {
        const token = btoa(`${credentials.username}:${credentials.password}`);
        config.headers.Authorization = `Basic ${token}`;
    }

    return config;
});