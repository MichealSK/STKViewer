import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_symbols():
    url = "https://www.mse.mk/en/stats/symbolhistory/TEL"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        dropdown = soup.find("select", {"id": "Code"})
        symbols = []

        for option in dropdown.find_all("option"):
            symbol = option.get("value")
            if not any(char.isdigit() for char in symbol): symbols.append(symbol)
        return symbols
    else:
        print("Cannot reach site.")
        return []


def get_stock_data(symbol, start_date, end_date):
    url = f"https://www.mse.mk/en/stats/symbolhistory/{symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    form_data = {"FromDate": start_date, "ToDate": end_date, "Code": symbol}
    response = requests.get(url, headers, data=form_data)
    data = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "resultsTable"})
        if table:
            for row in table.find_all("tr")[1:]:
                entry_data = row.find_all("td")

                entry = {"date": datetime.strptime(entry_data[0].text.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")}
                prices = ["last_price", "max", "min", "avg", "change", "volume", "best_turnover", "total_turnover"]
                for i, key in zip(range(1, 9), prices):
                    if entry_data[i].text.strip():
                        num_text = entry_data[i].text.replace(',', 'X')
                        num_text = num_text.replace('.', ',')
                        num_text = num_text.replace('X', '.')
                        entry[key] = num_text
                    else:
                        entry[key] = "0,00"

                data.append(entry)
                print(f"{symbol}: {entry}")
    else:
        print("Cannot reach site.")

    return data