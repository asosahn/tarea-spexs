import logging
from hubspot_client import hubspot_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_all_data():
    """Load all data with smart relationships"""
    logger.info("=== Loading all data with smart relationships ===")

    try:
        results = hubspot_client.bulk_load_all_data_with_relationships()

        logger.info("LOADING SUMMARY:")
        logger.info(f"Contacts: {results['contacts_loaded']}")
        logger.info(f"Leads: {results['leads_loaded']}")
        logger.info(f"Deals: {results['deals_loaded']}")
        logger.info(f"Total: {results['total_records']} records")

        return results
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None


def delete_all_data():
    logger.warning("WARNING: You are about to delete ALL data from HubSpot")

    confirmation = input("Type 'YES, DELETE ALL' to confirm: ").strip()

    if confirmation == "YES, DELETE ALL":
        confirmation2 = input(
            "Are you absolutely sure? Type 'YES, DELETE ALL' again: ").strip()

        if confirmation2 == "YES, DELETE ALL":
            logger.info("=== Starting complete cleanup ===")
            results = hubspot_client.delete_all_data()

            total_deleted = results['contacts_deleted'] + \
                results['companies_deleted'] + results['deals_deleted']
            logger.info(
                f"Cleanup completed. Total deleted: {total_deleted} records")
            return total_deleted
        else:
            logger.info("Operation cancelled in second confirmation")
            return 0
    else:
        logger.info("Operation cancelled")
        return None


def main():
    logger.info("Starting HubSpot API Client")

    try:
        print("\n" + "="*60)
        print("HUBSPOT API CLIENT")
        print("="*60)
        print("1. LOAD DATA")
        print("2. DELETE ALL")
        print("="*60)

        option = input("Select an option (1 or 2): ").strip()

        if option == "1":
            logger.info("Loading all data with smart relationships...")
            load_all_data()

        elif option == "2":
            logger.info("Starting complete cleanup...")
            delete_all_data()

        else:
            logger.warning("Invalid option. Please select 1 or 2.")

        logger.info("Execution completed successfully")

    except KeyboardInterrupt:
        logger.info("Execution cancelled by user")
    except Exception as e:
        logger.error(f"Error in execution: {e}")


if __name__ == "__main__":
    main()
