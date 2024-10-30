"""
Settings file to hold constants and functions
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config.settings import get_secret
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions
from selenium import webdriver
import undetected_chromedriver as uc
from config.settings import USE_PROXY, CAPTCHA_TESTING
from config.settings import get_secret
from twocaptcha import TwoCaptcha
from whois import whois
from whois.parser import PywhoisError
import os
import random


def take_snapshot(driver, filename="dump.png"):
    # Set window size
    required_width = driver.execute_script(
        "return document.body.parentNode.scrollWidth"
    )
    required_height = driver.execute_script(
        "return document.body.parentNode.scrollHeight"
    )
    driver.set_window_size(required_width, required_height + (required_height * 0.05))

    # Take the snapshot
    driver.find_element(By.TAG_NAME, "body").screenshot(
        "/dumps/" + filename
    )  # avoids any scrollbars
    print("Snapshot saved")


def dump_html(driver, filename="dump.html"):
    # Save the page source to error.html
    with open(("/dumps/" + filename), "w", encoding="utf-8") as file:
        file.write(driver.page_source)


def setup_webdriver(driver_type="chrome", use_proxy=True, use_saved_session=False):
    # Manual proxy override via .env variable
    if not USE_PROXY:
        use_proxy = False
    if use_proxy:
        print("Running driver with proxy enabled")
    else:
        print("Running driver with proxy disabled")

    if use_saved_session:
        print("Running with saved session")
    else:
        print("Running without using saved session")

    if driver_type == "chrome":
        print("Using Chrome driver")
        opts = uc.ChromeOptions()

        if use_saved_session:
            if os.path.exists("/tmp_chrome_profile"):
                print("Existing Chrome ephemeral profile found")
            else:
                print("No existing Chrome ephemeral profile found")
                os.system("mkdir /tmp_chrome_profile")
                if os.path.exists("/chrome"):
                    print("Copying Chrome Profile to ephemeral directory")
                    # Flush any non-essential cache directories from the existing profile as they may balloon in size overtime
                    os.system('rm -rf "/chrome/Selenium Profile/Code Cache/*"')
                    # Create a copy of the Chrome Profile
                    os.system("cp -r /chrome/* /tmp_chrome_profile")
                    try:
                        # Remove some items related to file locks
                        os.remove("/tmp_chrome_profile/SingletonLock")
                        os.remove("/tmp_chrome_profile/SingletonSocket")
                        os.remove("/tmp_chrome_profile/SingletonLock")
                    except:
                        pass
                else:
                    print("No existing Chrome Profile found. Creating one from scratch")

        if use_saved_session:
            # Specify the user data directory
            opts.add_argument(f"--user-data-dir=/tmp_chrome_profile")
            opts.add_argument("--profile-directory=Selenium Profile")

        # Set proxy
        if use_proxy:
            opts.add_argument(
                f'--proxy-server=socks5://{get_secret("PROXY_IP")}:{get_secret("PROXY_PORT_IP_AUTH")}'
            )

        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-application-cache")
        opts.add_argument("--disable-setuid-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--headless=new")
        driver = uc.Chrome(options=opts)

    elif driver_type == "firefox":
        print("Using firefox driver")
        opts = FirefoxOptions()
        if use_saved_session:
            if not os.path.exists("/firefox"):
                print("No profile found")
                os.makedirs("/firefox")
            else:
                print("Existing profile found")
                # Specify a profile if it exists
                opts.profile = "/firefox"

        # Set proxy
        if use_proxy:
            opts.set_preference("network.proxy.type", 1)
            opts.set_preference("network.proxy.socks", get_secret("PROXY_IP"))
            opts.set_preference(
                "network.proxy.socks_port", int(get_secret("PROXY_PORT_IP_AUTH"))
            )
            opts.set_preference("network.proxy.socks_remote_dns", False)

        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--headless")
        opts.add_argument("--disable-gpu")
        driver = webdriver.Firefox(options=opts)

    driver.maximize_window()

    # Check if proxy is working
    driver.get("https://api.ipify.org/")
    body = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    ip_address = body.text
    print(f"External IP: {ip_address}")
    return driver


# These are  wrapper function for quickly automating multiple steps in webscraping (logins, button presses, text inputs, etc.)
# Depending on your use case, you may have to opt out of using this


# Function to get the element once it has loaded in


def get_element(driver, by, key, hidden_element=False, timeout=8):
    try:
        # Convert string-based locators to By objects (By.XPATH, By.CSS, etc.)
        if isinstance(by, str):
            by = getattr(By, by.upper())

        wait = WebDriverWait(driver, timeout=timeout)
        if not hidden_element:
            element = wait.until(
                EC.element_to_be_clickable((by, key))
                and EC.visibility_of_element_located((by, key))
            )
        else:
            element = wait.until(EC.presence_of_element_located((by, key)))
        return element
    except Exception:
        dump_html(driver)
        take_snapshot(driver)
        driver.close()
        driver.quit()
        raise Exception(f"Unable to get element of {by} value: {key}")


def get_elements(driver, by, key, hidden_element=False, timeout=8):
    try:
        # Convert string-based locators to By objects (By.XPATH, By.CSS, etc.)
        if isinstance(by, str):
            by = getattr(By, by.upper())

        wait = WebDriverWait(driver, timeout=timeout)

        if hidden_element:
            elements = wait.until(EC.presence_of_all_elements_located((by, key)))
        else:
            visible_elements = wait.until(
                EC.visibility_of_any_elements_located((by, key))
            )
            elements = [element for element in visible_elements if element.is_enabled()]

        return elements
    except Exception:
        dump_html(driver)
        take_snapshot(driver)
        driver.close()
        driver.quit()
        raise Exception(f"Unable to get elements of {by} value: {key}")


def execute_selenium_elements(driver, timeout, elements):
    try:
        for index, element in enumerate(elements):
            print("Waiting...")
            # Element may have a keyword specified, check if that exists before running any actions
            if "keyword" in element:
                # Skip a step if the keyword does not exist
                if element["keyword"] not in driver.page_source:
                    print(
                        f'Keyword {element["keyword"]} does not exist. Skipping step: {index+1} - {element["name"]}'
                    )
                    continue
                elif (
                    element["keyword"] in driver.page_source
                    and element["type"] == "skip"
                ):
                    print(
                        f'Keyword {element["keyword"]} does exists. Stopping at step: {index+1} - {element["name"]}'
                    )
                    break
            print(f'Step: {index+1} - {element["name"]}')
            # Revert to default iframe action
            if element["type"] == "revert_default_frame":
                driver.switch_to.default_content()
                continue
            # CAPTCHA Callback
            elif element["type"] == "recaptchav2_callback":
                if callable(element["input"]):
                    values = element["input"]()
                else:
                    values = element["input"]
                if type(values) is list:
                    raise Exception('Invalid input value specified for "callback" type')
                else:
                    # For single input values
                    driver.execute_script(f'onRecaptcha("{values}");')
                continue
            try:
                # Try to get default element
                if "hidden" in element:
                    site_element = get_element(
                        driver,
                        element["default"]["type"],
                        element["default"]["key"],
                        hidden_element=True,
                        timeout=timeout,
                    )
                else:
                    site_element = get_element(
                        driver,
                        element["default"]["type"],
                        element["default"]["key"],
                        timeout=timeout,
                    )
            except Exception as e:
                print(f"Failed to find primary element")
                # If that fails, try to get the failover one
                print("Trying to find legacy element")
                if "hidden" in element:
                    site_element = get_element(
                        driver,
                        element["failover"]["type"],
                        element["failover"]["key"],
                        hidden_element=True,
                        timeout=timeout,
                    )
                else:
                    site_element = get_element(
                        driver,
                        element["failover"]["type"],
                        element["failover"]["key"],
                        timeout=timeout,
                    )
            # Clicking an element
            if element["type"] == "click":
                site_element.click()
            # Switching to an element frame/iframe
            elif element["type"] == "switch_to_iframe_click":
                driver.switch_to.frame(site_element)
            # Input type simulates user typing
            elif element["type"] == "input":
                if callable(element["input"]):
                    values = element["input"]()
                else:
                    values = element["input"]
                values = values.splitlines()

                # For multiple input values
                for index, value in enumerate(values):
                    site_element.send_keys(value)
                    # Only send a new line keypress if this is not the last value to enter in the list
                    if index != len(values) - 1:
                        site_element.send_keys(Keys.RETURN)
            elif element["type"] == "input_enter":
                site_element.send_keys(Keys.RETURN)
            # Input_replace type places values directly. Useful for CAPTCHA
            elif element["type"] == "input_replace":
                if callable(element["input"]):
                    values = element["input"]()
                else:
                    values = element["input"]
                if type(values) is list:
                    raise Exception(
                        'Invalid input value specified for "input_replace" type'
                    )
                else:
                    # For single input values
                    driver.execute_script(
                        f'arguments[0].value = "{values}";', site_element
                    )
    except Exception as e:
        take_snapshot(driver)
        dump_html(driver)
        driver.close()
        driver.quit()
        raise Exception(e)


def solve_captcha(
    site_key, url, retry_attempts=3, version="v2", enterprise=False, use_proxy=True
):
    # Manual proxy override set via $ENV
    if not USE_PROXY:
        use_proxy = False
    if CAPTCHA_TESTING:
        print("Initializing CAPTCHA solver in dummy mode")
        code = random.randint()
        print("CAPTCHA Successful")
        return code

    elif use_proxy:
        print("Using CAPTCHA solver with proxy")
    else:
        print("Using CAPTCHA solver without proxy")

    captcha_params = {
        "url": url,
        "sitekey": site_key,
        "version": version,
        "enterprise": 1 if enterprise else 0,
        "proxy": (
            {"type": "socks5", "uri": get_secret("PROXY_USER_AUTH")}
            if use_proxy
            else None
        ),
    }

    # Keep retrying until max attempts is reached
    for _ in range(retry_attempts):
        # Solver uses 2CAPTCHA by default
        solver = TwoCaptcha(get_secret("CAPTCHA_API_KEY"))
        try:
            print("Waiting for CAPTCHA code...")
            code = solver.recaptcha(**captcha_params)["code"]
            print("CAPTCHA Successful")
            return code
        except Exception as e:
            print(f"CAPTCHA Failed! {e}")

    raise Exception(f"CAPTCHA API Failed!")


def whois_lookup(url):
    try:
        lookup_info = whois(url)
        # TODO: Add your own processing here
    except PywhoisError:
        print(f"No WhoIs record found for {url}")
    return lookup_info


def save_browser_session(driver):
    # Copy over the profile once we finish logging in
    if isinstance(driver, webdriver.Firefox):
        # Copy process for Firefox
        print("Updating saved Firefox profile")
        # Get the current profile directory from about:support page
        driver.get("about:support")
        box = get_element(driver, "id", "profile-dir-box", timeout=4)
        temp_profile_path = os.path.join(os.getcwd(), box.text)
        profile_path = "/firefox"
        # Create the command
        copy_command = "cp -r " + temp_profile_path + "/* " + profile_path
        # Copy over the Firefox profile
        if os.system(copy_command):
            print("Firefox profile saved")
    elif isinstance(driver, uc.Chrome):
        # Copy the Chrome profile
        print("Updating non-ephemeral Chrome profile")
        # Flush Code Cache again to speed up copy
        os.system('rm -rf "/tmp_chrome_profile/SimpleDMCA Profile/Code Cache/*"')
        if os.system("cp -r /tmp_chrome_profile/* /chrome"):
            print("Chrome profile saved")


# Sample function
# Call this within a Celery task
# TODO: Modify as needed to your needs


def selenium_action_template(driver):
    # Data that might need to be entered during webscraping
    info = {
        "sample_field1": "sample_data",
        "sample_field2": "sample_data",
        "captcha_code": lambda: solve_captcha("SITE_KEY", "SITE_URL"),
    }

    elements = [
        {
            "name": "Enter data for sample field 1",
            "type": "input",
            "input": "{sample_field1}",
            # If a site implements canary design releases, you can place the ID for the element in the new design
            "default": {
                # See get_element() for possible selector types
                "type": "xpath",
                "key": "",
            },
            # If a site implements canary design releases, you can place the ID for the element in the old design here
            "failover": {"type": "xpath", "key": ""},
        },
    ]

    # Dictionary to store values which will be entered via Selenium
    # Helps prevent duplicates and stale values compared to just using the info variable directly
    site_form_values = {}

    # Fill in final fstring values in elements
    for element in elements:
        if "input" in element and "{" in element["input"]:
            a = element["input"].strip("{}")
            if a in info:
                value = info[a]
                # Check if the value is a callable (a lambda function) and call it if so
                if callable(value):
                    # Check if the value has already been called
                    if a not in site_form_values:
                        # Call the value and store it in the dictionary
                        site_form_values[a] = value()
                    # Use the stored value
                    value = site_form_values[a]
                # Replace the placeholder with the actual value
                element["input"] = str(value)

    # Execute the selenium actions
    execute_selenium_elements(driver, 8, elements)


# Sample task for Google search


def google_search(driver, search_term):
    info = {
        "search_term": search_term,
    }

    elements = [
        {
            "name": "Type in search term",
            "type": "input",
            "input": "{search_term}",
            "default": {"type": "xpath", "key": '//*[@id="APjFqb"]'},
            "failover": {"type": "xpath", "key": '//*[@id="APjFqb"]'},
        },
        {
            "name": "Press enter",
            "type": "input_enter",
            "default": {"type": "xpath", "key": '//*[@id="APjFqb"]'},
            "failover": {"type": "xpath", "key": '//*[@id="APjFqb"]'},
        },
    ]

    site_form_values = {}

    for element in elements:
        if "input" in element and "{" in element["input"]:
            a = element["input"].strip("{}")
            if a in info:
                value = info[a]
                if callable(value):
                    if a not in site_form_values:
                        site_form_values[a] = value()
                    value = site_form_values[a]
                element["input"] = str(value)

    execute_selenium_elements(driver, 8, elements)
