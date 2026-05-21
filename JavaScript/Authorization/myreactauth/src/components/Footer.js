import React from 'react';
import Container from 'react-bootstrap/Container';

/**
 * Stopka aplikacji z informacjami o prawach autorskich i autorach
 */
export function Footer() {
    return (
        <footer className="mt-auto bg-dark text-white py-3">
            <Container style={{ textAlign: 'center' }}>
                <p className="mb-0">
                    &copy; 2025 PANS 5G - System monitoringu.
                </p>
            </Container>
        </footer>
    );
}