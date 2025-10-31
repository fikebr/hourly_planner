import logging
import argparse
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
    parser = argparse.ArgumentParser(
        prog='hourly_planner',
        description='Generate a customizable daily planner PDF from a TOML configuration file.',
        epilog='Example: python main.py -t my_schedule.toml'
    )
    
    parser.add_argument(
        '-t', '--toml',
        type=str,
        required=True,
        metavar='FILE',
        help='Path to the TOML configuration file (e.g., 2025-10-31.toml)'
    )
    
    args = parser.parse_args()
    
    logger.info("Starting hourly planner generator")
    generate_from_toml(args.toml)


if __name__ == "__main__":
    main()


