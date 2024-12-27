import './App.css'
import { CssBaseline, AppBar, Toolbar, Typography, Box, Drawer, List, ListItem, ListItemText, Container } from '@mui/material';
import { Home, Settings, Info } from '@mui/icons-material';
import {useEffect, useState} from "react";
import axios from "axios";


function App() {
    const [data, setData] = useState(null);

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/api/data')
            .then(response => {
                setData(response.data);
            })
            .catch(error => {
                console.error("There was an error fetching the data!", error);
            });
    }, []);


  return (
      <>
          <AppBar position="fixed">
              <Toolbar>
                  <Typography variant="h6" noWrap>
                      STKViewer
                  </Typography>
              </Toolbar>
          </AppBar>

          <h1>STKViewer</h1>
          <label htmlFor="company">Select Company:</label>
          <select id="company">
              <option value="">Select a company...</option>
          </select>
          <button onClick="fetchCompanyData()">Get Data</button>
          <table id="data-table" border="1">
              <thead>
              <tr>
                  <th>Symbol</th>
                  <th>Date</th>
                  <th>Last Trade Price</th>
                  <th>Max</th>
                  <th>Min</th>
                  <th>Average Price</th>
                  <th>Change</th>
                  <th>Volume</th>
                  <th>Best Turnover</th>
                  <th>Total Turnover</th>
              </tr>
              </thead>
              <tbody></tbody>
          </table>



      </>
  )
}

export default App
