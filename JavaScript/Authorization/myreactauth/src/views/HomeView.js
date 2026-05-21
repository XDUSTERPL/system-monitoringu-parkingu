/**
 * HomeView.js
 * 
 * Widok główny aplikacji - strona startowa.
 * Wyświetla przyciski szybkiego dostępu do poszczególnych funkcji.
 */

import React from 'react';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';


/**
 * Komponent HomeView - widok główny aplikacji
 * 
 * @param {Object} props - Właściwości komponentu
 * @param {string} props.userName - Nazwa zalogowanego użytkownika
 * @param {Function} props.onNavigate - Callback do nawigacji
 * @returns {JSX.Element} - Widok główny
 */
export function HomeView({ userName, onNavigate }) {

    return (
        <Container className="text-center">
            {/* Główny panel */}
            <div className="p-4 bg-light rounded">
                <h1>PANS 5G - System monitoringu</h1>
                <p className="lead">
                    Szybki dostęp do kamery. Zaloguj się, aby uzyskać dostęp do statystyk.
                </p>

                {/* Przyciski nawigacyjne */}
                <div className="d-flex justify-content-center gap-2 my-3">
                    <Button 
                        variant="primary" 
                        onClick={() => onNavigate("camoutside")}
                    >
                        Podgląd kamery
                    </Button>
                    
                  
                   
                    {userName && (
                        <Button 
                            variant="success" 
                            onClick={() => onNavigate("parkingstats")}
                        >
                            Statystyki parkingu
                        </Button>
                    )}
                    
                </div>
            </div>
        </Container>
    );
}