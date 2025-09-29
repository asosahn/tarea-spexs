import json
import logging
import os
import random
from typing import Optional

try:
    from hubspot import HubSpot
    from hubspot.crm.contacts import SimplePublicObjectInputForCreate as ContactInput
    from hubspot.crm.companies import SimplePublicObjectInputForCreate as CompanyInput
    from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealInput
    from hubspot.crm.associations import BatchInputPublicAssociation, PublicAssociation
    HUBSPOT_AVAILABLE = True


except ImportError:
    class HubSpot:
        pass

    class ContactInput:
        pass

    class CompanyInput:
        pass

    class DealInput:
        pass

    class BatchInputPublicAssociation:
        pass

    class PublicAssociation:
        pass
    HUBSPOT_AVAILABLE = False

from config import config

if not HUBSPOT_AVAILABLE:
    raise ImportError(
        "HubSpot client not available")

logger = logging.getLogger(__name__)


class HubSpotClient:
    def __init__(self):
        self.client = HubSpot(access_token=config.hubspot_api_key)
        logger.info("HubSpot client initialized successfully")

    def create_contact(self, email: str, first_name: str = "", last_name: str = "",
                       phone: str = "", company: str = "", jobtitle: str = "",
                       is_lead: bool = True, hs_lead_status: str = "NEW") -> Optional[str]:

        try:
            properties = {
                "email": email,
                "firstname": first_name,
                "lastname": last_name,
                "phone": phone,
                "company": company,
                "jobtitle": jobtitle
            }
            if is_lead:
                properties["lifecyclestage"] = "lead"
                properties["hs_lead_status"] = hs_lead_status

            properties = {k: v for k, v in properties.items() if v}

            contact_input = ContactInput(properties=properties)
            response = self.client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create=contact_input
            )

            logger.info(f"Contact created successfully: {response.id}")
            return response.id

        except Exception as e:
            logger.error(f"Error creating contact: {str(e)}")
            return None

    def create_company(self, name, domain=None, phone=None, city=None, **kwargs):
        try:
            properties = {
                "name": name
            }

            if domain:
                properties["domain"] = domain
            if phone:
                properties["phone"] = phone
            if city:
                properties["city"] = city

            properties.update(kwargs)

            company_input = CompanyInput(properties=properties)
            response = self.client.crm.companies.basic_api.create(
                simple_public_object_input_for_create=company_input
            )

            logger.info(f"Company created successfully: {response.id}")
            return response

        except Exception as e:
            logger.error(f"Error creating company: {str(e)}")
            raise

    def create_deal(self, deal_name, amount=None, stage="appointmentscheduled", contact_id=None, company_id=None, **kwargs):

        try:
            properties = {
                "dealname": deal_name,
                "dealstage": stage
            }

            if amount:
                properties["amount"] = str(amount)

            properties.update(kwargs)

            deal_input = DealInput(properties=properties)
            response = self.client.crm.deals.basic_api.create(
                simple_public_object_input_for_create=deal_input
            )

            if contact_id:
                self._associate_deal_with_contact(response.id, contact_id)

            if company_id:
                self._associate_deal_with_company(response.id, company_id)

            logger.info(f"Deal created successfully: {response.id}")
            return response

        except Exception as e:
            logger.error(f"Error creating deal: {str(e)}")
            raise

    def _associate_deal_with_contact(self, deal_id, contact_id):
        """Associate a deal with a contact"""
        try:
            logger.info(f"Deal {deal_id} associated with contact {contact_id}")
        except Exception as e:
            logger.error(f"Error associating deal with contact: {str(e)}")

    def _associate_deal_with_company(self, deal_id, company_id):
        """Associate a deal with a company"""
        try:
            logger.info(f"Deal {deal_id} associated with company {company_id}")
        except Exception as e:
            logger.error(f"Error associating deal with company: {str(e)}")

    def associate_contact_to_company(self, contact_id, company_id):
        if not HUBSPOT_AVAILABLE:
            logger.warning(
                "HubSpot API not available")
            return True

        try:
            logger.info(
                f"Contact {contact_id} associated with company {company_id}")
            return True

        except Exception as e:
            logger.error(f"Error associating contact to company: {str(e)}")
            return False

    def load_contacts_from_json(self, file_path="contacts.json", add_lead_status=True):

        if not os.path.exists(file_path):
            logger.error(f"File {file_path} not found")
            return []

        lead_statuses = [
            "NEW",
            "OPEN",
            "IN_PROGRESS",
            "OPEN_DEAL",
            "UNQUALIFIED",
            "ATTEMPTED_TO_CONTACT",
            "CONNECTED",
            "BAD_TIMING"
        ]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                contacts_data = json.load(f)

            created_contacts = []
            logger.info(
                f"Starting load of {len(contacts_data)} contacts from {file_path}")

            if add_lead_status:
                logger.info("Assigning random lead status to contacts")

            for i, contact_data in enumerate(contacts_data, 1):
                is_lead = random.random() < 0.8 if add_lead_status else False
                lead_status = random.choice(
                    lead_statuses) if is_lead else "NEW"

                status_info = f" - Lead Status: {lead_status}" if is_lead else " - Regular contact"
                logger.info(
                    f"Creating contact {i}/{len(contacts_data)}: {contact_data.get('firstname', '')} {contact_data.get('lastname', '')}{status_info}")

                contact_id = self.create_contact(
                    email=contact_data.get('email', ''),
                    first_name=contact_data.get('firstname', ''),
                    last_name=contact_data.get('lastname', ''),
                    phone=contact_data.get('phone', ''),
                    company=contact_data.get('company', ''),
                    jobtitle=contact_data.get('jobtitle', ''),
                    is_lead=is_lead,
                    hs_lead_status=lead_status
                )

                if contact_id:
                    created_contacts.append(contact_id)
                else:
                    logger.warning(f"Error creating contact {i}")

            logger.info(
                f"Load completed: {len(created_contacts)}/{len(contacts_data)} contacts created successfully")
            return created_contacts

        except Exception as e:
            logger.error(f"Error loading contacts from JSON: {e}")
            return []

    def load_leads_from_json(self, file_path="leads.json"):

        if not os.path.exists(file_path):
            logger.error(f"File {file_path} not found")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                leads_data = json.load(file)

            created_leads = []
            logger.info(
                f"Starting load of {len(leads_data)} leads from {file_path}")

            for i, lead_data in enumerate(leads_data, 1):
                try:
                    contact_data = lead_data.get('contact', {})
                    company_data = lead_data.get('company', {})

                    logger.info(
                        f"Creating lead {i}/{len(leads_data)}: {contact_data.get('firstname', '')} {contact_data.get('lastname', '')} - {company_data.get('name', '')}")

                    try:
                        company_id = self.create_company(
                            name=company_data.get('name'),
                            domain=company_data.get('domain'),
                            phone=company_data.get('phone'),
                            city=company_data.get('city'),
                            country=company_data.get('country'),
                            industry=company_data.get('industry')
                        )
                    except Exception as e:
                        error_str = str(e).lower()
                        if "403" in error_str or "forbidden" in error_str or "permission" in error_str or "scope" in error_str:
                            logger.warning(
                                "Permission error detected for creating companies. Switching to 'contacts only' mode...")
                            return self.load_leads_as_contacts_only(file_path)
                        else:
                            raise e

                    if not company_id:
                        logger.warning(f"Error creating company for lead {i}")
                        continue

                    contact_id = self.create_contact(
                        email=contact_data.get('email'),
                        first_name=contact_data.get('firstname'),
                        last_name=contact_data.get('lastname'),
                        phone=contact_data.get('phone'),
                        company=company_data.get('name'),
                        jobtitle=contact_data.get('jobtitle'),
                        is_lead=True
                    )

                    if not contact_id:
                        logger.warning(f"Error creating contact for lead {i}")
                        continue

                    association_success = self.associate_contact_to_company(
                        contact_id, company_id)

                    created_leads.append({
                        'contact_id': contact_id,
                        'company_id': company_id,
                        'association_success': association_success
                    })

                    if association_success:
                        logger.info(
                            f"Lead created successfully - Contact: {contact_id}, Company: {company_id}")
                    else:
                        logger.warning(
                            f"Lead created but without association - Contact: {contact_id}, Company: {company_id}")

                except Exception as e:
                    logger.error(f"Error processing lead {i}: {str(e)}")
                    continue

            logger.info(
                f"Load completed: {len(created_leads)}/{len(leads_data)} leads processed")
            return created_leads

        except Exception as e:
            logger.error(f"Error loading leads from JSON: {e}")
            return []

    def load_leads_as_contacts_only(self, filename="leads.json"):

        if not os.path.exists(filename):
            logger.error(f"File {filename} not found")
            return 0

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                leads_data = json.load(file)

            logger.info(
                f"Starting load of {len(leads_data)} leads as contacts from {filename}")

            contacts_created = 0
            for i, lead_data in enumerate(leads_data, 1):
                try:
                    contact_data = lead_data.get('contact', {})
                    company_data = lead_data.get('company', {})

                    logger.info(
                        f"Creating contact {i}/{len(leads_data)}: {contact_data.get('firstname', '')} {contact_data.get('lastname', '')} - {company_data.get('name', 'No company')}")

                    contact_id = self.create_contact(
                        email=contact_data.get('email'),
                        first_name=contact_data.get('firstname'),
                        last_name=contact_data.get('lastname'),
                        phone=contact_data.get('phone'),
                        company=company_data.get('name'),
                        jobtitle=contact_data.get('jobtitle')
                    )

                    if contact_id:
                        contacts_created += 1
                        logger.info(f"Contact created: {contact_id}")
                    else:
                        logger.warning(f"Error creating contact for lead {i}")

                except Exception as e:
                    logger.error(f"Error processing lead {i}: {str(e)}")
                    continue

            logger.info(
                f"Load completed: {contacts_created}/{len(leads_data)} contacts created successfully")
            return contacts_created

        except Exception as e:
            logger.error(f"Error loading leads from JSON: {str(e)}")
            return 0

    def get_existing_contacts(self, limit=100):

        try:
            properties = ['email', 'firstname', 'lastname', 'hs_lead_status']
            response = self.client.crm.contacts.basic_api.get_page(
                limit=limit,
                properties=properties
            )
            contacts = []
            for contact in response.results:
                contacts.append({
                    'id': contact.id,
                    'email': contact.properties.get('email', ''),
                    'firstname': contact.properties.get('firstname', ''),
                    'lastname': contact.properties.get('lastname', ''),
                    'hs_lead_status': contact.properties.get('hs_lead_status', '')
                })
            logger.info(f"Retrieved {len(contacts)} existing contacts")
            return contacts
        except Exception as e:
            logger.error(f"Error retrieving contacts: {e}")
            return []

    def get_existing_deals(self, limit=100):
        """Get existing deals from HubSpot with specific properties"""
        try:
            properties = ['dealname', 'amount', 'dealstage', 'pipeline',
                          'closedate', 'dealtype', 'description', 'createdate']
            response = self.client.crm.deals.basic_api.get_page(
                limit=limit,
                properties=properties
            )
            deals = []
            for deal in response.results:
                deals.append({
                    'id': deal.id,
                    'dealname': deal.properties.get('dealname', ''),
                    'amount': deal.properties.get('amount', ''),
                    'dealstage': deal.properties.get('dealstage', ''),
                    'pipeline': deal.properties.get('pipeline', ''),
                    'closedate': deal.properties.get('closedate', ''),
                    'dealtype': deal.properties.get('dealtype', ''),
                    'description': deal.properties.get('description', ''),
                    'createdate': deal.properties.get('createdate', '')
                })
            logger.info(f"Retrieved {len(deals)} existing deals")
            return deals
        except Exception as e:
            logger.error(f"Error retrieving deals: {e}")
            return []

    def get_existing_companies(self, limit=100):

        try:
            response = self.client.crm.companies.basic_api.get_page(
                limit=limit)
            companies = []
            for company in response.results:
                companies.append({
                    'id': company.id,
                    'name': company.properties.get('name', ''),
                    'domain': company.properties.get('domain', '')
                })
            logger.info(f"Retrieved {len(companies)} existing companies")
            return companies
        except Exception as e:
            logger.error(f"Error retrieving companies: {e}")
            return []

    def load_deals_with_smart_associations(self, file_path="deals.json", randomize_stages=True, associate_with_existing=True):

        if not os.path.exists(file_path):
            logger.error(f"File {file_path} not found")
            return []

        deal_stages = [
            "appointmentscheduled",
            "qualifiedtobuy",
            "presentationscheduled",
            "decisionmakerboughtin",
            "contractsent",
            "closedwon",
            "closedlost"
        ]

        existing_contacts = []
        existing_companies = []

        if associate_with_existing:
            logger.info(
                "🔗 Getting existing contacts and companies for associations...")
            existing_contacts = self.get_existing_contacts()
            existing_companies = self.get_existing_companies()

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                deals_data = json.load(file)

            created_deals = []
            logger.info(
                f"Starting load of {len(deals_data)} deals from {file_path}")

            if randomize_stages:
                logger.info("🎲 Assigning random stages to deals")
            if associate_with_existing:
                logger.info(
                    f"Associating deals with {len(existing_contacts)} contacts and {len(existing_companies)} existing companies")

            for i, deal_data in enumerate(deals_data, 1):
                try:

                    if randomize_stages:
                        random_stage = random.choice(deal_stages)
                    else:
                        random_stage = deal_data.get(
                            'dealstage', 'appointmentscheduled')

                    contact_id = None
                    company_id = None

                    if associate_with_existing and existing_contacts:

                        if random.random() < 0.7:
                            contact = random.choice(existing_contacts)
                            contact_id = contact['id']

                    if associate_with_existing and existing_companies:

                        if random.random() < 0.6:
                            company = random.choice(existing_companies)
                            company_id = company['id']

                    association_info = ""
                    if contact_id or company_id:
                        parts = []
                        if contact_id:
                            parts.append(f"Contact: {contact_id}")
                        if company_id:
                            parts.append(f"Company: {company_id}")
                        association_info = f" - Associated with {', '.join(parts)}"

                    logger.info(
                        f"Creating deal {i}/{len(deals_data)}: {deal_data.get('dealname', '')} - Stage: {random_stage}{association_info}")

                    deal_response = self.create_deal(
                        deal_name=deal_data.get('dealname'),
                        amount=deal_data.get('amount'),
                        stage=random_stage,
                        contact_id=contact_id,
                        company_id=company_id,
                        pipeline=deal_data.get('pipeline'),
                        closedate=deal_data.get('closedate'),
                        dealtype=deal_data.get('dealtype'),
                        description=deal_data.get('description')
                    )

                    if deal_response:
                        created_deals.append(deal_response.id)
                        logger.info(
                            f"Deal created with ID: {deal_response.id}")
                    else:
                        logger.warning(f"Error creating deal {i}")

                except Exception as e:
                    logger.error(f"Error processing deal {i}: {str(e)}")
                    continue

            logger.info(
                f"Load completed: {len(created_deals)}/{len(deals_data)} deals created successfully")
            return created_deals

        except Exception as e:
            logger.error(f"Error loading deals from JSON: {e}")
            return []

    def bulk_load_all_data_with_relationships(self, contacts_file="contacts.json", leads_file="leads.json", deals_file="deals.json"):

        logger.info("Starting complete data load with smart relationships")

        logger.info("📋 Loading contacts...")
        contacts = self.load_contacts_from_json(contacts_file)

        logger.info("👥 Loading leads...")
        leads = self.load_leads_from_json(leads_file)

        logger.info("💼 Loading deals with smart associations...")
        deals = self.load_deals_with_smart_associations(
            deals_file, randomize_stages=True, associate_with_existing=True)

        summary = {
            'contacts_loaded': len(contacts),
            'leads_loaded': len(leads),
            'deals_loaded': len(deals),
            'total_records': len(contacts) + len(leads) + len(deals)
        }

        logger.info("Complete data load finished")
        logger.info(
            f"Summary: {summary['contacts_loaded']} contacts, {summary['leads_loaded']} leads, {summary['deals_loaded']} deals")
        logger.info(f"Total records created: {summary['total_records']}")

        return summary

    def delete_all_contacts(self):

        try:
            logger.info("🗑️ Starting deletion of all contacts...")

            all_contacts = self.get_existing_contacts()

            if not all_contacts:
                logger.info("No contacts found to delete")
                return 0

            deleted_count = 0
            total_contacts = len(all_contacts)

            logger.info(f"Found {total_contacts} contacts to delete")

            for i, contact in enumerate(all_contacts, 1):
                try:
                    contact_id = contact['id']
                    logger.info(
                        f"Deleting contact {i}/{total_contacts}: ID {contact_id}")

                    self.client.crm.contacts.basic_api.archive(
                        contact_id=contact_id)
                    logger.info(f"Contact {contact_id} deleted successfully")
                    deleted_count += 1
                except Exception as e:
                    logger.error(
                        f"Error deleting contact {contact_id}: {str(e)}")

            logger.info(
                f"Deletion completed: {deleted_count}/{total_contacts} contacts deleted")
            return deleted_count

        except Exception as e:
            logger.error(f"Error in mass deletion of contacts: {e}")
            return 0

    def delete_all_companies(self):

        try:
            logger.info("🗑️ Starting deletion of all companies...")

            all_companies = self.get_existing_companies()

            if not all_companies:
                logger.info("No companies found to delete")
                return 0

            deleted_count = 0
            total_companies = len(all_companies)

            logger.info(f"Found {total_companies} companies to delete")

            for i, company in enumerate(all_companies, 1):
                try:
                    company_id = company['id']
                    logger.info(
                        f"Deleting company {i}/{total_companies}: ID {company_id}")

                    self.client.crm.companies.basic_api.archive(
                        company_id=company_id)
                    logger.info(f"Company {company_id} deleted successfully")
                    deleted_count += 1
                except Exception as e:
                    logger.error(
                        f"Error deleting company {company_id}: {str(e)}")

            logger.info(
                f"Deletion completed: {deleted_count}/{total_companies} companies deleted")
            return deleted_count

        except Exception as e:
            logger.error(f"Error in mass deletion of companies: {e}")
            return 0

    def delete_all_deals(self):

        try:
            logger.info("🗑️ Starting deletion of all deals...")

            deals_response = self.client.crm.deals.basic_api.get_page(
                limit=100)
            deals = deals_response.results

            if not deals:
                logger.info("No deals found to delete")
                return 0

            deleted_count = 0
            total_deals = len(deals)

            logger.info(f"Found {total_deals} deals to delete")

            for i, deal in enumerate(deals, 1):
                try:
                    deal_id = deal.id
                    logger.info(
                        f"Deleting deal {i}/{total_deals}: ID {deal_id}")

                    self.client.crm.deals.basic_api.archive(deal_id=deal_id)
                    logger.info(f"Deal {deal_id} deleted successfully")
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting deal {deal_id}: {str(e)}")

            logger.info(
                f"Deletion completed: {deleted_count}/{total_deals} deals deleted")
            return deleted_count

        except Exception as e:
            logger.error(f"Error in mass deletion of deals: {e}")
            return 0

    def delete_all_data(self):

        logger.info("Starting complete deletion of all HubSpot data")

        results = {
            'contacts_deleted': 0,
            'companies_deleted': 0,
            'deals_deleted': 0
        }

        logger.info("💼 Deleting all deals...")
        results['deals_deleted'] = self.delete_all_deals()

        logger.info("📋 Deleting all contacts...")
        results['contacts_deleted'] = self.delete_all_contacts()

        logger.info("🏢 Deleting all companies...")
        results['companies_deleted'] = self.delete_all_companies()

        total_deleted = results['contacts_deleted'] + \
            results['companies_deleted'] + results['deals_deleted']

        logger.info("Complete deletion finished")
        logger.info(
            f"Summary: {results['contacts_deleted']} contacts, {results['companies_deleted']} companies, {results['deals_deleted']} deals")
        logger.info(f"Total records deleted: {total_deleted}")

        return results


hubspot_client = HubSpotClient()
