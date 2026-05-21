/**
 * CameraOutsideView.js
 * 
 * Widok wyświetlający transmisję z kamery zewnętrznej.
 * Pobiera stream video z serwera i wyświetla go w pełnej wysokości.
 */

import React from 'react';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';

/**
 * Komponent CameraOutsideView - widok kamery zewnętrznej
 * 
 * @param {Object} props - Właściwości komponentu
 * @param {Function} props.onNavigate - Callback do nawigacji
 * @returns {JSX.Element} - Widok kamery
 */
export function CameraOutsideView({ onNavigate }) {
    return (
        <Container className="flex-fill d-flex flex-column">
            <div
                className="w-100 d-flex justify-content-center align-items-center"
                style={{ maxHeight: 'calc(100vh - 200px)', overflow: 'hidden' }}
            >
                <img
                    src="http://127.0.0.1:8000/video_feed/"
                    alt="Camera Stream"
                    className="img-fluid"
                    style={{ maxHeight: '100%', width: 'auto', display: 'block' }}
                />
            </div>

            
        </Container>
    );
}