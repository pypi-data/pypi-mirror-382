#!/usr/bin/env python3
"""
Basic usage examples for GPlay Scraper.

Demonstrates the core functionality of the Google Play Store scraper
including single field access, multiple field retrieval, and complete analysis.
"""

from gplay_scraper import GPlayScraper

def main():
    """Demonstrate basic GPlay Scraper functionality with real examples."""
    # Initialize the scraper instance
    scraper = GPlayScraper()
    
    # Use WhatsApp as example (popular, stable app)
    app_id = "com.whatsapp"
    
    print("=== Basic Usage Examples ===\n")
    
    # 1. Get single field - most efficient for one piece of data
    print("1. Single field access:")
    title = scraper.get_field(app_id, "title")
    print(f"   Title: {title}\n")
    
    # 2. Get multiple fields - efficient for several specific fields
    print("2. Multiple fields access:")
    data = scraper.get_fields(app_id, ["title", "developer", "score", "installs"])
    for field, value in data.items():
        print(f"   {field}: {value}")
    
    # 3. Complete analysis - gets all 65+ available fields
    print("\n3. Complete analysis:")
    all_data = scraper.analyze(app_id)
    print(f"   Total fields retrieved: {len(all_data)}")
    print(f"   App rating: {all_data.get('score', 'N/A')}")
    print(f"   Install count: {all_data.get('installs', 'N/A')}")

if __name__ == "__main__":
    main()