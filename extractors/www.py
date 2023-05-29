import csv
import os
import requests
from requests import get
from bs4 import BeautifulSoup

def extract_news(keyword):
    base_url = "https://tribune.net.ph/?s="
    response = get(f"{base_url}{keyword}")
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
                            'link': link,
                            'title': title,
                            'subtitle': subtitle
                        }
                        results.append(news_data)
        return results
        # for result in results:
        #     print(result)
        #     print("////////////////")


def extract_scv(keyword):
  base_url = "https://www.manilatimes.net/search?query="
  response = get(f"{base_url}{keyword}")
  if response.status_code != 200:
      print("Unable to request the page")
  else:
      soup = BeautifulSoup(response.text, "html.parser")
      item_row = soup.find('div', class_='item-row-2')

      if item_row is None:
          print("Unable to locate 'item-row-2'")
      else:
          pagination_row = item_row.find_next_sibling('div', class_='pagination-row')

          if pagination_row is None:
              print("Unable to locate 'pagination-row'")
              total_pages = 1  # Set a default value for total pages
          else:
              pagination_info = pagination_row.find('div', class_='pagination-info')
              total_pages = 1  # Set a default value for total pages

              if pagination_info is not None:
                  page_links = pagination_info.find_all('a')
                  last_page_link = page_links[-1]['href']
                  total_pages = int(last_page_link.split("=")[-1])

          item_data = []  # Initialize the item data array

          anchor = item_row.find('a')

          if anchor:
              link = anchor['href']
              item_data.append({'link': link})
          else:
              print("No anchor found in 'item-row-2'")

          for page in range(1, total_pages + 1):
              page_url = f"{base_url}{keyword}&page={page}"
              page_response = get(page_url)

              if page_response.status_code == 200:
                  page_soup = BeautifulSoup(page_response.text, "html.parser")
                  col_content_1_divs = page_soup.find_all('div', class_='col-content-1')

                  for col_content_1_div in col_content_1_divs:
                      try:
                          # Find the title and subtitle elements inside col-content-1 div
                          title_element = col_content_1_div.find('div', class_='article-title-h4').find('a')
                          subtitle_element = col_content_1_div.find('div', class_='author-name-a')

                          # Extract the title, subtitle, and date from the elements
                          title = title_element.get_text(strip=True) if title_element else ""
                          subtitle = subtitle_element.get_text(strip=True) if subtitle_element else ""
                          date_element = subtitle_element.find('span', class_='roboto-a')
                          date = date_element.get_text(strip=True) if date_element else ""

                          item_data.append({'link': link, 'title': title, 'subtitle': f"{subtitle} - {date}"})
                      except AttributeError:
                          pass  # Skip the item if title or subtitle element is not found
              else:
                  print(f"Unable to request page {page_url}")

          # Remove '\n' from the results
          item_data = [{k: v.replace('\n', '') for k, v in item.items()} for item in item_data]

          # Export the data to a CSV file
          filename = "search_results.csv"
          with open(filename, 'w', newline='', encoding='utf-8') as file:
              fieldnames = ['link', 'title', 'subtitle']
              writer = csv.DictWriter(file, fieldnames=fieldnames)
              writer.writeheader()
              writer.writerows(item_data)

          print(f"Data exported to {filename}")


def extract_house(keyword):
    base_url = 'https://www.lamudi.com.ph/metro-manila/quezon-city/house'
    response = get(f'{base_url}{keyword}')

    def download_image(url, filename):
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)

    house_data = []

    if response.status_code != 200:
        print("Can't request contents")
    else:
        soup = BeautifulSoup(response.text, "html.parser")
        house = soup.find_all('div', class_='ListingCell-content')

        # images 폴더 생성
        if not os.path.exists("images"):
            os.makedirs("images")

        for idx, house_section in enumerate(house):
            house_info = {}

            main_image = house_section.find('div', class_='ListingCell-MainImage')
            all_info = house_section.find('div', class_='ListingCell-AllInfo')

            if main_image is not None:
                listing_link = main_image.find('a', class_='ListingCell-ListingLink')
                if listing_link is not None:
                    bg_image = listing_link.find('div', class_='ListingCell-image')
                    if bg_image is not None:
                        image = bg_image.find('img')
                        if image is not None:
                            image_data_src = image.get('data-src')
                            image_src = image.get('src')
                            if image_data_src and image_data_src.endswith('.webp'):
                                image_url = image_data_src
                            if image_src and image_src.endswith('.webp'):
                                image_url = image_src

                            # 이미지 다운로드 및 파일명 생성
                            image_filename = f"images/{idx}.webp"
                            download_image(image_url, image_filename)

                            house_info['image'] = image_filename

            if all_info is not None:
                info_link = all_info.find('a')
                if info_link is not None:
                    link = info_link['href']
                    house_info['link'] = link

                    title_wrapper = info_link.find('div', class_='ListingCell-TitleWrapper')
                    if title_wrapper is not None:
                        title = title_wrapper.find('h2', class_='ListingCell-KeyInfo-title').text.strip()
                        address = title_wrapper.find('span', class_='ListingCell-KeyInfo-address-text').text.strip()
                        house_info['title'] = title
                        house_info['location'] = address

                    price_section = info_link.find('div', class_='ListingCell-KeyInfo-price')
                    if price_section is not None:
                        price = price_section.find('span', class_='PriceSection-FirstPrice').text.strip()
                        # 가격 데이터에서 통화 기호와 쉼표 제거 후 정수로 변환
                        price = int(price.replace('₱', '').replace(',', ''))
                        house_info['price'] = price

                        key_info_details = price_section.find('div', class_='ListingCell-keyInfo-details')
                        if key_info_details is not None:
                            key_info_v2 = key_info_details.find('div', class_='KeyInformation_v2')

                            if key_info_v2 is not None:
                                info_attributes = key_info_v2.find_all('div', class_='KeyInformation-attribute_v2')

                                amenities = []
                                for attribute in info_attributes:
                                    description = attribute.find('div', class_='KeyInformation-description_v2')
                                    label = attribute.find('span', class_='KeyInformation-label_v2')

                                    if description is not None and label is not None:
                                        value = description.find('span', class_='KeyInformation-value_v2')
                                        if value is not None:
                                            value_text = value.get_text(strip=True)
                                            label_text = label.get_text(strip=True)
                                            amenity = f"{label_text}: {value_text}"
                                            amenities.append(amenity)

                                house_info['amenities'] = ', '.join(amenities)

            house_data.append(house_info)

    # 'price'를 기준으로 내림차순 정렬
    house_data.sort(key=lambda x: x.get('price', 0), reverse=True)

    # CSV 파일 저장
    filename = 'house_data.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['image', 'title', 'location', 'price', 'amenities', 'link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(house_data)

    print(f"CSV 파일 '{filename}'이 저장되었습니다.")