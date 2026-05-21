import { useState } from "react";
import { apiClient } from "../api/apiClient";

export function useParkingStats() {

    const [stats, setStats] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const [mode, setMode] = useState("day");

    const [selectedDate, setSelectedDate] = useState(getTodayString());
    const [selectedMonth, setSelectedMonth] = useState(getCurrentMonthString());
    const [selectedQuarter, setSelectedQuarter] = useState(getCurrentQuarterString());
    const [selectedYear, setSelectedYear] = useState(getCurrentYearString());

    function getTodayString() {

        const today = new Date();
        return today.toISOString().split("T")[0];

    }

    function getCurrentMonthString() {

        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");

        return `${year}-${month}`;

    }

    function getCurrentQuarterString() {

        const today = new Date();
        const year = today.getFullYear();
        const quarter = Math.floor(today.getMonth() / 3) + 1;

        return `${year}-${quarter}`;

    }

    function getCurrentYearString() {

        return String(new Date().getFullYear());

    }

    async function fetchStats() {

        setIsLoading(true);
        setError("");

        try {

            let params = { mode };

            if (mode === "day") params.date = selectedDate;
            if (mode === "month") params.month = selectedMonth;
            if (mode === "quarter") params.quarter = selectedQuarter;
            if (mode === "year") params.year = selectedYear;

            if (mode === "best_day_month") params.month = selectedMonth;
            if (mode === "best_day_quarter") params.quarter = selectedQuarter;
            if (mode === "best_day_year" || mode === "best_month_year" || mode === "best_quarter_year") params.year = selectedYear;

            const response = await apiClient.get("/get_parking_stats/", { params });

            setStats(response.data);

        } catch (err) {

            setError(`Błąd połączenia: ${err.message}`);
            setStats(null);

        } finally {

            setIsLoading(false);

        }
    }

    return {
        stats,
        isLoading,
        error,
        mode,
        selectedDate,
        selectedMonth,
        selectedQuarter,
        selectedYear,
        setMode,
        setSelectedDate,
        setSelectedMonth,
        setSelectedQuarter,
        setSelectedYear,
        fetchStats
    };
}