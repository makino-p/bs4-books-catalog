"""
Book Catalog Scraper
Scrapes http://books.toscrape.com to create a comprehensive book catalog
with detailed information, including price analysis and category statistics.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from typing import List, Dict, Any
from collections import defaultdict

def normalize_rating(rating_text: str) -> int:
    """Convert textual rating to numeric scale (1-5)."""
    rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    return rating_map.get(rating_text, 0)

def scrape_catalog_page(page_url: str) -> List[Dict[str, Any]]:
    """Scrape a single catalog page for basic book information."""
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        books = []
        
        for item in soup.select('article.product_pod'):
            # Extract basic book information
            title = item.h3.a.get('title', '')
            price_text = item.select_one('p.price_color').text.strip()
            rating_class = item.select_one('p.star-rating')['class'][1]
            availability = item.select_one('p.availability').text.strip()
            detail_path = item.h3.a['href']
            
            # Build absolute URL for detail page
            detail_url = f"http://books.toscrape.com/{detail_path}"
            
            books.append({
                'title': title,
                'price': float(price_text.replace('£', '')),
                'rating': normalize_rating(rating_class),
                'availability': availability,
                'detail_url': detail_url
            })
            
        return books
        
    except requests.RequestException as e:
        print(f"Error fetching page {page_url}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error parsing page {page_url}: {e}")
        return []

def scrape_book_detail(detail_url: str) -> Dict[str, Any]:
    """Scrape detailed information from a book's specific page."""
    try:
        response = requests.get(detail_url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract detailed information
        product_description = soup.select_one('#product_description + p')
        category = soup.select_one('ul.breadcrumb li:nth-child(3)').text.strip()
        upc = soup.select_one('table.table tr:first-child td').text.strip()
        
        # Find number of reviews (look for the specific row)
        num_reviews = 0
        for row in soup.select('table.table tr'):
            th = row.find('th')
            if th and 'review' in th.text.lower():
                num_reviews = int(row.select_one('td').text.strip())
                break
        
        return {
            'product_description': product_description.text.strip() if product_description else '',
            'category': category,
            'upc': upc,
            'num_reviews': num_reviews
        }
        
    except requests.RequestException as e:
        print(f"Error fetching detail page {detail_url}: {e}")
    except Exception as e:
        print(f"Error parsing detail page {detail_url}: {e}")
    
    # Return default values if detail scraping fails
    return {
        'product_description': 'detail_not_fetched',
        'category': 'detail_not_fetched',
        'upc': 'detail_not_fetched',
        'num_reviews': 'detail_not_fetched'
    }

def aggregate_by_category(books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate book statistics by category."""
    category_data = defaultdict(list)
    
    for book in books:
        category = book['category']
        if category == 'detail_not_fetched':
            continue
            
        category_data[category].append({
            'price': book['price'],
            'rating': book['rating']
        })
    
    stats = []
    for category, data in category_data.items():
        avg_price = sum(d['price'] for d in data) / len(data)
        avg_rating = sum(d['rating'] for d in data) / len(data)
        
        stats.append({
            'category': category,
            'avg_price': round(avg_price, 2),
            'avg_rating': round(avg_rating, 2),
            'count': len(data)
        })
    
    return stats

def save_catalog(data: List[Dict[str, Any]], filename: str, mode: str = 'w') -> None:
    """Save catalog data to CSV file."""
    if not data:
        return
        
    fieldnames = data[0].keys()
    
    with open(filename, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def print_summary(books: List[Dict[str, Any]], stats: List[Dict[str, Any]]) -> None:
    """Print summary statistics of the scraped data."""
    print("── SUMMARY ──")
    
    total_books = len(books)
    detailed_books = sum(1 for b in books if b['category'] != 'detail_not_fetched')
    
    # Calculate overall averages
    valid_ratings = [b['rating'] for b in books]
    avg_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0
    
    valid_prices = [b['price'] for b in books]
    avg_price = sum(valid_prices) / len(valid_prices) if valid_prices else 0
    
    categories_covered = len(stats)
    
    print(f"Total books scraped: {total_books}")
    print(f"Books with detailed information: {detailed_books}")
    print(f"Average price of all books: £{avg_price:.2f}")
    print(f"Average rating of all books: {avg_rating:.2f}/5.0")
    print(f"Categories covered: {categories_covered}")
    
    if stats:
        print("\nTop 3 Categories by Average Rating:")
        sorted_stats = sorted(stats, key=lambda x: x['avg_rating'], reverse=True)[:3]
        for i, stat in enumerate(sorted_stats, 1):
            print(f"{i}. {stat['category']} ({stat['count']} books) - £{stat['avg_price']:.2f} avg price, {stat['avg_rating']}/5.0 avg rating")

def main():
    """Main function to orchestrate the scraping process."""
    BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
    DETAIL_LIMIT = 30
    
    books_catalog = []
    detail_counter = 0
    
    print("── PROGRESS ──")
    
    for page_num in range(1, 51):
        page_url = BASE_URL.format(page_num)
        
        print(f"Scraping page {page_num}...")
        books_on_page = scrape_catalog_page(page_url)
        
        for book in books_on_page:
            if detail_counter < DETAIL_LIMIT:
                detail_data = scrape_book_detail(book['detail_url'])
                detail_counter += 1
            else:
                detail_data = {
                    'product_description': 'detail_not_fetched',
                    'category': 'detail_not_fetched',
                    'upc': 'detail_not_fetched',
                    'num_reviews': 'detail_not_fetched'
                }
                
            # Merge basic and detailed book data
            merged_book = {**book, **detail_data}
            books_catalog.append(merged_book)
        
        if page_num % 5 == 0:
            print(f"Processed {page_num} pages. Total books collected: {len(books_catalog)}")
        # Add a small delay to be respectful
        time.sleep(0.5)
    
    # Save the collected data
    print("\nSaving data to CSV files...")
    save_catalog(books_catalog, 'books_catalog.csv')
    
    # Aggregate and save statistics
    stats = aggregate_by_category(books_catalog)
    save_catalog(stats, 'books_stats.csv')
    
    # Print final summary
    print_summary(books_catalog, stats)

if __name__ == '__main__':
    main()