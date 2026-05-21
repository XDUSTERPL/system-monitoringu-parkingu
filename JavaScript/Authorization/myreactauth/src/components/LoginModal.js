/**
 * LoginModal.js
 * 
 * Komponent modala okna dialogowego do logowania użytkownika.
 * Zawiera pola na nazwę użytkownika, hasło i przyciski akcji.
 */

import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';



/**
 * Komponent LoginModal - okno modalne do logowania
 * 
 * @param {Object} props - Właściwości komponentu
 * @param {boolean} props.show - Czy modal ma być widoczny
 * @param {Function} props.onHide - Callback do zamknięcia modala
 * @param {string} props.username - Bieżąca wartość pola username
 * @param {string} props.password - Bieżąca wartość pola password
 * @param {string} props.error - Komunikat błędu do wyświetlenia
 * @param {boolean} props.isLoading - Czy trwa operacja logowania
 * @param {Function} props.onUsernameChange - Callback przy zmianie username
 * @param {Function} props.onPasswordChange - Callback przy zmianie password
 * @param {Function} props.onSubmit - Callback przy wysłaniu formularza (parametr: true/false dla OK/Anuluj)
 * @returns {JSX.Element} Komponent modala
 */
export function LoginModal({ 
    show, 
    onHide, 
    username, 
    password, 
    error, 
    isLoading, 
    onUsernameChange, 
    onPasswordChange, 
    onSubmit 
}) {
    

    return (
        <Modal show={show} onHide={onHide}>
            {/* Nagłówek modala */}
            <Modal.Header closeButton>
                <Modal.Title>Logowanie</Modal.Title>
            </Modal.Header>

            {/* Treść modala */}
            <Modal.Body>
                {/* Alert z błędem - wyświetla się tylko jeśli jest błąd */}
                {error && <Alert variant="danger">{error}</Alert>}

                {/* Formularz logowania */}
                <Form>
                    <Form.Group className="auto">
                        <Form.Label>Użytkownik:</Form.Label>
                        <Form.Control
                            type="text"
                            value={username}
                            onChange={(e) => onUsernameChange(e.target.value)}
                            disabled={isLoading}
                            autoFocus
                        />
                    </Form.Group>

                    <Form.Group className="auto">
                        <Form.Label>Hasło:</Form.Label>
                        <Form.Control
                            type="password"
                            value={password}
                            onChange={(e) => onPasswordChange(e.target.value)}
                            disabled={isLoading}
                            // Potwierdzenie formularza klawiszem Enter
                            onKeyDown={(e) => e.key === 'Enter' && onSubmit(true)}
                        />
                    </Form.Group>
                </Form>
            </Modal.Body>

            {/* Stopka modala - przyciski akcji */}
            <Modal.Footer>
                <Button 
                    variant="primary" 
                    onClick={() => onSubmit(true)} 
                    disabled={isLoading}
                >
                    {isLoading ? "Logowanie..." : "OK"}
                </Button>
                <Button 
                    variant="secondary" 
                    onClick={() => onSubmit(false)} 
                    disabled={isLoading}
                >
                    Anuluj
                </Button>
            </Modal.Footer>
        </Modal>
    );
}