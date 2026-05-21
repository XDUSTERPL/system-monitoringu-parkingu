import { useState, useRef, useEffect } from "react";
import { apiClient, setGetCredentials } from "../api/apiClient";

export function useAuth() {
    const [userName, setUserName] = useState("");
    const [loginError, setLoginError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const credentialsRef = useRef({
        username: "",
        password: ""
    });

    useEffect(() => {
        setGetCredentials(() => credentialsRef.current);
    }, []);

    async function validateLogin(username, password) {
        if (!username.trim() || !password.trim()) {
            setLoginError("Użytkownik i hasło nie mogą być puste");
            return false;
        }

        setIsLoading(true);
        setLoginError("");

        try {
            const response = await apiClient.get("/test_auth/", {
                auth: {
                    username: username,
                    password: password
                }
            });

            if (response.status === 200) {
                credentialsRef.current = {
                    username,
                    password
                };

                setUserName(username);
                console.log("Zalogowano");

                return true;
            }

        } catch (error) {
            setLoginError("Błędna nazwa użytkownika lub hasło");
            credentialsRef.current = {
                username: "",
                password: ""
            };
            return false;

        } finally {
            setIsLoading(false);
        }
    }

    function handleLogout() {
        setUserName("");
        setLoginError("");
        credentialsRef.current = {
            username: "",
            password: ""
        };

        console.log("Wylogowano");
    }

    return {
        userName,
        loginError,
        isLoading,
        credentialsRef,
        validateLogin,
        handleLogout,
        setLoginError
    };
}