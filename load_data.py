from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json


def get_movies(driver):
    url = 'https://www.kinopoisk.ru/lists/movies/top250/'
    driver.get(url)
    time.sleep(20)

    movies = []
    movie_items = driver.find_elements(By.CSS_SELECTOR, '.styles_root__ti07r')

    for item in movie_items[:15]:
        title_tag = item.find_element(By.CSS_SELECTOR, '.desktop-list-main-info_mainTitle__8IBrD')
        title = title_tag.text.strip()

        movie_link = item.find_element(By.CSS_SELECTOR, '.base-movie-main-info_link__YwtP1')
        movie_url = movie_link.get_attribute('href')
        movie_id = movie_url.split('/')[-2]

        movies.append({'id': movie_id, 'title': title})

    return movies


def get_reviews_and_types(driver, movie_id):
    url = f'https://www.kinopoisk.ru/film/{movie_id}/reviews/'
    driver.get(url)

    # Используем WebDriverWait для ожидания появления элементов на странице
    try:
        # Ожидаем, пока блок с отзывами ('.response') не станет видимым на странице
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.response'))
        )
    except TimeoutException:
        print(f"Не удалось найти отзывы для фильма с ID: {movie_id}")
        return []

    reviews = []

    # Теперь, когда элементы загружены, можем безопасно извлекать данные
    review_items = driver.find_elements(By.CSS_SELECTOR, '.response')

    for item in review_items[:10]:
        try:
            # Ожидаем, пока блок с текстом отзыва не станет доступным
            review_text_element = WebDriverWait(item, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[itemprop="reviewBody"]'))
            )
            review_text = review_text_element.text.strip()
            if 'good' in item.get_attribute('class'):
                review_type = 'POSITIVE'
            elif 'bad' in item.get_attribute('class'):
                review_type = 'NEGATIVE'
            elif 'neutral' in item.get_attribute('class'):
                review_type = 'NEUTRAL'
            else:
                review_type = 'UNKNOWN'

            reviews.append({
                'text': review_text,
                'type': review_type
            })

        except TimeoutException:
            print(f"Не удалось загрузить текст отзыва для фильма с ID: {movie_id}")
            continue

    return reviews


def get_data(driver):
    movies = get_movies(driver)

    movie_reviews = []
    for movie in movies:
        print(f"Парсим отзывы для фильма: {movie['title']} (ID: {movie['id']})")
        reviews = get_reviews_and_types(driver, movie['id'])
        movie_reviews.append({
            'title': movie['title'],
            'id': movie['id'],
            'reviews': reviews
        })

    return movie_reviews


# Получаем отзывы
driver = webdriver.Chrome()
reviews_data = get_data(driver)
driver.quit()

# Сохраняем данные в JSON
with open('movie_reviews.json', 'w', encoding='utf-8') as json_file:
    json.dump(reviews_data, json_file, ensure_ascii=False, indent=4)

print("Данные о рецензиях сохранены в movie_reviews.json")
