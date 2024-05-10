from celery import shared_task
from webdriver.utils import setup_webdriver, selenium_action_template

# Sample Celery Selenium function
# TODO: Modify this as needed


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 6, 'countdown': 5})
def sample_selenium_task():
    driver = setup_webdriver()
    selenium_action_template(driver)
    # Place any other actions here after Selenium is done executing

    # Once completed, always close the session
    driver.close()
    driver.quit()
