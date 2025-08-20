import urllib.request
import urllib.parse
import json
import csv
import re
import time
import os
from html.parser import HTMLParser
from typing import List, Dict

class ProductHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.products = []
        self.current_product = {}
        self.in_product = False
        self.in_title = False
        self.in_price = False
        self.in_rating = False
        self.data_buffer = ""
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get('class', '').lower()
        id_name = attrs_dict.get('id', '').lower()
        
        # Check if we're entering a product container
        if any(keyword in class_name or keyword in id_name for keyword in 
               ['product', 'item', 'listing', 'card']):
            self.in_product = True
            self.current_product = {'name': 'N/A', 'price': 'N/A', 'rating': 'N/A'}
        
        # Check for title elements
        if self.in_product and (tag in ['h1', 'h2', 'h3', 'h4'] or 
                               'title' in class_name or 'name' in class_name):
            self.in_title = True
            self.data_buffer = ""
        
        # Check for price elements
        if self.in_product and ('price' in class_name or 'cost' in class_name or 
                               'amount' in class_name or 'currency' in class_name):
            self.in_price = True
            self.data_buffer = ""
        
        # Check for rating elements
        if self.in_product and ('rating' in class_name or 'star' in class_name or 
                               'score' in class_name):
            self.in_rating = True
            self.data_buffer = ""
    
    def handle_endtag(self, tag):
        if self.in_title:
            if self.data_buffer.strip():
                self.current_product['name'] = self.data_buffer.strip()[:200]
            self.in_title = False
        
        if self.in_price:
            if self.data_buffer.strip():
                self.current_product['price'] = self.extract_price(self.data_buffer.strip())
            self.in_price = False
        
        if self.in_rating:
            if self.data_buffer.strip():
                self.current_product['rating'] = self.extract_rating(self.data_buffer.strip())
            self.in_rating = False
        
        # End of product container
        if self.in_product and tag == 'div':
            if self.current_product.get('name') != 'N/A':
                self.products.append(self.current_product.copy())
            self.in_product = False
    
    def handle_data(self, data):
        if self.in_title or self.in_price or self.in_rating:
            self.data_buffer += data
    
    def extract_price(self, text):
        if not text:
            return "N/A"
        
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'₹[\d,]+\.?\d*',
            r'€[\d,]+\.?\d*',
            r'£[\d,]+\.?\d*',
            r'[\d,]+\.?\d*\s*(?:USD|EUR|GBP|INR)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return text.strip() if any(char.isdigit() for char in text) else "N/A"
    
    def extract_rating(self, text):
        if not text:
            return "N/A"
        
        rating_patterns = [
            r'(\d+\.?\d*)\s*(?:out of|/)\s*5',
            r'(\d+\.?\d*)\s*stars?',
            r'(\d+\.?\d*)/5',
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return text.strip() if any(char.isdigit() for char in text) else "N/A"

class SimpleProductScraper:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def fetch_url(self, url):
        """Fetch URL content using urllib"""
        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def scrape_website(self, url, max_products=20):
        """Scrape products from a website"""
        html_content = self.fetch_url(url)
        if not html_content:
            return []
        
        parser = ProductHTMLParser()
        parser.feed(html_content)
        
        products = parser.products[:max_products]
        for product in products:
            product['source_url'] = url
        
        return products
    
    def create_demo_data(self):
        """Create demo data when web scraping isn't possible"""
        return [
            {
                'name': 'Wireless Bluetooth Headphones',
                'price': '$79.99',
                'rating': '4.5',
                'source_url': 'demo_data'
            },
            {
                'name': 'Smartphone Case - Clear',
                'price': '$24.99',
                'rating': '4.2',
                'source_url': 'demo_data'
            },
            {
                'name': 'USB-C Charging Cable',
                'price': '$12.99',
                'rating': '4.7',
                'source_url': 'demo_data'
            },
            {
                'name': 'Portable Power Bank 10000mAh',
                'price': '$34.99',
                'rating': '4.3',
                'source_url': 'demo_data'
            },
            {
                'name': 'Wireless Mouse',
                'price': '$29.99',
                'rating': '4.1',
                'source_url': 'demo_data'
            }
        ]
    
    def save_to_csv(self, products, filename='products.csv'):
        """Save products to CSV file in the same directory as the script"""
        if not products:
            print("No products to save.")
            return
        
        try:
            # Get the directory where the current script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Create full path for the CSV file
            csv_path = os.path.join(script_dir, filename)
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'price', 'rating', 'source_url']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for product in products:
                    writer.writerow(product)
            
            print(f"Successfully saved {len(products)} products to {csv_path}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

def main():
    scraper = SimpleProductScraper()
    all_products = []
    
    print("E-commerce Product Scraper (Built-in Libraries Version)")
    print("=" * 55)
    
    # Show options
    print("\nOptions:")
    print("1. Use demo data (recommended for testing)")
    print("2. Try to scrape a website (may not work due to modern website complexity)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == '1':
        print("\nGenerating demo product data...")
        demo_products = scraper.create_demo_data()
        all_products.extend(demo_products)
        print(f"Created {len(demo_products)} demo products")
    
    elif choice == '2':
        print("\nNote: Modern websites often use JavaScript and anti-scraping measures.")
        print("This simple scraper may not work with many sites.")
        
        while True:
            url = input("\nEnter website URL (or 'done' to finish): ").strip()
            if url.lower() == 'done':
                break
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            print(f"Attempting to scrape {url}...")
            products = scraper.scrape_website(url, max_products=10)
            
            if products:
                all_products.extend(products)
                print(f"Found {len(products)} products")
            else:
                print("No products found or unable to scrape this site")
            
            time.sleep(2)
    
    else:
        print("Invalid choice. Using demo data.")
        demo_products = scraper.create_demo_data()
        all_products.extend(demo_products)
    
    # Save to CSV
    if all_products:
        scraper.save_to_csv(all_products, 'extracted_products.csv')
        
        # Display results
        print(f"\nExtracted Products Summary:")
        print("-" * 40)
        for i, product in enumerate(all_products, 1):
            print(f"{i}. {product['name'][:50]}...")
            print(f"   Price: {product['price']}")
            print(f"   Rating: {product['rating']}")
            print()
        
        print(f"All data saved to 'extracted_products.csv'")
    else:
        print("No products were extracted.")

if __name__ == "__main__":
    main()
