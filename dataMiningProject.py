import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json

# Change these manually for each batch
BATCH_NUMBER = 1  # Example: 1 for first batch, 2 for next batch
START_PAGE = 1    # Example: 0 for first batch, 51 for next
END_PAGE = 50  # Example: 50 for first batch, 100 for next

CSV_FILE = f"SmartBandData{BATCH_NUMBER}.csv"  # Auto-generate filename


def flipkart_scrape(URL):
    """Scrape Flipkart page for product details."""
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"🚨 Request error: {e}")
        return None  # Skip this page if request fails

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract product details
    name = soup.find_all("div", class_="KzDlHZ")
    prodName = [i.get_text() for i in name]

    s_p = soup.find_all("div", class_="Nx9bqj _4b5DiR")
    ProdSalePrice = [i.get_text() for i in s_p]

    m_p = soup.find_all("div", class_="yRaY8j ZYYwLA")
    market_Price = [i.get_text() for i in m_p]

    disc = soup.find_all("div", class_="UkUFwK")
    d = [disc[i].get_text() if i < len(disc) else "N/A" for i in range(len(prodName))]

    rate = soup.find_all("div", class_="XQDdHH")
    p = [rate[i].get_text() if i < len(rate) else "N/A" for i in range(len(prodName))]

    rrt = soup.find_all("span", class_="Wphh3N")
    temp = []
    for i in range(len(rrt)):
        main_span = rrt[i].find("span")
        if main_span:
            spans = main_span.find_all("span")
            temp.append([spans[j].get_text().strip() for j in range(len(spans)) if j != 1])
        else:
            temp.append(["N/A", "N/A"])  # Fallback if data is missing
    no_of_ratings = [temp[i][0] if i < len(temp) else "N/A" for i in range(len(prodName))]
    no_of_reviews = [temp[i][1] if i < len(temp) else "N/A" for i in range(len(prodName))]

    specs = soup.find_all("ul", class_="G4BRas")
    prodSpecs = [json.dumps([li.get_text() for li in specs[i].find_all('li')]) if i < len(specs) else "[]" for i in range(len(prodName))]

    offer = soup.find_all("div", class_="n5vj9c")
    temp = [[offer[i].get_text()] for i in range(len(offer))]
    offer__on_prod = [[temp[i] for i in range(j, j+2)] if j+1 < len(temp) else ["N/A", "N/A"] for j in range(0, len(prodName))]

    # Ensure all columns have equal length
    max_length = len(prodName)
    data = {
        "Product Name": prodName + ["N/A"] * (max_length - len(prodName)),
        "Sale Price": ProdSalePrice + ["N/A"] * (max_length - len(ProdSalePrice)),
        "Market Price": market_Price + ["N/A"] * (max_length - len(market_Price)),
        "Discount Offered": d + ["N/A"] * (max_length - len(d)),
        "Product Rating": p + ["N/A"] * (max_length - len(p)),
        "No_of_rating": no_of_ratings + ["N/A"] * (max_length - len(no_of_ratings)),
        "No_of_review": no_of_reviews + ["N/A"] * (max_length - len(no_of_reviews)),
        "Product Specs": prodSpecs + ["N/A"] * (max_length - len(prodSpecs)),
        "Offers": offer__on_prod + [["N/A", "N/A"]] * (max_length - len(offer__on_prod))
    }

    return data

# Loop through pages in the given range
for page in range(START_PAGE, END_PAGE + 1):
    time.sleep(2)  # Prevent IP ban
    URL = f"https://www.flipkart.com/search?q=smartbands&page={page}"
    print(f"⚡ Scraping page {page}...")

    data = flipkart_scrape(URL)

    if data:  # If scraping was successful
        df = pd.DataFrame(data)
        df["Category"] = "Smart Band"

        # Save in a new CSV for this batch
        df.to_csv(CSV_FILE, mode='a', header=not (page > START_PAGE), index=False)
        print(f"✅ Saved page {page} in {CSV_FILE}, total rows: {len(pd.read_csv(CSV_FILE))}\n", flush=True)

    else:
        print(f"❌ Skipped page {page} (no data)")

print(f"🎉 Batch {BATCH_NUMBER} complete! Data saved in {CSV_FILE} 🚀")

