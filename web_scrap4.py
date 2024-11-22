import streamlit as st
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import os

# Ensure NLTK punkt tokenizer is downloaded without permission errors
nltk_data_dir = './nltk_data/'
nltk_tokenizer_dir = os.path.join(nltk_data_dir, 'tokenizers')

# Check if 'punkt' is available, download if it's not
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    if not os.path.exists(nltk_tokenizer_dir):
        os.makedirs(nltk_tokenizer_dir)  # Create directory if it doesn't exist
    nltk.download('punkt', download_dir=nltk_data_dir)

nltk.data.path.append(nltk_data_dir)

# Function to get URLs using SerpAPI
def get_urls_for_prompt(prompt):
    try:
        params = {
            "engine": "google",
            "q": prompt,
            "api_key": "99032d11f4529779ed8b321c24eedeee0575114010305c719dd19fc019542c7d",  # Replace with your SerpAPI key
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        urls = []
        if "organic_results" in results:
            seen_domains = set()
            for result in results["organic_results"]:
                href = result.get("link")
                domain = urlparse(href).netloc
                if href and domain not in seen_domains:
                    seen_domains.add(domain)
                    urls.append(href)
                    if len(urls) >= 5:
                        break

        return urls if urls else ["No URLs found."]

    except Exception as e:
        st.error(f"Error fetching URLs: {e}")
        return []

# Function to extract important passages from a webpage
def extract_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        paragraphs = soup.find_all('p')
        important_passages = []
        for para in paragraphs:
            text = para.get_text().strip()
            if text and len(text.split()) > 10:
                important_passages.append(text)

        return important_passages if important_passages else ["No important content found."]

    except Exception as e:
        return f"Error extracting content: {e}"

# Function to summarize extracted content using LSA Summarizer
def summarize_content(content):
    if isinstance(content, list):
        content = " ".join(content)

    # Use Sumy to summarize content
    parser = PlaintextParser.from_string(content, Tokenizer("english"))
    summarizer = LsaSummarizer()

    summary = summarizer(parser.document, 5)  # Summarize to 5 sentences
    summarized_text = " ".join([str(sentence) for sentence in summary])

    return summarized_text

# Streamlit UI
def main():
    st.title("URL Fetcher, Content Extractor, and Storyteller")

    prompt = st.text_input("Enter your search query:")

    if st.button("Fetch URLs and Extract Story"):
        if prompt:
            with st.spinner("Fetching URLs..."):
                urls = get_urls_for_prompt(prompt)
                if urls:
                    st.success("URLs fetched successfully!")
                    full_content = ""
                    for url in urls:
                        st.write(f"URL: {url}")
                        content = extract_content(url)
                        st.write("Extracted Content:")
                        for passage in content:
                            st.write(passage)
                        full_content += " ".join(content) + " "
                else:
                    st.warning("No URLs found.")
        else:
            st.error("Please enter a search query.")

if __name__ == "__main__":
    main()




