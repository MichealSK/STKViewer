import { useState, useEffect } from "react";
import {
    AppBar, Toolbar, Typography, Box, Button, Select, MenuItem, FormControl, InputLabel, CircularProgress, CssBaseline,
} from "@mui/material";
//import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import axios from "axios";
import { styled } from "@mui/system";
import { FaGithub } from "react-icons/fa";
import { ThemeProvider, createTheme } from '@mui/material/styles';
//import {CategoryScale, Chart as ChartJS, PointElement} from "chart.js";
//import {LinearScale, Title} from "@mui/icons-material";
//import {LineElement} from "@mui/x-charts";



//ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const App = () => {
    const [symbols, setSymbols] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState("");
    const [stockData, setStockData] = useState(null);
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(false);

    const theme = createTheme({
        palette: {
            mode: 'dark', // Set the default mode to dark
        },
    });

    // Fetch symbols on component mount
    useEffect(() => {
        axios.get("http://localhost:5000/symbols")
            .then(response => setSymbols(response.data))
            .catch(error => console.error("Error fetching symbols:", error));
    }, []);

    const handleFetchData = () => {
        if (!selectedSymbol) return;

        setLoading(true);
        // TODO - remove chart stuff, focus only on filling the paragraphs
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

    const StyledFooter = styled(Box)(() => ({
        position: "fixed",
        bottom: 0,
        left: 0,
        width: "100%",
        padding: "1rem",
        backgroundColor: "rgba(64, 64, 64, 1)",
        color: "#fff",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        zIndex: 1000,
    }));

    const CenteredTypography = styled(Typography)(() => ({
        position: "absolute",
        left: "50%",
        transform: "translateX(-50%)",
    }));

    const IconWrapper = styled(Box)(() => ({
        cursor: "pointer",
        transition: "transform 0.2s ease-in-out",
        "&:hover": {
            transform: "scale(1.1)"
        }
    }));

    const StyledButton = styled(Button)(() => ({
        backgroundColor: "#000",
        color: "#fff",
        "&:hover": {
            backgroundColor: "#f9f9f9",
            color: "#000"
        }
    }));

    const ChartContainer = styled(Box)(() => ({
        width: "100%",
        height: "400px",
        padding: "20px",
        marginBottom: "60px"
    }));


    return (
        <ThemeProvider theme={theme}>
            <CssBaseline/>
            <AppBar sx={{backgroundColor: 'rgba(64, 64, 64, 1)', boxShadow: 'none' , position: 'fixed'}}>
                <Toolbar>
                    <Typography variant="h6" noWrap>
                        STKViewer
                    </Typography>
                </Toolbar>
            </AppBar>

            {/* Main Content */}
            <Box sx={{my: 4}}>
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
                    color="inherit"
                    sx={{mt: 2}}
                    onClick={handleFetchData}
                    disabled={loading}
                >
                    {loading ? <CircularProgress size={24}/> : "Fetch Data"}
                </Button>
            </Box>

            <Box sx={{my: 4}}>
                <h2>Latest Information:</h2>
                <p id="latest-symbol">Symbol: </p>
                <p id="latest-date">Date: </p>
                <p id="latest-price">Last Trade Price: </p>
                <p id="latest-change">Change: </p>
                <p id="latest-signal">Signal: </p>
                <p id="latest-sentiment">Recommendation: </p>
                <p id="latest-prediction">Prediction: </p>
                <p></p>
                <p></p>
                <p></p>
                <p></p>
            </Box>

            {/*<ChartContainer>
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
            </ChartContainer>*/}

            <StyledFooter>
                <IconWrapper>
                    <a
                        href="https://github.com/MichealSK/STKViewer"
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{color: "inherit"}}
                        aria-label="Visit our GitHub"
                    >
                        <FaGithub size={24}/>
                    </a>
                </IconWrapper>

                <CenteredTypography
                    variant="h6"
                    component="div"
                    align="center"
                >
                    STKViewer
                </CenteredTypography>

                <StyledButton
                    variant="contained"
                    href="https://github.com/MichealSK/STKViewer/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Visit Material-UI website"
                >
                    Report an issue
                </StyledButton>
            </StyledFooter>
        </ThemeProvider>
    );
};

export default App;
