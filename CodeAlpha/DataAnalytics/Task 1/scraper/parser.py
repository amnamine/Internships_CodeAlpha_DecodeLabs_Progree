import re
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Rating mapping from textual CSS class to integer
RATING_MAP = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}

class BookParser:
    """
    Parses HTML pages from books.toscrape.com.
    """
    
    @staticmethod
    def parse_book_list(html_content: str, base_url: str) -> list[str]:
        """
        Parses a catalog/category page and extracts all absolute book detail links.
        """
        soup = BeautifulSoup(html_content, "lxml")
        book_links = []
        
        # Books are in <article class="product_pod">
        pods = soup.find_all("article", class_="product_pod")
        for pod in pods:
            link_tag = pod.find("h3").find("a") if pod.find("h3") else None
            if link_tag and "href" in link_tag.attrs:
                relative_url = link_tag["href"]
                # Resolve relative url to absolute url
                absolute_url = urljoin(base_url, relative_url)
                book_links.append(absolute_url)
                
        return book_links

    @staticmethod
    def parse_next_page(html_content: str, base_url: str) -> str | None:
        """
        Extracts the absolute URL of the next page if it exists.
        """
        soup = BeautifulSoup(html_content, "lxml")
        next_li = soup.find("li", class_="next")
        if next_li:
            link_tag = next_li.find("a")
            if link_tag and "href" in link_tag.attrs:
                return urljoin(base_url, link_tag["href"])
        return None

    @staticmethod
    def parse_book_detail(html_content: str, detail_url: str) -> dict:
        """
        Parses a book's detail page and extracts all target data points.
        """
        soup = BeautifulSoup(html_content, "lxml")
        
        # 1. Title
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else ""
        
        # 2. Rating
        rating = 0
        rating_tag = soup.find("p", class_=re.compile(r"star-rating\s+\w+"))
        if rating_tag:
            classes = rating_tag.get("class", [])
            for c in classes:
                if c.lower() in RATING_MAP:
                    rating = RATING_MAP[c.lower()]
                    break
        
        # 3. Category
        category = ""
        breadcrumb = soup.find("ul", class_="breadcrumb")
        if breadcrumb:
            lis = breadcrumb.find_all("li")
            if len(lis) >= 3:
                category = lis[2].text.strip()
                
        # 4. Description
        description = ""
        product_desc_heading = soup.find("div", id="product_description")
        if product_desc_heading:
            desc_tag = product_desc_heading.find_next_sibling("p")
            if desc_tag:
                description = desc_tag.text.strip()
                
        # 5. Product Information Table (UPC, Price, Stock, etc.)
        info_table = soup.find("table", class_="table-striped")
        table_data = {}
        if info_table:
            rows = info_table.find_all("tr")
            for row in rows:
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    table_data[th.text.strip()] = td.text.strip()
                    
        upc = table_data.get("UPC", "")
        price_excl = table_data.get("Price (excl. tax)", "")
        price_incl = table_data.get("Price (incl. tax)", "")
        tax = table_data.get("Tax", "")
        availability = table_data.get("Availability", "")
        
        # 6. Cover Image
        image_url = ""
        img_container = soup.find("div", class_="carousel-inner")
        if img_container:
            img_tag = img_container.find("img")
            if img_tag and "src" in img_tag.attrs:
                image_url = urljoin(detail_url, img_tag["src"])
                
        return {
            "title": title,
            "category": category,
            "rating": rating,
            "price_excl_tax": price_excl,
            "price_incl_tax": price_incl,
            "tax": tax,
            "availability": availability,
            "upc": upc,
            "description": description,
            "url": detail_url,
            "image_url": image_url
        }
