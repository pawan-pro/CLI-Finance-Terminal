from dataclasses import dataclass

@dataclass
class EconomicEvent:
    """Represents a single economic event"""
    date: str              # Date in YYYY-MM-DD format
    time_ist: str          # Time in IST (e.g., "14:30 IST")
    currency: str          # Currency code (e.g., "USD", "EUR")
    event_name: str        # Name of the economic event
    importance: int        # Importance level (1-3, where 3 is highest)
    forecast: str          # Forecasted value
    previous: str          # Previous value
    notes: str             # Additional notes about the event

    def __post_init__(self):
        """Validate event data after initialization"""
        if self.importance not in [1, 2, 3]:
            raise ValueError(f"Importance must be 1, 2, or 3, got {self.importance}")

        # Ensure strings are properly cleaned
        self.event_name = self.event_name.strip()
        self.currency = self.currency.strip().upper()
        self.notes = self.notes.strip()
