import requests
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
import re
from src.data.models.economic_event import EconomicEvent
from src.data import cache_manager

logger = logging.getLogger(__name__)

def get_current_week_dates() -> dict:
    """Get Monday, Sunday, and Tuesday dates for current week in YYYYMMDD format"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday - timedelta(days=1)
    tuesday = monday + timedelta(days=1)

    return {
        "monday": monday.strftime('%Y%m%d'),
        "sunday": sunday.strftime('%Y%m%d'),
        "tuesday": tuesday.strftime('%Y%m%d')
    }

def parse_time_to_24h(time_str: str) -> str:
    """Convert time string to 24-hour format"""
    # Try to match format like "08-Sep-25, Mon, 05:20"
    match = re.search(r'\d{2}:\d{2}', time_str)
    if match:
        return match.group(0)

    # Fallback for formats like "2:30 PM IST"
    try:
        time_clean = time_str.replace(" IST", "").strip()
        if ":" in time_clean and ("AM" not in time_clean.upper() and "PM" not in time_clean.upper()):
            return time_clean # Already 24h

        dt_obj = datetime.strptime(time_clean, "%I:%M %p")
        return dt_obj.strftime("%H:%M")
    except Exception:
        pass # Fallback to original string if all parsing fails

    return time_str

class QuantwaterScraper:
    def __init__(self):
        self.base_url = "https://quantwatertech.netlify.app/blogs/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })

    def get_economic_calendar(self) -> Optional[List[EconomicEvent]]:
        """Scrapes and returns the economic calendar events."""
        cache_key = cache_manager.get_cache_key("quantwater_calendar", {"week": get_current_week_dates()['monday']})
        cached_data = cache_manager.get_from_cache(cache_key)
        if cached_data:
            return [EconomicEvent(**event) for event in cached_data]

        url, _, _ = self.find_weekly_blog_post()
        if not url:
            return None

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            events = self.extract_events_from_html(response.text)

            # Convert to list of dicts for caching
            event_dicts = [event.__dict__ for event in events]
            cache_manager.set_to_cache(cache_key, event_dicts)

            return events
        except requests.RequestException as e:
            logger.error(f"Error fetching data from Quantwater: {e}")
            return None

    def find_weekly_blog_post(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Find weekly blog post using smart date detection"""
        dates = get_current_week_dates()
        dates_to_try = [
            (dates["monday"], "Monday"),
            (dates["sunday"], "Sunday"),
            (dates["tuesday"], "Tuesday")
        ]
        for date_str, day_name in dates_to_try:
            url = f"{self.base_url}{date_str}.html"
            try:
                response = self.session.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    return url, date_str, day_name
            except requests.RequestException:
                continue
            time.sleep(1)
        return None, None, None

    def extract_events_from_html(self, html_content: str) -> List[EconomicEvent]:
        """Extract economic events from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        events = []
        day_groups = soup.find_all('section', class_='event-day-group')
        for day_group in day_groups:
            date_h2 = day_group.find('h2', class_='timeline-date')
            if not date_h2: continue

            section_text = date_h2.get_text().strip()
            date_match = re.search(r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', section_text)
            if not date_match: continue

            day, month_name, year = date_match.groups()
            month_num = datetime.strptime(month_name, '%B').month
            event_date = f"{year}-{month_num:02d}-{int(day):02d}"

            event_cards = day_group.find_all('article', class_='event-card')
            for event_card in event_cards:
                event = self.parse_event_card(event_card, event_date)
                if event and event.importance == 3:
                    events.append(event)
        return events

    def parse_event_card(self, event_card, event_date: str) -> Optional[EconomicEvent]:
        """Parse individual event card"""
        title_h3 = event_card.find('h3', class_='event-title')
        if not title_h3: return None
        event_name = title_h3.get_text().strip()

        details_div = event_card.find('div', class_='event-details')
        if not details_div: return None

        details = {}
        for span in details_div.find_all('span'):
            if 'event-label' in span.get('class', []):
                label = span.get_text().strip()
                next_span = span.find_next_sibling('span')
                if next_span and 'event-value' in next_span.get('class', []):
                    value = next_span.get_text().strip()
                    details[label] = value

        time_ist = parse_time_to_24h(details.get('Date:', 'All Day'))
        importance = int(details.get('Importance:', '3'))

        if importance != 3: return None

        return EconomicEvent(
            date=event_date,
            time_ist=time_ist,
            currency=details.get('Currency:', 'USD'),
            event_name=event_name,
            importance=importance,
            forecast=details.get('Forecast:', 'N/A'),
            previous=details.get('Previous:', 'N/A'),
            notes=details.get('Notes:', 'No additional notes available')
        )
