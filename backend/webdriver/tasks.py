from celery import shared_task
from search_results.tasks import create_search_result
from selenium.webdriver.common.by import By
from webdriver.utils import (
    get_element,
    get_elements,
    google_search,
    selenium_action_template,
    setup_webdriver,
)


# Task template
@shared_task(
    autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5}
)
def sample_selenium_task():

    driver = setup_webdriver(use_proxy=False, use_saved_session=False)
    driver.get("Place URL here")
    selenium_action_template(driver)

    # TODO: Modify this as needed

    # Once completed, always close the session
    driver.close()
    driver.quit()


# Sample task to scrape Google for search results based on a keyword


@shared_task(
    autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5}
)
def simple_google_search():
    driver = setup_webdriver(
        driver_type="firefox", use_proxy=False, use_saved_session=False
    )
    driver.get(f"https://google.com/")

    google_search(driver, search_term="cat blog posts")

    # Count number of Google search results
    search_items = get_elements(driver, "xpath", '//*[@id="search"]/div[1]/div[1]/*')

    for item in search_items:
        title = item.find_element(By.TAG_NAME, "h3").text
        link = item.find_element(By.TAG_NAME, "a").get_attribute("href")

        create_search_result.apply_async(kwargs={"title": title, "link": link})

    driver.close()
    driver.quit()
