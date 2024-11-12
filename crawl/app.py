import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from urllib.parse import urljoin

# Custom headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

# Broad set of keywords for identifying "features" and "pricing" URLs
keywords = {
    "features": ["feature", "features", "spec", "specification", "overview", "capabilities", "function", "functions", "services", "solutions", "benefits"],
    "pricing": ["pricing", "price", "plan", "plans", "subscription", "cost", "rates", "fees", "packages", "billing", "quotes", "quote"]
}

def find_feature_pricing_urls(base_url):
    try:
        response = requests.get(base_url, headers=headers, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        urls = {
            "features": None,
            "pricing": None
        }

        # Prioritize "features" over "overview" if both are found
        for link in links:
            href = link['href'].lower()
            full_url = urljoin(base_url, link['href'])

            if "example.com" not in full_url:
                for key, terms in keywords.items():
                    if any(term in href for term in terms):
                        if key == "features" and "overview" in href and urls[key] is None:
                            urls[key] = full_url
                        elif urls[key] is None:
                            urls[key] = full_url

            if urls["features"] and urls["pricing"]:
                break

        return urls
    except requests.exceptions.RequestException as e:
        st.error(f"Error retrieving the page: {e}")
        return {}

# Streamlit interface
st.title("Automated Features & Pricing URL Crawler")

input_url = st.text_input("Enter the website URL:")

if st.button("Start Crawling"):
    if input_url:
        urls = find_feature_pricing_urls(input_url)
        
        if urls:
            data = [{"Type": key.capitalize(), "URL": url} for key, url in urls.items() if url]
            df = pd.DataFrame(data)
            st.write(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="features_pricing_urls.csv",
                mime="text/csv"
            )
        else:
            st.write("No 'features' or 'pricing' URLs found on the page.")
    else:
        st.warning("Please enter a URL to crawl.")
