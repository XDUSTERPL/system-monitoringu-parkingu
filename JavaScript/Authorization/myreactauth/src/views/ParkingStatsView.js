/**
 * ParkingStatsView.js
 * 
 * Widok statystyk zajęć miejsc parkingowych.
 * Obsługuje 13 trybów wyświetlania statystyk.
 */

import React from 'react';
import Container from 'react-bootstrap/Container';
import Alert from 'react-bootstrap/Alert';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Spinner from 'react-bootstrap/Spinner';

/**
 * Komponent ParkingStatsView - widok statystyk parkingu
 * 
 * @param {Object} props - Właściwości komponentu
 * @param {Object} props.stats - Obiekt ze statystykami
 * @param {boolean} props.isLoading - Czy trwa ładowanie
 * @param {string} props.error - Komunikat błędu
 * @param {string} props.mode - Tryb wyświetlania (day/best_month/best_quarter)
 * @param {string} props.selectedDate - Wybrana data
 * @param {string} props.selectedMonth - Wybrany miesiąc
 * @param {string} props.selectedQuarter - Wybrany kwartał
 * @param {string} props.selectedYear - Wybrany rok
 * @param {Function} props.onModeChange - Callback zmiany trybu
 * @param {Function} props.onDateChange - Callback zmiany daty
 * @param {Function} props.onMonthChange - Callback zmiany miesiąca
 * @param {Function} props.onQuarterChange - Callback zmiany kwartału
 * @param {Function} props.onYearChange - Callback zmiany roku
 * @param {Function} props.onFetchStats - Callback pobierania statystyk
 * @returns {JSX.Element} - Widok statystyk
 */
export function ParkingStatsView({
    stats,
    isLoading,
    error,
    mode,
    selectedDate,
    selectedMonth,
    selectedQuarter,
    selectedYear,
    onModeChange,
    onDateChange,
    onMonthChange,
    onQuarterChange,
    onYearChange,
    onFetchStats
}) {
    /**
     * Obsługa wysłania formularza
     */
    function handleSubmit(event) {
        event.preventDefault();
        onFetchStats();
    }

    /**
     * Renderuje pole wyboru okresu w zależności od trybu
     */
    function renderPeriodInput() {
        switch (mode) {
            case 'day':
                return (
                    <Form.Group className="mb-3">
                        <Form.Label>Wybierz datę:</Form.Label>
                        <Form.Control
                            type="date"
                            value={selectedDate}
                            onChange={(e) => onDateChange(e.target.value)}
                            disabled={isLoading}
                        />
                    </Form.Group>
                );
            
            case 'month':
                return (
                    <Form.Group className="mb-3">
                        <Form.Label>Wybierz miesiąc:</Form.Label>
                        <Form.Control
                            type="month"
                            value={selectedMonth}
                            onChange={(e) => onMonthChange(e.target.value)}
                            disabled={isLoading}
                        />
                    </Form.Group>
                );
            
            case 'quarter':
                return (
                    <Form.Group className="mb-3">
                        <Form.Label>Wybierz kwartał:</Form.Label>
                        <Row>
                            <Col md={6}>
                                <Form.Control
                                    type="number"
                                    placeholder="Rok (np. 2025)"
                                    value={selectedQuarter.split('-')[0]}
                                    onChange={(e) => {
                                        const quarter = selectedQuarter.split('-')[1] || '1';
                                        onQuarterChange(`${e.target.value}-${quarter}`);
                                    }}
                                    disabled={isLoading}
                                />
                            </Col>
                            <Col md={6}>
                                <Form.Select
                                    value={selectedQuarter.split('-')[1]}
                                    onChange={(e) => {
                                        const year = selectedQuarter.split('-')[0];
                                        onQuarterChange(`${year}-${e.target.value}`);
                                    }}
                                    disabled={isLoading}
                                >
                                    <option value="1">Q1 (Sty-Mar)</option>
                                    <option value="2">Q2 (Kwi-Cze)</option>
                                    <option value="3">Q3 (Lip-Wrz)</option>
                                    <option value="4">Q4 (Paź-Gru)</option>
                                </Form.Select>
                            </Col>
                        </Row>
                    </Form.Group>
                );
            
            case 'year':
                return (
                    <Form.Group className="mb-3">
                        <Form.Label>Wybierz rok:</Form.Label>
                        <Form.Control
                            type="number"
                            placeholder="Rok (np. 2025)"
                            value={selectedYear}
                            onChange={(e) => onYearChange(e.target.value)}
                            disabled={isLoading}
                        />
                    </Form.Group>
                );
            
            case 'best_day_month':
                return (
                    <Form.Group className="mb-3">
                        <Form.Label>Wybierz miesiąc:</Form.Label>
                        <Form.Control
                            type="month"
                            value={selectedMonth}
                            onChange={(e) => onMonthChange(e.target.value)}
                            disabled={isLoading}
                        />
                        <Form.Text className="text-muted">
                            Znajdzie dzień z największą liczbą zajęć w tym miesiącu.
                        </Form.Text>
                    </Form.Group>
                );
            
            case 'best_day_quarter':
                return (
                    <Form.Group className="mb-3">
                        <Form.Label>Wybierz kwartał:</Form.Label>
                        <Row>
                            <Col md={6}>
                                <Form.Control
                                    type="number"
                                    placeholder="Rok (np. 2025)"
                                    value={selectedQuarter.split('-')[0]}
                                    onChange={(e) => {
                                        const quarter = selectedQuarter.split('-')[1] || '1';
                                        onQuarterChange(`${e.target.value}-${quarter}`);
                                    }}
                                    disabled={isLoading}
                                />
                            </Col>
                            <Col md={6}>
                                <Form.Select
                                    value={selectedQuarter.split('-')[1]}
                                    onChange={(e) => {
                                        const year = selectedQuarter.split('-')[0];
                                        onQuarterChange(`${year}-${e.target.value}`);
                                    }}
                                    disabled={isLoading}
                                >
                                    <option value="1">Q1 (Sty-Mar)</option>
                                    <option value="2">Q2 (Kwi-Cze)</option>
                                    <option value="3">Q3 (Lip-Wrz)</option>
                                    <option value="4">Q4 (Paź-Gru)</option>
                                </Form.Select>
                            </Col>
                        </Row>
                        <Form.Text className="text-muted">
                            Znajdzie dzień z największą liczbą zajęć w tym kwartale.
                        </Form.Text>
                    </Form.Group>
                );
            
            case 'best_day_year':
            case 'best_month_year':
            case 'best_quarter_year':
                return (
                    <Form.Group className="mb-3">
                        <Form.Label>Wybierz rok:</Form.Label>
                        <Form.Control
                            type="number"
                            placeholder="Rok (np. 2025)"
                            value={selectedYear}
                            onChange={(e) => onYearChange(e.target.value)}
                            disabled={isLoading}
                        />
                        <Form.Text className="text-muted">
                            {mode === 'best_day_year' && 'Znajdzie dzień z największą liczbą zajęć w tym roku.'}
                            {mode === 'best_month_year' && 'Znajdzie miesiąc z największą liczbą zajęć w tym roku.'}
                            {mode === 'best_quarter_year' && 'Znajdzie kwartał z największą liczbą zajęć w tym roku.'}
                        </Form.Text>
                    </Form.Group>
                );
            
            case 'best_day':
            case 'best_month':
            case 'best_quarter':
            case 'best_year':
                return (
                    <Alert variant="info">
                        {mode === 'best_day' && 'Znajdzie najlepszy dzień ze wszystkich danych w bazie.'}
                        {mode === 'best_month' && 'Znajdzie najlepszy miesiąc ze wszystkich danych w bazie.'}
                        {mode === 'best_quarter' && 'Znajdzie najlepszy kwartał ze wszystkich danych w bazie.'}
                        {mode === 'best_year' && 'Znajdzie najlepszy rok ze wszystkich danych w bazie.'}
                    </Alert>
                );
            
            default:
                return null;
        }
    }

    return (
        <Container>
            {/* Formularz wyboru okresu */}
            <Card className="mb-4">
                <Card.Body>
                    <Form onSubmit={handleSubmit}>
                        {/* Wybór trybu */}
                        <Form.Group className="mb-3">
                            <Form.Label>Tryb wyświetlania:</Form.Label>
                            <Form.Select
                                value={mode}
                                onChange={(e) => onModeChange(e.target.value)}
                                disabled={isLoading}
                            >
                                <optgroup label="Konkretny okres">
                                    <option value="day">Konkretny dzień</option>
                                    <option value="month">Konkretny miesiąc</option>
                                    <option value="quarter">Konkretny kwartał</option>
                                    <option value="year">Konkretny rok</option>
                                </optgroup>
                                <optgroup label="Najlepszy w okresie">
                                    <option value="best_day_month">Najlepszy dzień w miesiącu</option>
                                    <option value="best_day_quarter">Najlepszy dzień w kwartale</option>
                                    <option value="best_day_year">Najlepszy dzień w roku</option>
                                    <option value="best_month_year">Najlepszy miesiąc w roku</option>
                                    <option value="best_quarter_year">Najlepszy kwartał w roku</option>
                                </optgroup>
                                <optgroup label="Najlepszy ogólnie">
                                    <option value="best_day">Najlepszy dzień (wszystkie dane)</option>
                                    <option value="best_month">Najlepszy miesiąc (wszystkie dane)</option>
                                    <option value="best_quarter">Najlepszy kwartał (wszystkie dane)</option>
                                    <option value="best_year">Najlepszy rok (wszystkie dane)</option>
                                </optgroup>
                            </Form.Select>
                        </Form.Group>

                        {/* Pole wyboru okresu (zmienia się w zależności od trybu) */}
                        {renderPeriodInput()}

                        {/* Przycisk pobierania danych */}
                        <Button 
                            variant="primary" 
                            type="submit" 
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <Spinner
                                        as="span"
                                        animation="border"
                                        size="sm"
                                        role="status"
                                        aria-hidden="true"
                                        className="me-2"
                                    />
                                    Ładowanie...
                                </>
                            ) : (
                                'Pokaż statystyki'
                            )}
                        </Button>
                    </Form>
                </Card.Body>
            </Card>

            {/* Wyświetlanie błędów */}
            {error && (
                <Alert variant="danger">
                    {error}
                </Alert>
            )}

            {/* Wyświetlanie wyników */}
            {stats && (
                <>
                    {/* Podsumowanie */}
                    <Card className="mb-4">
                        <Card.Header as="h5">Podsumowanie</Card.Header>
                        <Card.Body>
                            <Row>
                                <Col md={6}>
                                    <p><strong>Okres:</strong> {stats.period}</p>
                                    {stats.best_day && (
                                        <p><strong>Najlepszy dzień:</strong> {stats.best_day}</p>
                                    )}
                                    {stats.best_month && (
                                        <p><strong>Najlepszy miesiąc:</strong> {stats.best_month}</p>
                                    )}
                                    {stats.best_quarter && (
                                        <p><strong>Najlepszy kwartał:</strong> {stats.best_quarter}</p>
                                    )}
                                    {stats.best_year && (
                                        <p><strong>Najlepszy rok:</strong> {stats.best_year}</p>
                                    )}
                                </Col>
                                <Col md={6}>
                                    <p><strong>Łączna liczba zajęć:</strong> {stats.total_occupations}</p>
                                    {stats.start_date && stats.end_date && (
                                        <p>
                                            <strong>Zakres czasowy:</strong><br />
                                            {stats.start_date} - {stats.end_date}
                                        </p>
                                    )}
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>

                    {/* Tabela z miejscami */}
                    {stats.spots && stats.spots.length > 0 ? (
                        <Card>
                            <Card.Header as="h5">Statystyki według miejsc</Card.Header>
                            <Card.Body>
                                <Table striped bordered hover responsive>
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Numer miejsca</th>
                                            <th>Liczba zajęć</th>
                                            <th>% z całości</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {stats.spots.map((spot, index) => (
                                            <tr key={spot.spot_number}>
                                                <td>{index + 1}</td>
                                                <td>Miejsce #{spot.spot_number}</td>
                                                <td>{spot.occupations}</td>
                                                <td>
                                                    {((spot.occupations / stats.total_occupations) * 100).toFixed(1)}%
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </Table>
                            </Card.Body>
                        </Card>
                    ) : (
                        <Alert variant="info">
                            Brak danych dla wybranego okresu.
                        </Alert>
                    )}
                </>
            )}
        </Container>
    );
}