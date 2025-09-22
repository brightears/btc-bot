"""
Hypothesis File Maintenance
Prevents hypotheses.json from growing too large
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import logging


class HypothesisCleaner:
    """Maintains hypotheses file at reasonable size"""

    def __init__(self, max_per_category: int = 100):
        """
        Initialize cleaner

        Args:
            max_per_category: Maximum hypotheses to keep per category
        """
        self.max_per_category = max_per_category
        self.hypotheses_path = Path("knowledge/hypotheses.json")
        self.logger = logging.getLogger(__name__)

    def clean_hypotheses(self):
        """Clean and trim hypotheses file"""
        try:
            if not self.hypotheses_path.exists():
                return

            with open(self.hypotheses_path, 'r') as f:
                data = json.load(f)

            original_count = sum(len(data.get(cat, [])) for cat in ['pending', 'tested', 'validated', 'rejected'])

            # Trim each category to max size
            for category in ['pending', 'tested', 'validated', 'rejected']:
                if category in data and len(data[category]) > self.max_per_category:
                    # Keep only the most recent ones
                    data[category] = sorted(
                        data[category],
                        key=lambda x: x.get('created_at', ''),
                        reverse=True
                    )[:self.max_per_category]

            # Save cleaned data
            with open(self.hypotheses_path, 'w') as f:
                json.dump(data, f, indent=2)

            new_count = sum(len(data.get(cat, [])) for cat in ['pending', 'tested', 'validated', 'rejected'])

            if original_count != new_count:
                self.logger.info(f"Cleaned hypotheses: {original_count} → {new_count}")

        except Exception as e:
            self.logger.error(f"Error cleaning hypotheses: {e}")
            # Reset to safe state if corrupted
            self.reset_hypotheses()

    def reset_hypotheses(self):
        """Reset hypotheses to safe state"""
        safe_data = {
            "pending": [],
            "tested": [],
            "validated": [],
            "rejected": []
        }

        with open(self.hypotheses_path, 'w') as f:
            json.dump(safe_data, f, indent=2)

        self.logger.info("Reset hypotheses.json to safe state")