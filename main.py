from requests import get
from bs4 import BeautifulSoup

base_url = "https://www.philstar.com/"
search_term = "business"

response = get(f"{base_url}{search_term}")

# print(response)

if response.status_code != 200:
    print("can't request website")
else:
    soup = BeautifulSoup(response.text, "html.parser")
    news = soup.find_all('div', class_="tiles")
    for news_section in news:
        news_post = news_section.find_all('div', class_="TilesText")
        for post in news_post:
            div_elements = post.find_all("div")
            if len(div_elements) > 1: # 두개 이상의 div 요소가 있는지 체크
                div_elements[1].extract() # 두번째 div 요소를 삭제함
            print(post)
            print("/////////////////////")