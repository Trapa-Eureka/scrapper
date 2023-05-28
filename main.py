import csv
from requests import get
from bs4 import BeautifulSoup

base_url = "https://www.manilatimes.net/search?query="
search_term = "headline"

response = get(f"{base_url}{search_term}")

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
            page_url = f"{base_url}{search_term}&page={page}"
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
