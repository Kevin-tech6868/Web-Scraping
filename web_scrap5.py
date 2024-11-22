import streamlit as st
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fpdf import FPDF
from io import BytesIO

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
            if text and len(text.split()) > 10:  # Keep passages with more than 10 words
                important_passages.append(text)

        return important_passages if important_passages else ["No important content found."]

    except Exception as e:
        return f"Error extracting content: {e}"

# Clean extracted content by removing irrelevant parts
def clean_content(passages):
    cleaned_passages = []
    for passage in passages:
        # Remove passages that are too short or contain irrelevant data
        if len(passage.split()) > 20 and not passage.lower().startswith(("click here", "read more", "advertisement")):
            cleaned_passages.append(passage)
    return cleaned_passages

# Custom summarizer function (without NLTK)
def summarize_storytelling(content):
    sentences = content.split(". ")  # Split content into sentences
    # Select the first, middle, and last sentence for storytelling structure
    if len(sentences) > 5:
        summary = " ".join([sentences[0], sentences[len(sentences)//2], sentences[-1]])
    else:
        summary = content  # If content is too short, return as is
    return summary

# Function to create and return a PDF buffer
def create_pdf(summarized_story):
    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()
    
    # Set font and add content
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summarized_story)
    
    # Create a BytesIO buffer
    buffer = BytesIO()
    
    # Output the PDF content to the buffer
    pdf.output(buffer, dest='S')  # 'S' outputs to the buffer
    
    # Move the buffer pointer to the beginning
    buffer.seek(0)
    
    return buffer

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
                        cleaned_content = clean_content(content)  # Clean the content
                        st.write("Extracted Content (Cleaned):")
                        for passage in cleaned_content:
                            st.write(passage)
                        full_content += " ".join(cleaned_content) + " "
                    
                    # Summarize the content in storytelling mode
                    st.write("Summarized Story:")
                    summarized_story = summarize_storytelling(full_content)
                    st.write(summarized_story)

                    # Generate PDF for download
                    pdf_buffer = create_pdf(summarized_story)
                    st.download_button(
                        label="Download Story as PDF",
                        data=pdf_buffer,
                        file_name="story.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("No URLs found.")
        else:
            st.error("Please enter a search query.")

if __name__ == "__main__":
    main()

