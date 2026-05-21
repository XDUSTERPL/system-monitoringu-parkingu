import React from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';

export function Header({
    userName,
    isLoading,
    onLogout,
    onShow,
    onNavigate
}) {

    // BEZPIECZNA FUNKCJA NAWIGACJI
    const safeNavigate = (view) => {
        if (typeof onNavigate === "function") {
            onNavigate(view);
        } else {
            console.warn("onNavigate is not defined");
        }
    };

    return (
        <Navbar bg="dark" variant="dark" expand="lg">
            <Container>

                {/* LOGO */}
                <Navbar.Brand
                    href="#"
                    onClick={(e) => {
                        e.preventDefault();
                        safeNavigate("home");
                    }}
                >
                    PANS 5G
                </Navbar.Brand>

                <Navbar.Toggle aria-controls="basic-navbar-nav" />

                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">

                        <Nav.Link
                            onClick={() => safeNavigate("camoutside")}
                        >
                            Kamera zewnętrzna
                        </Nav.Link>

                    

                        {userName && (
                            <>
                                <Nav.Link
                                    onClick={() => safeNavigate("parkingstats")}
                                >
                                    Statystyki parkingu
                                </Nav.Link>

                                
                            </>
                        )}
                    </Nav>

                    <Nav className="align-items-center">
                        <Navbar.Text className="me-3">
                            Użytkownik: <strong>{userName || "Brak"}</strong>
                        </Navbar.Text>

                        {userName ? (
                            <Button
                                variant="outline-light"
                                size="sm"
                                onClick={onLogout}
                                disabled={isLoading}
                            >
                                Wyloguj
                            </Button>
                        ) : (
                            <Button
                                variant="outline-light"
                                size="sm"
                                onClick={onShow}
                                disabled={isLoading}
                            >
                                Zaloguj
                            </Button>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
}
