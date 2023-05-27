from requests import get
from bs4 import BeautifulSoup
from extractors.www import extract_news

news = extract_news("business")
print(news)