import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_google_news():

    # Proxy configuration
    proxy_config = {
        "server": "endpoint:port",  # Proxy server and port only
        "username": "user",
        "password": "pass"
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, proxy=proxy_config)
        page = browser.new_page()    

        # Define the Google News URL

        url = "https://news.google.com/search?q=web+scraping&hl=en-US&gl=US&ceid=US%3Aen"

        # Navigate to the page
        page.goto(url)

        # Wait for the "Accept all" button to appear and click it if found
        try:
            accept_button = page.wait_for_selector('text="Accept all"', timeout=5000)  # Adjust timeout if needed
            if accept_button:
                page.click('text="Accept all"')
        except:
            print("No 'Accept all' button found, continuing...")

        # Wait for the page to fully load after clicking the button
        page.wait_for_timeout(5000)  # Adjust if needed

        # Get the page content
        content = page.content()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")

        # Find all article links (now using the correct class name "WwrzSb")
        links = soup.find_all("a", class_="WwrzSb")
        titles = soup.find_all("a", class_="JtKRv")

        proxy_count = 0  # Initialize counter for articles containing "proxy" or "proxies"
        total_count = 0  # Initialize counter for total articles scraped

        # Open a CSV file for writing
        with open('scraped_articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'URL', 'Contains Proxy']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header row
            writer.writeheader()

            # Iterate over the links
            for title, link in zip(titles[:10], links[:10]):
                article_title = title.text
                article_url = link['href']

                # Ensure the URL is complete (Google News URLs can be relative)
                if article_url.startswith('./'):
                    article_url = "https://news.google.com" + article_url

                # Navigate to the article page
                page.goto(article_url)

                # Wait for the page to fully load
                page.wait_for_timeout(5000)  # Adjust if needed

                # Get the article content
                article_content = page.content()

                # Parse the article content with BeautifulSoup
                article_soup = BeautifulSoup(article_content, "html.parser")

               # Check if the article contains the keywords "proxy" or "proxies"
                article_text = article_soup.get_text().lower()  # Get the text and convert to lowercase
                contains_proxy = "proxy" in article_text or "proxies" in article_text

                # Write the article data to the CSV file
                writer.writerow({'Title': article_title, 'URL': page.url, 'Contains Proxy': contains_proxy})

                # Print the data to the terminal
                print(f"Title: {article_title}")
                print(f"URL: {page.url}")
                print(f"Contains 'proxy' or 'proxies': {contains_proxy}")
                print()

                # Increment counters
                total_count += 1
                if contains_proxy:
                    proxy_count += 1

        # Print the amount of URLs that contained the phrase and the number of total URLs scraped
        print(f"\n{proxy_count}/{total_count} URLs contained the phrases.")

        # Close the browser
        browser.close()

if __name__ == "__main__":
    scrape_google_news()