import logging
from core.planner_generator import generate_from_toml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('planner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point - generates planner from TOML file."""
    generate_from_toml("2025-10-31_hourly.toml")


if __name__ == "__main__":
    main()


