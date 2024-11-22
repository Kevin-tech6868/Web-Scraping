import streamlit as st
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_urls_for_prompt(prompt):
    try:
        # Set up the search parameters
        params = {
            "engine": "google",
            "q": prompt,
            "api_key": "99032d11f4529779ed8b321c24eedeee0575114010305c719dd19fc019542c7d",  # Replace with your SerpAPI key
        }

        # Perform the search
        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract URLs from the search results
        urls = []
        if "organic_results" in results:
            seen_domains = set()
            for result in results["organic_results"]:
                href = result.get("link")
                domain = urlparse(href).netloc
                if href and domain not in seen_domains:
                    seen_domains.add(domain)
                    urls.append(href)
                    if len(urls) >= 5:  # Limit to 5 unique domains
                        break

        return urls if urls else ["No URLs found."]

    except Exception as e:
        st.error(f"Error fetching URLs: {e}")
        return []

def extract_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract paragraphs
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])

        # Basic logic to exclude introductory content
        # Here, we split content into sentences and try to find meaningful passages.
        # You might want to use more advanced NLP techniques for better results.
        important_passages = []
        for para in paragraphs:
            text = para.get_text().strip()
            if text and len(text.split()) > 10:  # Filter out very short paragraphs
                important_passages.append(text)

        return important_passages if important_passages else ["No important content found."]

    except Exception as e:
        return f"Error extracting content: {e}"

# Streamlit UI
def main():
    st.title("URL Fetcher and Content Extractor with SerpAPI")

    prompt = st.text_input("Enter your search query:")

    if st.button("Fetch URLs and Extract Content"):
        if prompt:
            with st.spinner("Fetching URLs..."):
                urls = get_urls_for_prompt(prompt)
                if urls:
                    st.success("URLs fetched successfully!")
                    for url in urls:
                        st.write(url)
                        content = extract_content(url)
                        st.write("Content Extracted:")
                        for passage in content:
                            st.write(passage)
                else:
                    st.warning("No URLs found.")
        else:
            st.error("Please enter a search query.")

if __name__ == "__main__":
    main()


       