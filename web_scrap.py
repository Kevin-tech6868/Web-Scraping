import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Function to parse the website based on the user's prompt
def parse_website(url, prompt):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        time.sleep(5)  # Add delay to allow the page to fully load

        # Collect all text-based elements on the page (example with divs, spans, and paragraphs)
        elements = driver.find_elements(By.XPATH, "//div | //span | //p")

        matched_content = None  # Will store the first match
        for element in elements:
            text = element.text.strip()
            if prompt.lower() in text.lower():  # Case-insensitive matching
                matched_content = text
                break  # Stop after first match
        
        driver.quit()

        if matched_content:
            return matched_content
        else:
            return "No matching content found."
    
    except TimeoutException:
        return "Error: Timeout occurred while loading the page."
    except WebDriverException as e:
        return f"Error: WebDriver exception occurred - {str(e)}"

# Streamlit app
def main():
    st.title("Prompt-Based Website Parser")

    url = st.text_input("Enter the URL:")
    prompt = st.text_input("Enter the prompt to search for specific content:")

    if st.button("Parse"):
        if url and prompt:
            result = parse_website(url, prompt)
            st.success(f"Parsed content based on prompt:\n\n{result}")
        else:
            st.warning("Please enter both a valid URL and a prompt.")

if __name__ == "__main__":
    main()

