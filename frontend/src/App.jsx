import { useState, useEffect } from "react";
import {
    AppBar, Toolbar, Typography, Box, Button, Select, MenuItem, FormControl, InputLabel, CircularProgress, CssBaseline,
} from "@mui/material";
import { styled } from "@mui/system";
import { FaGithub } from "react-icons/fa";
import { ThemeProvider, createTheme } from '@mui/material/styles';
//import {LinearScale, Title} from "@mui/icons-material";
//import {LineElement} from "@mui/x-charts";
//ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const App = () => {
    const [symbols, setSymbols] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState("");
    const [companyData, setCompanyData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const theme = createTheme({
        palette: {
            mode: 'dark',
        },
    });

    useEffect(() => {
        const loadSymbols = async () => {
            try {
                const response = await fetch(`${apiBase}/symbols`);
                const data = await response.json();
                setSymbols(data);
            } catch (error) {
                console.error("Error fetching symbols:", error);
                setError("Failed to load symbols.");
            }
        };

        loadSymbols();
    }, []);

    const fetchCompanyData = async () => {
        if (!selectedSymbol) {
            alert("Please select a company.");
            return;
        }
        setLoading(true);
        try {
            const response = await fetch(`${apiBase}/stocks?symbol=${selectedSymbol}`);
            const data = await response.json();

            if (response.ok) {
                setCompanyData(data);
            } else {
                alert(data.error || "No data available for the selected company.");
            }
        } catch (error) {
            console.error("Error fetching company data:", error);
            alert("An error occurred while fetching company data.");
        } finally {
            setLoading(false);
        }
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



    return (
        <ThemeProvider theme={theme}>
            <CssBaseline/>
            <AppBar sx={{backgroundColor: 'rgba(40, 40, 40, 1)', color:'inherit', boxShadow: 'none', position: 'fixed'}}>
                <Toolbar>
                    <Typography variant="h6" noWrap>
                        STKViewer
                    </Typography>
                </Toolbar>
            </AppBar>

            <h1>Welcome to STKViewer</h1>
            <Typography variant="p">To get started, select a company from the dropdown menu to view their latest stock
                performance and recommendations.</Typography>

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
                    onClick={fetchCompanyData}
                    disabled={loading}
                >
                    {loading ? <CircularProgress size={24}/> : "Fetch Data"}
                </Button>
            </Box>
            {companyData && (
                <div>
                    <h2>Latest information for: {selectedSymbol}</h2>
                    <p>
                    <span className="data" id="latest-symbol">Symbol: {companyData.dataframe[0].Symbol}</span>
                    <span className="data" id="latest-date">Date: {companyData.dataframe[0].Date}</span>
                    <span className="data" id="latest-price">Last Trade Price: {companyData.dataframe[0].Last_Trade_Price}</span>
                    <span className="data" id="latest-change">Change: {companyData.dataframe[0].Change}</span>
                    <span className="data" id="latest-signal">Signal: {companyData.dataframe[0].Overall_signal}</span>
                    <span className="data" id="latest-sentiment">Recommendation: {companyData.sentiment}</span>
                    <span className="data" id="latest-prediction">{companyData.prediction}</span>
                    </p>
                    {error && <p style={{color: "red"}}>{error}</p>}
                </div>
            )}

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
