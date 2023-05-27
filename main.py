from requests import get
from bs4 import BeautifulSoup

base_url = "https://tribune.net.ph/?s="
search_term = "immigration"

response = get(f"{base_url}{search_term}")

if response.status_code != 200:
    print("Can't request website")
else:
    results = []
    soup = BeautifulSoup(response.text, "html.parser")
    news = soup.find_all('div', class_="border-dark")
    for news_section in news:
        news_divs = news_section.find_all('div', recursive=False)
        if len(news_divs) > 1:
            # border-dark의 두번째 div만 찾기.
            post = news_divs[1]
            anchors = post.find_all('a')
            for anchor in anchors:
                link = anchor['href']
                title_element = anchor.find("h3")
                subtitle_element = anchor.find("div")
                
                # title과 subtitle중 한개의 정보가 없어서
                # 오류메세지 노출될 수도 있는데 그런거 상관없이 배열에 포함한다.
                if title_element is not None and subtitle_element is not None:
                    if title_element is not None:
                        title = title_element.get_text().strip()
                    else:
                        title = ""

                    if subtitle_element is not None:
                        subtitle = subtitle_element.get_text().strip()
                    else:
                        subtitle = ""

                    news_data = {
                        'title': title,
                        'subtitle': subtitle
                    }
                    results.append(news_data)

    for result in results:
        print(result)
        print("////////////////")
