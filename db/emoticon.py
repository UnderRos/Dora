import requests
from bs4 import BeautifulSoup
from db.connection import Database

def crawl_and_save(url):
    # 웹 요청
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    all_elements = soup.find_all(['div', 'pre'])

    db = Database()
    db.connect()

    current_title = None

    for element in all_elements:
        if element.name == 'div' and 'contentTitle' in element.get('class', []):
            current_title = element.get_text(strip=True)
        elif element.name == 'pre' and current_title:
            emoticon = element.get_text(strip=True)
            insert_query = """
                INSERT INTO petemoticon (text, emoticon)
                VALUES (%s, %s)
            """
            db.execute(insert_query, (current_title, emoticon))
            print(f"[INSERTED] {current_title} - {emoticon}")

    db.disconnect()

if __name__ == '__main__':
    crawl_and_save("https://snskeyboard.com/emoticon/#google_vignette")
