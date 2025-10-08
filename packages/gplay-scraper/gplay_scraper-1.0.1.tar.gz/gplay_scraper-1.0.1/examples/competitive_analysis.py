#!/usr/bin/env python3
"""
Competitive analysis example using GPlay Scraper.

Demonstrates how to compare multiple apps across key metrics
like ratings, install counts, and user engagement for competitive intelligence.
"""

import sys
from gplay_scraper import GPlayScraper

def competitive_analysis():
    """Perform competitive analysis on messaging apps.
    
    Compares popular messaging apps across key performance indicators
    and ranks them by user rating to identify market leaders.
    """
    # Set UTF-8 encoding for Windows console
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Initialize scraper for batch analysis
    scraper = GPlayScraper()
    
    # Define competitor apps in messaging category
    apps = {
        "WhatsApp": "com.whatsapp",
        "Telegram": "org.telegram.messenger", 
        "Signal": "org.thoughtcrime.securesms"
    }
    
    print("=== Competitive Analysis: Messaging Apps ===\n")
    
    results = []
    # Analyze each competitor app
    for name, app_id in apps.items():
        try:
            # Get key competitive metrics
            data = scraper.get_fields(app_id, [
                "title", "score", "ratings", "installs", "realInstalls"
            ])
            data["name"] = name
            results.append(data)
            print(f"[OK] Analyzed {name}")
        except Exception as e:
            print(f"[ERROR] Error analyzing {name}: {e}")
    
    if not results:
        print("No apps successfully analyzed.")
        return
    
    # Sort competitors by user rating (highest first)
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    print("\n=== Ranking by User Rating ===\n")
    for i, app in enumerate(results, 1):
        score = app.get('score', 'N/A')
        ratings = app.get('ratings', 'N/A')
        installs = app.get('installs', 'N/A')
        print(f"{i}. {app['name']}:")
        print(f"   Rating: {score} stars ({ratings} reviews)")
        print(f"   Installs: {installs}")
        print()

def main():
    """Main function to run competitive analysis."""
    competitive_analysis()

if __name__ == "__main__":
    main()