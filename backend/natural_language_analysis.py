# FUNDAMENTAL ANALYSIS
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
# nltk.download("vader_lexicon")


def get_news_sentiment(company_name):
    urls = [
        "https://www.mse.mk/mk/news/latest/1",
        "https://www.mse.mk/mk/news/latest/2"
    ]

    news_links = []
    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch the page: {url}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        panel_body = soup.find("div", class_="panel-body")
        if panel_body:
            links = panel_body.find_all("a", href=True)
            news_links.extend([link["href"] for link in links])

    if not news_links:
        print("No news links found.")
        return

    sia = SentimentIntensityAnalyzer()
    company_sentiment = {"positive": 0, "negative": 0, "neutral": 0}
    company_news_found = False

    for link in news_links:
        if not link.startswith("http"):
            link = f"https://www.mse.mk{link}"

        response = requests.get(link)
        if response.status_code != 200:
            print(f"Failed to fetch news article: {link}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        news_text = soup.get_text()

        if company_name.lower() in news_text.lower():
            company_news_found = True
            sentiment_score = sia.polarity_scores(news_text)
            if sentiment_score["compound"] > 0.05:
                company_sentiment["positive"] += 1
            elif sentiment_score["compound"] < -0.05:
                company_sentiment["negative"] += 1
            else:
                company_sentiment["neutral"] += 1

    if not company_news_found:
        print("No information.")
        return

    positive = company_sentiment["positive"]
    negative = company_sentiment["negative"]
    neutral = company_sentiment["neutral"]

    print(f"Sentiment Analysis for {company_name}:")
    print(f"Positive news: {positive}")
    print(f"Negative news: {negative}")
    print(f"Neutral news: {neutral}")

    if positive > negative:
        print("Recommendation: Buy stocks.")
        return "Buy"
    elif negative > positive:
        print("Recommendation: Sell stocks.")
        return "Sell"
    else:
        print("Recommendation: Hold stocks.")
        return "Hold"