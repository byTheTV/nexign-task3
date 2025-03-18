from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from spellchecker import SpellChecker
import re
from bs4 import BeautifulSoup


def configure_driver():
    """Настройка браузера с параметрами"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def get_page_content(driver, url):
    """Получение контента страницы с динамической загрузкой"""
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return driver.page_source
    except Exception as e:
        print(f"Ошибка загрузки страницы: {str(e)}")
        return ""


def extract_links(driver, base_url):
    """Извлечение ссылок с главной страницы"""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
        links = []
        for a in driver.find_elements(By.TAG_NAME, "a"):
            href = a.get_attribute("href")
            if href and href.startswith(('/' + base_url, base_url)):
                links.append(href)
        return list(set(links))
    except Exception as e:
        print(f"Ошибка извлечения ссылок: {str(e)}")
        return []


def check_spelling(text, spell):
    """Проверка орфографии с фильтрацией"""
    cleaned = re.sub(r'[^\w\s]', '', text.lower())
    words = re.findall(r'\b\w+\b', cleaned)
    return [word for word in words if word not in spell and len(word) > 3]


def process_page(driver, url, spell):
    """Обработка страницы с проверкой орфографии"""
    try:
        content = get_page_content(driver, url)
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        errors = check_spelling(text, spell)

        if errors:
            print(f"\nОшибки на {url}:")
            for error in errors[:5]:
                print(f"- {error}")
        else:
            print(f"Ошибки на {url} не найдены")
    except Exception as e:
        print(f"Ошибка обработки {url}: {str(e)}")


def main():
    main_url = "https://nexign.com/ru"
    spell = SpellChecker(language='ru')

    driver = configure_driver()
    try:
        process_page(driver, main_url, spell)


        num_of_checking_links = 20
        links = extract_links(driver, main_url)
        print(f"\nНайдено {len(links)} ссылок. Проверяем первые {num_of_checking_links}:")

        for link in links[:num_of_checking_links]:
            process_page(driver, link, spell)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
