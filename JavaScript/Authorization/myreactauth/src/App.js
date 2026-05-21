/**
 * App.js
 * 
 * Główny komponent aplikacji.
 * Zarządza stanem globalnym, routingiem między widokami, autentykacją
 * i wyświetlaniem modala logowania.
 */

import React, { useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { LoginModal } from './components/LoginModal';
import { HomeView } from './views/HomeView';
import { CameraOutsideView } from './views/CameraOutsideView';
import { ParkingStatsView } from './views/ParkingStatsView';

import { useAuth } from './hooks/useAuth';
import { useParkingStats } from './hooks/useParkingStats';
import Container from 'react-bootstrap/Container';

/**
 * Główny komponent aplikacji TestReact
 * 
 * Struktura:
 * - Header (navbar z nawigacją)
 * - Główna zawartość (renderowana na podstawie activeView)
 * - LoginModal (modal do logowania)
 * - Footer (stopka)
 * 
 * @returns {JSX.Element} Całe drzewo komponentów aplikacji
 */
export default function TestReact() {
    // Stan widoku (home, camoutside, parkingstats)
    const [activeView, setActiveView] = useState("home");

    // Stan widoczności modala logowania
    const [modalShow, setModalShow] = useState(false);

    // Stan pól formularza w modalu logowania
    const [modalNewUsername, setModalNewUsername] = useState("");
    const [modalNewPassword, setModalNewPassword] = useState("");

    // Hook do zarządzania autentykacją
    const auth = useAuth();


    // Hook do zarządzania statystykami parkingu
    const parkingStats = useParkingStats();

    /**
     * Otwiera modal logowania i czyści poprzednie dane
     */
    function handleShow() {
        setModalNewUsername("");
        setModalNewPassword("");
        auth.setLoginError("");
        setModalShow(true);
    }

    /**
     * Zamyka modal logowania
     */
    function handleCloseHeader() {
        setModalShow(false);
        auth.setLoginError("");
    }

    /**
     * Obsługuje wysłanie formularza logowania
     * 
     * @param {boolean} isSubmit - true jeśli użytkownik kliknął OK, false jeśli Anuluj
     */
    async function handleModalClose(isSubmit) {
        if (isSubmit) {
            // Próba walidacji logowania
            const success = await auth.validateLogin(modalNewUsername, modalNewPassword);
            if (success) {
                // Logowanie udane - zamykanie modala i czyszczenie pól
                setModalShow(false);
                setModalNewUsername("");
                setModalNewPassword("");
            }
        } else {
            // Użytkownik kliknął Anuluj
            handleCloseHeader();
        }
    }

    /**
     * Wylogowuje użytkownika i wraca na stronę główną
     */
    function handleLogout() {
        auth.handleLogout();
        setActiveView("home");
    }

    /**
     * Zmienia bieżący widok
     * 
     * @param {string} view - Nazwa widoku (home, camoutside, parkingstats)
     */
    function handleNavigate(view) {
        setActiveView(view);
    }

    /**
     * Renderuje zawartość na podstawie bieżącego widoku
     * 
     * @returns {JSX.Element} Komponent widoku
     */
    const renderView = () => {
        switch (activeView) {
            case "home":
                return <HomeView userName={auth.userName} onNavigate={handleNavigate} />;

            case "camoutside":
                return <CameraOutsideView onNavigate={handleNavigate} />;

            case "parkingstats":
                return (
                    <ParkingStatsView
                        stats={parkingStats.stats}
                        isLoading={parkingStats.isLoading}
                        error={parkingStats.error}
                        mode={parkingStats.mode}
                        selectedDate={parkingStats.selectedDate}
                        selectedMonth={parkingStats.selectedMonth}
                        selectedQuarter={parkingStats.selectedQuarter}
                        selectedYear={parkingStats.selectedYear}
                        onModeChange={parkingStats.setMode}
                        onDateChange={parkingStats.setSelectedDate}
                        onMonthChange={parkingStats.setSelectedMonth}
                        onQuarterChange={parkingStats.setSelectedQuarter}
                        onYearChange={parkingStats.setSelectedYear}
                        onFetchStats={() => parkingStats.fetchStats(auth.credentialsRef.current)}
                    />
                );

            

            default:
                return null;
        }
    };

    // Struktura główna aplikacji
    return (
        <div className="d-flex flex-column min-vh-100">
            {/* Górny pasek nawigacji */}
            <Header
                userName={auth.userName}
                isLoading={auth.isLoading}
                onLogout={handleLogout}
                onShow={handleShow}
                onNavigate={handleNavigate}
            />

            {/* Główna zawartość strony */}
            <Container
                className="app-content flex-fill d-flex flex-column"
                style={{ marginTop: '1rem', overflow: 'hidden' }}
            >
                {renderView()}
            </Container>

            {/* Modal do logowania */}
            <LoginModal
                show={modalShow}
                onHide={handleCloseHeader}
                username={modalNewUsername}
                password={modalNewPassword}
                error={auth.loginError}
                isLoading={auth.isLoading}
                onUsernameChange={setModalNewUsername}
                onPasswordChange={setModalNewPassword}
                onSubmit={handleModalClose}
            />

            {/* Stopka aplikacji */}
            <Footer />
        </div>
    );
}

