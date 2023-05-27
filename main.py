from requests import get
from bs4 import BeautifulSoup

base_url = "https://tribune.net.ph/?s="
search_term = "business"

response = get(f"{base_url}{search_term}")

# print(response)

if response.status_code != 200:
    print("can't request website")
else:
    # print(response)
    soup = BeautifulSoup(response.text, "html.parser")
    news = soup.find_all('div', class_="border-dark")
    for news_section in news:
        news_post = news_section.find_all('div', class_="col-lg-6")
        for post in news_post:
            anchors = post.find_all('a')
            anchor = anchors[1]
            link = anchor['href']
            title = anchor.find("h3")
            subtitle = anchor.find("div")
            # title, subtitle = anchor.find("h3", "div")
            print(title, subtitle)
            print("//////////////////////")
            print("//////////////////////")