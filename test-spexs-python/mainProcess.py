import argparse
from hubspot_client import HubSpotClient
from config import config
import pandas as pd
from pymongo import MongoClient
from pymongo.operations import UpdateOne


def get_mongo_client():
    try:
        client = MongoClient(config.mongodb_uri)
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None


def upsert_leads_to_mongo(leads_df):
    if leads_df.empty:
        print("No leads data to upsert")
        return
    client = get_mongo_client()
    if not client:
        print("Failed to connect to MongoDB. Skipping upsert.")
        return
    try:
        db = client[config.mongodb_database]
        collection = db.leads
        bulk_operations = []
        for _, row in leads_df.iterrows():
            lead_data = row.to_dict()
            lead_data = {k: (None if pd.isna(v) else v)
                         for k, v in lead_data.items()}
            operation = UpdateOne(
                {"id": lead_data["id"]},
                {"$set": lead_data},
                upsert=True
            )
            bulk_operations.append(operation)
        if bulk_operations:
            result = collection.bulk_write(bulk_operations)
            print(f"MongoDB Leads Upsert Results:")
            print(f"  - Matched: {result.matched_count}")
            print(f"  - Modified: {result.modified_count}")
            print(f"  - Upserted: {result.upserted_count}")

    except Exception as e:
        print(f"Error during leads upsert: {e}")
    finally:
        client.close()


def upsert_deals_to_mongo(deals_df):
    if deals_df.empty:
        print("No deals data to upsert")
        return

    client = get_mongo_client()
    if not client:
        print("Failed to connect to MongoDB. Skipping upsert.")
        return

    try:
        db = client[config.mongodb_database]
        collection = db.deals

        bulk_operations = []

        for _, row in deals_df.iterrows():
            deal_data = row.to_dict()
            deal_data = {k: (None if pd.isna(v) else v)
                         for k, v in deal_data.items()}

            if 'amount' in deal_data and deal_data['amount'] is not None:
                try:
                    deal_data['amount'] = float(deal_data['amount'])
                except (ValueError, TypeError):
                    deal_data['amount'] = None

            operation = UpdateOne(
                {"id": deal_data["id"]},
                {"$set": deal_data},
                upsert=True
            )
            bulk_operations.append(operation)

        if bulk_operations:
            result = collection.bulk_write(bulk_operations)
            print(f"MongoDB Deals Upsert Results:")
            print(f"  - Matched: {result.matched_count}")
            print(f"  - Modified: {result.modified_count}")
            print(f"  - Upserted: {result.upserted_count}")

    except Exception as e:
        print(f"Error during deals upsert: {e}")
    finally:
        client.close()


def get_lead_status_mapping():
    client = get_mongo_client()
    db = client[config.mongodb_database]
    collection = db.lead_status
    lead_status_docs = list(collection.find())
    mapping = {}
    for doc in lead_status_docs:
        if 'lead_status' in doc and 'id' in doc:
            mapping[doc['lead_status']] = doc['id']
    client.close()
    return mapping


def get_leads_dataframe():
    client = HubSpotClient()

    leads_data = client.get_existing_contacts(limit=100)

    df = pd.DataFrame(leads_data)

    if not df.empty:
        df = df.rename(columns={
            'firstname': 'first_name',
            'lastname': 'last_name',
            'hs_lead_status': 'lead_status'
        })

        df['full_name'] = df['first_name'].fillna(
            '') + ' ' + df['last_name'].fillna('')
        df['full_name'] = df['full_name'].str.strip()

        lead_status_mapping = get_lead_status_mapping()

        df['lead_status_id'] = df['lead_status'].map(
            lead_status_mapping).fillna(0).astype(int)

    return df


def get_deals_dataframe():
    client = HubSpotClient()
    deals_data = client.get_existing_deals(limit=100)
    df = pd.DataFrame(deals_data)
    
    if not df.empty:
        df = df.rename(columns={
            'dealtype': 'deal_type',
            'dealstage': 'deal_stage',
            'dealname': 'deal_name',
            'closedate': 'close_date',
            'createdate': 'create_date'
        })
        
        if 'close_date' in df.columns:
            df['close_date'] = pd.to_datetime(df['close_date'], errors='coerce')
        
        if 'create_date' in df.columns:
            df['create_date'] = pd.to_datetime(df['create_date'], errors='coerce')
    
    return df


def upsert_lead_status_summary():
    try:
        client = get_mongo_client()
        db = client[config.mongodb_database]
        leads_collection = db['leads']
        summary_collection = db['resume_lead_status']

        pipeline = [
            {
                "$group": {
                    "_id": "$lead_status_id",
                    "total": {"$sum": 1},
                    "status": {"$first": "$lead_status"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": "$_id",
                    "total": 1,
                    "status": 1
                }
            }
        ]

        summary_results = list(leads_collection.aggregate(pipeline))

        if summary_results:
            bulk_operations = []
            for result in summary_results:
                bulk_operations.append(
                    UpdateOne(
                        {"id": result["id"]},
                        {"$set": result},
                        upsert=True
                    )
                )
            if bulk_operations:
                upsert_result = summary_collection.bulk_write(bulk_operations)
                print("MongoDB Lead Status Summary Upsert Results:")
                print(f"  - Matched: {upsert_result.matched_count}")
                print(f"  - Modified: {upsert_result.modified_count}")
                print(f"  - Upserted: {upsert_result.upserted_count}")

                print("\nLead Status Summary:")
                for result in summary_results:
                    print(
                        f"  - Status: {result['status']} (ID: {result['id']}) - Total: {result['total']}")
            else:
                print("No summary data to upsert")
        else:
            print("No leads found for summary aggregation")

    except Exception as e:
        print(f"Error creating lead status summary: {e}")
    finally:
        if 'client' in locals():
            client.close()


def upsert_deals_summary():
    try:
        client = get_mongo_client()
        db = client[config.mongodb_database]
        deals_collection = db['deals']
        summary_collection = db['total_deals']

        pipeline = [
            {
                "$group": {
                    "_id": "$deal_stage",
                    "total": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": "$_id",
                    "total": 1,
                    "amount": 1
                }
            }
        ]

        summary_results = list(deals_collection.aggregate(pipeline))

        if summary_results:
            bulk_operations = []
            for result in summary_results:
                bulk_operations.append(
                    UpdateOne(
                        {"id": result["id"]},
                        {"$set": result},
                        upsert=True
                    )
                )
            if bulk_operations:
                upsert_result = summary_collection.bulk_write(bulk_operations)
                print("MongoDB Deals Summary Upsert Results:")
                print(f"  - Matched: {upsert_result.matched_count}")
                print(f"  - Modified: {upsert_result.modified_count}")
                print(f"  - Upserted: {upsert_result.upserted_count}")

                print("\nDeals Summary by Stage:")
                for result in summary_results:
                    print(f"  - Stage: {result['id']} - Total: {result['total']} - Amount: ${result['amount']:,.2f}")
            else:
                print("No deals summary data to upsert")
        else:
            print("No deals found for summary aggregation")

    except Exception as e:
        print(f"Error creating deals summary: {e}")
    finally:
        if 'client' in locals():
            client.close()


def upsert_deals_close_summary():
    try:
        client = get_mongo_client()
        db = client[config.mongodb_database]
        deals_collection = db['deals']
        summary_collection = db['resume_close_deals']

        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$close_date"},
                        "month": {"$month": "$close_date"},
                        "deal_stage": "$deal_stage"
                    },
                    "count": {"$sum": 1},
                    "amount": {"$sum": "$amount"}
                }
            },
            {
                "$sort": {
                    "_id.year": 1,
                    "_id.month": 1,
                    "_id.deal_stage": 1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "deal_stage": "$_id.deal_stage",
                    "count": 1,
                    "amount": 1
                }
            }
        ]

        summary_results = list(deals_collection.aggregate(pipeline))

        if summary_results:
            bulk_operations = []
            for result in summary_results:
                bulk_operations.append(
                    UpdateOne(
                        {
                            "year": result["year"],
                            "month": result["month"],
                            "deal_stage": result["deal_stage"]
                        },
                        {"$set": result},
                        upsert=True
                    )
                )
            if bulk_operations:
                upsert_result = summary_collection.bulk_write(bulk_operations)
                print("MongoDB Deals Close Summary Upsert Results:")
                print(f"  - Matched: {upsert_result.matched_count}")
                print(f"  - Modified: {upsert_result.modified_count}")
                print(f"  - Upserted: {upsert_result.upserted_count}")

                print("\nDeals Close Summary by Year/Month/Stage:")
                for result in summary_results:
                    print(f"  - {result['year']}/{result['month']:02d} - Stage: {result['deal_stage']} - Count: {result['count']} - Amount: ${result['amount']:,.2f}")
            else:
                print("No deals close summary data to upsert")
        else:
            print("No deals found for close summary aggregation")

    except Exception as e:
        print(f"Error creating deals close summary: {e}")
    finally:
        if 'client' in locals():
            client.close()


def main():
    parser = argparse.ArgumentParser(description='Extract data from HubSpot')
    parser.add_argument('--type', choices=['leads', 'deals'], default='leads',
                        help='Type of data to extract: leads or deals (default: leads)')

    args = parser.parse_args()

    try:
        if args.type == 'leads':
            data_df = get_leads_dataframe()
            data_type = "Leads"
        else:
            data_df = get_deals_dataframe()
            data_type = "Deals"

        print(f"{data_type} from HubSpot:")
        print("=" * 50)

        if args.type == 'deals':
            key_columns = ['id', 'dealname', 'amount',
                           'dealstage', 'pipeline', 'closedate']
            available_columns = [
                col for col in key_columns if col in data_df.columns]
            print("Key Deal Information:")
            print(data_df[available_columns])
            print("\nAll columns available:", list(data_df.columns))
        else:
            print(data_df)

        print("=" * 50)
        print(f"Total {data_type.lower()}: {len(data_df)}")

        print("\n" + "=" * 50)
        print("Upserting data to MongoDB...")
        print("=" * 50)

        if args.type == 'leads':
            upsert_leads_to_mongo(data_df)
            print("\n" + "=" * 50)
            print("Creating lead status summary...")
            print("=" * 50)
            upsert_lead_status_summary()
        else:
            upsert_deals_to_mongo(data_df)
            print("\n" + "=" * 50)
            print("Creating deals summary...")
            print("=" * 50)
            upsert_deals_summary()
            print("\n" + "=" * 50)
            print("Creating deals close summary...")
            print("=" * 50)
            upsert_deals_close_summary()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
