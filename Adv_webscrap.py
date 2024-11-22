import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import time
import os

# Function to get URLs from Google search results using Selenium
def get_urls_for_prompt(prompt, use_firefox=False):
    try:
        if use_firefox:
            # Set Firefox binary path if needed
            firefox_binary_path = "C:/Program Files/Mozilla Firefox/firefox.exe"  # Change this path if Firefox is installed elsewhere
            options = webdriver.FirefoxOptions()
            options.binary_location = firefox_binary_path  # Set the binary location explicitly
            options.add_argument("--headless")
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
        else:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("user-agent=Mozilla/5.0")
            options.add_argument("--disable-blink-features=AutomationControlled")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        # Open Google and perform the search
        driver.get("https://www.google.com")

        # Handle cookie consent
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='I agree' or text()='Accept all']"))
            ).click()
        except TimeoutException:
            pass  # If no consent form, continue

        # Perform the search
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(prompt)
        search_box.send_keys(Keys.RETURN)

        # Wait for results to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.g")))

        # Get the first 5 search result links
        results = driver.find_elements(By.CSS_SELECTOR, "div.g a")[:5]
        urls = [result.get_attribute("href") for result in results if result.get_attribute("href")]

        driver.quit()
        return urls if urls else ["No URLs found."]
    
    except WebDriverException as e:
        st.error(f"Error fetching URLs: {e}")
        return []

# Function to parse website content using Selenium based on the user's prompt
def parse_website(url, prompt, use_firefox=False):
    try:
        if use_firefox:
            firefox_binary_path = "C:/Program Files/Mozilla Firefox/firefox.exe"  # Change this path if needed
            options = webdriver.FirefoxOptions()
            options.binary_location = firefox_binary_path  # Set the binary location explicitly
            options.add_argument("--headless")
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
        else:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("user-agent=Mozilla/5.0")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        # Visit the website
        driver.get(url)

        # Allow the page to load
        time.sleep(5)

        # Collect relevant text-based elements
        elements = driver.find_elements(By.XPATH, "//div | //span | //p")
        matched_content = [element.text.strip() for element in elements if prompt.lower() in element.text.lower()]

        driver.quit()
        return "\n\n".join(matched_content) if matched_content else "No matching content found."
    
    except TimeoutException:
        return "Error: Timeout occurred while loading the page."
    except WebDriverException as e:
        return f"Error: WebDriver exception occurred - {str(e)}"

# Streamlit app
def main():
    st.title("Prompt-Based Multi-Website Parser for Google SERP")

    prompt = st.text_input("Enter the prompt to search for specific content:")
    use_firefox = st.checkbox("Use Firefox instead of Chrome")

    if st.button("Parse"):
        if prompt:
            st.info(f"Searching Google for websites related to: {prompt}")
            
            # Fetch URLs based on the prompt
            urls = get_urls_for_prompt(prompt, use_firefox)

            if "No URLs found." in urls:
                st.warning("No URLs were found based on the prompt.")
            else:
                for idx, url in enumerate(urls):
                    st.write(f"Parsing content from URL {idx+1}: {url}")
                    result = parse_website(url, prompt, use_firefox)
                    st.success(f"Parsed content from {url}:\n\n{result}")
        else:
            st.warning("Please enter a prompt.")

if __name__ == "__main__":
    main()


