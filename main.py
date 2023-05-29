import os
import csv
import requests
from bs4 import BeautifulSoup
from requests import get

# from extractors.www import extract_news
# from extractors.www import extract_scv
# from extractors.www import extract_house

# news = extract_news('business')
# print(news)

# scv = extract_scv('headline')
# print(scv)

# houseItem = extract_house('/single-family-house/buy/price:0-17000000/bedrooms:5+/?sorting=price-high')
# print(houseItem)

base_url = 'https://www.lamudi.com.ph/metro-manila/quezon-city/house'
search_term = '/single-family-house/buy/price:0-17000000/bedrooms:5+/?sorting=price-high'
response = get(f'{base_url}{search_term}')

def download_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

house_data = []

if response.status_code != 200:
    print("Can't request contents")
else:
    soup = BeautifulSoup(response.text, "html.parser")
    pagination = soup.find('div', class_='Pagination')

    if pagination is not None:
        select = pagination.find('select')
        options = select.find_all('option')
        total_pages = len(options)

        for page in range(1, total_pages + 1):
            page_url = f'{base_url}{search_term}&page={page}'
            page_response = get(page_url)

            if page_response.status_code == 200:
                page_soup = BeautifulSoup(page_response.text, "html.parser")
                page_house = page_soup.find_all('div', class_='ListingCell-content')

                for idx, house_section in enumerate(page_house):
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
    else:
        print("Pagination not found.")

                                