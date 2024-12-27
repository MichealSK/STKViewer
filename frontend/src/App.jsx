import { useState, useEffect } from "react";
import {
    AppBar,
    Toolbar,
    Typography,
    Box,
    Button,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    CircularProgress,
} from "@mui/material";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import axios from "axios";
import { styled } from "@mui/system";
import { FaGithub } from "react-icons/fa";
import {CategoryScale, Chart as ChartJS, PointElement} from "chart.js";
import {LinearScale, Title} from "@mui/icons-material";
import {LineElement} from "@mui/x-charts";



ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const App = () => {
    const [symbols, setSymbols] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState("");
    const [stockData, setStockData] = useState(null);
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(false);

    // Fetch symbols on component mount
    useEffect(() => {
        axios.get("http://localhost:5000/symbols")
            .then(response => setSymbols(response.data))
            .catch(error => console.error("Error fetching symbols:", error));
    }, []);

    const handleFetchData = () => {
        if (!selectedSymbol) return;

        setLoading(true);
        axios.get(`http://localhost:5000/stocks?symbol=${selectedSymbol}&start_date=2023-01-01&end_date=2023-12-31`)
            .then(response => {
                const fetchedData = response.data;

                // Extract dates and prices for the chart
                const dates = fetchedData.map(item => item.Date); // Ensure field matches backend
                const prices = fetchedData.map(item => parseFloat(item.Last_Trade_Price)); // Convert string to number

                // Update state for chart
                setStockData(fetchedData);
                setChartData({
                    labels: dates,
                    datasets: [
                        {
                            label: `${selectedSymbol} Stock Prices`,
                            data: prices,
                            borderColor: "rgba(75,192,192,1)",
                            fill: false,
                            tension: 0.1, // Smooth line
                        },
                    ],
                });
            })
            .catch(error => console.error("Error fetching stock data:", error))
            .finally(() => setLoading(false));
    };

    const StyledFooter = styled(Box)(({ theme }) => ({
        position: "fixed",
        bottom: 0,
        left: 0,
        width: "100%",
        padding: "1rem",
        backgroundColor: "#1976d2",
        color: "#fff",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        zIndex: 1000
    }));

    const IconWrapper = styled(Box)(({ theme }) => ({
        cursor: "pointer",
        transition: "transform 0.2s ease-in-out",
        "&:hover": {
            transform: "scale(1.1)"
        }
    }));

    const StyledButton = styled(Button)(({ theme }) => ({
        backgroundColor: "#fff",
        color: "#1976d2",
        "&:hover": {
            backgroundColor: "#e3f2fd"
        }
    }));

    const ChartContainer = styled(Box)(({ theme }) => ({
        width: "100%",
        height: "400px",
        padding: "20px",
        marginBottom: "60px"
    }));


    return (
        <>
            <AppBar position="fixed">
                <Toolbar>
                    <Typography variant="h6" noWrap>
                        STKViewer
                    </Typography>
                </Toolbar>
            </AppBar>

            {/* Main Content */}
            <Box sx={{ my: 4 }}>
                <FormControl fullWidth>
                    <InputLabel>Select Company</InputLabel>
                    <Select
                        value={selectedSymbol}
                        onChange={(e) => setSelectedSymbol(e.target.value)}
                    >
                        {symbols.map((symbol, index) => (
                            <MenuItem key={index} value={symbol}>{symbol}</MenuItem>
                        ))}
                    </Select>
                </FormControl>

                <Button
                    variant="contained"
                    color="primary"
                    sx={{ mt: 2 }}
                    onClick={handleFetchData}
                    disabled={loading}
                >
                    {loading ? <CircularProgress size={24} /> : "Fetch Data"}
                </Button>
            </Box>

            <ChartContainer>
                <Typography variant="h4" gutterBottom>
                    Stock Price Trend
                </Typography>
                {loading ? (
                    <Typography>Loading...</Typography>
                ) : error ? (
                    <Typography color="error">{error}</Typography>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                            data={stockData.length ? stockData : dummyData}
                            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="value"
                                stroke="#1976d2"
                                strokeWidth={2}
                                dot={{ r: 4 }}
                                activeDot={{ r: 8 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                )}
            </ChartContainer>

            <StyledFooter>
                <IconWrapper>
                    <a
                        href="https://github.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: "inherit" }}
                        aria-label="Visit GitHub"
                    >
                        <FaGithub size={24} />
                    </a>
                </IconWrapper>

                <Typography
                    variant="h6"
                    component="div"
                    sx={{
                        fontWeight: "bold",
                        letterSpacing: 1
                    }}
                >
                    STKViewer
                </Typography>

                <StyledButton
                    variant="contained"
                    href="https://mui.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Visit Material-UI website"
                >
                    Visit MUI
                </StyledButton>
            </StyledFooter>
        </>
    );
};

export default App;
