# bs4-books-catalog

> BeautifulSoup — Full Book Catalog Scraper

`BeautifulSoup4` `Web Scraping` `Requests` `Pagination`

---

## Overview

Create a professional book catalog scraper using requests and BeautifulSoup4.

Target: http://books.toscrape.com (scrape all 50 pages)

Requirements:
- Scrape ALL 50 pages of the catalog
- Extract per book: title, price, rating (convert text to number), availability,
  category, product_description, upc, num_reviews
- Navigate into each book's detail page to get full description and UPC
  (only do this for first 30 books to stay fast — mark rest as "detail_not_fetched")
- Handle the star-rating text (One/Two/Three/Four/Five → 1/2/3/4/5)
- Show progress every 5 pages
- Save all books to books_c

## Features

- Scrape ALL 50 pages of the catalog
- Extract per book: title, price, rating (convert text to number), availability,
- Navigate into each book's detail page to get full description and UPC
- Handle the star-rating text (One/Two/Three/Four/Five → 1/2/3/4/5)
- Show progress every 5 pages
- Save all books to books_catalog.csv
- Save aggregated stats to books_stats.csv: avg price, avg rating, count per category
- Functions: scrape_catalog_page(), scrape_book_detail(), normalize_rating(),

---

## Tech Stack

| Library | Purpose |
|---|---|
| `bs4` | Data processing |
| `requests` | Data processing |

---

## Quick Start

```bash
git clone https://github.com/makino-p/bs4-books-catalog.git
cd bs4-books-catalog
pip install bs4 requests
python solution.py
```

## Dependencies

```bash
pip install bs4 requests
```

## Key Functions

- `normalize_rating()`
- `scrape_catalog_page()`
- `scrape_book_detail()`
- `aggregate_by_category()`
- `save_catalog()`
- `print_summary()`
- `main()`


---

## Project Stats

- **Lines of code**: 218
- **Functions**: 7
- **Output files**: 0

---

## Skills Demonstrated

`BeautifulSoup4` `Web Scraping` `Requests` `Pagination`

---

## License

MIT
