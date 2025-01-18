import {useState, useEffect} from "react";
import {
    AppBar, Toolbar, Typography, Box, Button, Select, MenuItem, FormControl, InputLabel, CircularProgress, CssBaseline,
} from "@mui/material";
import {styled} from "@mui/system";
import {FaGithub, FaLinkedin} from "react-icons/fa";
import {ThemeProvider, createTheme} from '@mui/material/styles';
import {CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";

const apiBase = 'http://localhost:5000' || import.meta.env.VITE_API_URL;

const App = () => {
    const [symbols, setSymbols] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState("");
    const [selectedSymbol1, setSelectedSymbol1] = useState("");
    const [companyData, setCompanyData] = useState(null);
    const [companyData1, setCompanyData1] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loading1, setLoading1] = useState(false);
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
    const fetchCompanyData1 = async () => {
        if (!selectedSymbol1) {
            alert("Please select a company.");
            return;
        }
        setLoading1(true);
        try {
            const response = await fetch(`${apiBase}/stocks?symbol=${selectedSymbol1}`);
            const data = await response.json();

            if (response.ok) {
                setCompanyData1(data);
            } else {
                alert(data.error || "No data available for the selected company.");
            }
        } catch (error) {
            console.error("Error fetching company data:", error);
            alert("An error occurred while fetching company data.");
        } finally {
            setLoading1(false);
        }
    };

    // eslint-disable-next-line react/prop-types
    const LineChartComponent = ({symbol}) => {
        const [timeInterval, setTimeInterval] = useState("7");
        const [chartData, setChartData] = useState([]);
        const [loading, setLoading] = useState(false);
        const [error, setError] = useState(null);

        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(
                    `${apiBase}/chart?symbol=${symbol}&interval=${timeInterval}`
                );
                const data = await response.json();

                if (response.ok) {
                    const transformedData = data.dataframe.map((entry) => {
                        const parsedPrice = parseFloat(entry.Last_Trade_Price.replace('.', '').replace(',', '.'));
                        const truncatedPrice = isNaN(parsedPrice) ? null : Math.trunc(parsedPrice); // Truncate decimal values
                        return {
                            price: truncatedPrice,
                        };
                    });
                    const limit = timeInterval === "7" ? 7 : timeInterval === "30" ? 30 : 60;
                    const lastData = transformedData.slice(-limit);
                    const dataWithIndex = lastData.map((entry, index) => ({
                        ...entry,
                        index: index + 1,
                    }));

                    setChartData(dataWithIndex);
                } else {
                    setError("Failed to fetch data for the selected interval.");
                }
                // eslint-disable-next-line no-unused-vars
            } catch (err) {
                setError("An error occurred while fetching chart data.");
            } finally {
                setLoading(false);
            }
        };

        useEffect(() => {
            if (symbol) {
                fetchData();
            }
        }, [symbol, timeInterval]);
        return (
            <Box sx={{
                my: 4,
                backgroundColor: '#444',
                color: '#fff',
                padding: 3,
                borderRadius: 2,
                height: '700px',
            }}>
                <Typography variant="h6" gutterBottom>
                    Price Trend for {symbol}
                </Typography>
                <FormControl fullWidth sx={{mb: 2}}>
                    <Select
                        value={timeInterval}
                        onChange={(e) => setTimeInterval(e.target.value)}
                    >
                        <MenuItem value="7">Last 7 Values</MenuItem>
                        <MenuItem value="30">Last 30 Values</MenuItem>
                        <MenuItem value="60">Last 60 Values</MenuItem>
                    </Select>
                </FormControl>
                {loading ? (
                    <CircularProgress/>
                ) : error ? (
                    <Typography color="error">{error}</Typography>
                ) : (
                    <ResponsiveContainer width="100%" height={500}>
                        <LineChart data={([...chartData]).reverse()} margin={{top: 20, right: 30, left: 20, bottom: 5}}>
                            <CartesianGrid stroke="#ccc" strokeDasharray="3 3"/>
                            <XAxis dataKey="index"
                                   tickCount={chartData.length}
                                   tickFormatter={(value) => `${value + 1}`}  // Sequential index (1, 2, 3, ...)
                            />
                            <YAxis/>
                            <Tooltip/>
                            <Line type="monotone" dataKey="price" stroke="#000000" dot={true} fill="#000000"
                                  fillOpacity={1}/>
                        </LineChart>
                    </ResponsiveContainer>
                )}
            </Box>
        );
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
            <AppBar
                sx={{backgroundColor: 'rgba(40, 40, 40, 1)', color: 'inherit', boxShadow: 'none', position: 'fixed'}}>
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
                        <span className="data"
                              id="latest-symbol">Symbol: {companyData.dataframe[companyData.dataframe.length - 1].Symbol}</span>
                        <span className="data"
                              id="latest-date">Date: {companyData.dataframe[companyData.dataframe.length - 1].Date}</span>
                        <span className="data"
                              id="latest-price">Last Trade Price: {companyData.dataframe[companyData.dataframe.length - 1].Last_Trade_Price}</span>
                        <span className="data"
                              id="latest-change">Change: {companyData.dataframe[companyData.dataframe.length - 1].Change}</span>
                        <span className="data"
                              id="latest-signal">Signal: {companyData.dataframe[companyData.dataframe.length - 1].Overall_signal}</span>
                        <span className="data" id="latest-sentiment">Recommendation: {companyData.sentiment}</span>
                        <span className="data" id="latest-prediction">{companyData.prediction}</span>
                    </p>
                    {error && <p style={{color: "red"}}>{error}</p>}
                </div>
            )}

            <LineChartComponent symbol={selectedSymbol}/>

            <hr/>

            <Box sx={{my: 4}}>
                <FormControl fullWidth>
                    <InputLabel>Select Company to Compare</InputLabel>
                    <Select
                        value={selectedSymbol1}
                        onChange={(e) => setSelectedSymbol1(e.target.value)}
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
                    onClick={fetchCompanyData1}
                    disabled={loading1}
                >
                    {loading1 ? <CircularProgress size={24}/> : "Fetch Data"}
                </Button>
            </Box>
            {companyData1 && (
                <div>
                    <h2>Latest information for: {selectedSymbol1}</h2>
                    <p>
                        <span className="data"
                              id="latest-symbol">Symbol: {companyData1.dataframe[companyData1.dataframe.length - 1].Symbol}</span>
                        <span className="data"
                              id="latest-date">Date: {companyData1.dataframe[companyData1.dataframe.length - 1].Date}</span>
                        <span className="data"
                              id="latest-price">Last Trade Price: {companyData1.dataframe[companyData1.dataframe.length - 1].Last_Trade_Price}</span>
                        <span className="data"
                              id="latest-change">Change: {companyData1.dataframe[companyData1.dataframe.length - 1].Change}</span>
                        <span className="data"
                              id="latest-signal">Signal: {companyData1.dataframe[companyData1.dataframe.length - 1].Overall_signal}</span>
                        <span className="data" id="latest-sentiment">Recommendation: {companyData1.sentiment}</span>
                        <span className="data" id="latest-prediction">{companyData1.prediction}</span>
                    </p>
                    {error && <p style={{color: "red"}}>{error}</p>}
                </div>
            )}
            <LineChartComponent symbol={selectedSymbol1}/>

            <StyledFooter>
                <div className="icon-wrapper">
                    <IconWrapper className="icon">
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
                    <IconWrapper className="icon">
                        <a
                            href="https://www.linkedin.com/in/mihail-sekuloski-179149344/"
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{color: "inherit"}}
                            aria-label="Visit our LinkedIn"
                        >
                            <FaLinkedin size={24}/>
                        </a>
                    </IconWrapper>
                    <IconWrapper className="icon">
                        <a
                            href="https://www.linkedin.com/in/stefan-misoski/"
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{color: "inherit"}}
                            aria-label="Visit our GitHub"
                        >
                            <FaLinkedin size={24}/>
                        </a>
                    </IconWrapper>
                    <IconWrapper className="icon">
                        <a
                            href="https://www.linkedin.com/in/krste-koloski-9a6992304/"
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{color: "inherit"}}
                            aria-label="Visit our GitHub"
                        >
                            <FaLinkedin size={24}/>
                        </a>
                    </IconWrapper>
                </div>

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
