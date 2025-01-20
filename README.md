## STKViewer

**STKViewer** (Stock Viewer) is a project created for storing, archiving and presenting historical stock data from the [Macedonian Stock Exchange](https://www.mse.mk/) from the last 10 years.

IP of the STKViewer AWS Website: http://51.20.107.165/

It compiles all the stock data into a .db file that can be viewed using a standard database viewer.
If you want to re-scrape the website, please make sure both stocks_history.db and last_date.txt are deleted.

The UI includes a graph that displays the cost of the stocks over time. Additional information about each company is displayed, including reccomendations on whether or not to buy/hold/sell stocks according to technical, natural language and neural network analysis.