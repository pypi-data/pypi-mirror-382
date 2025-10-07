"""LDAP Update class for Google."""

import re
from datetime import date, timedelta

from bits.ldap.server import Server


class Google(Server):
    """Google LDAP Update class."""

    def get_default_ous(self):
        """Return list of default ous."""
        # add ous to the list of default_ous
        # these ous do not have any ldap users in them but they need to exist for GCDS
        items = [
            # devices
            "ou=Devices",
            "ou=Admin,ou=Devices",
            "ou=Allow Non-Broad Logins,ou=Devices",
            "ou=Digital Signage,ou=Devices",
            "ou=Loaners,ou=Devices",
            "ou=Meet,ou=Devices",
            "ou=Meet Unmonitored,ou=Devices",
            "ou=Unassigned,ou=Devices",
            # people
            "ou=Insecure,ou=People",
        ]
        return [f"{x},{self.ldap.base_dn}" for x in items ]

    def get_account_dn(self, account):
        """Return the dn for an other account."""
        # set the base ou
        ou = f"ou=Other Accounts,{self.ldap.base_dn}"

        # check for an ou override
        if account.google_ou:
            parts = account.google_ou.split("/")
            for part in parts:
                ou = f"ou={part},{ou}"

        # otherwise, get the type ou
        else:
            type_ou = self.get_account_type_ou(account)
            if type_ou:
                ou = f"ou={type_ou},{ou}"

        # get primary domain
        domain = None
        if "primary" in self.ldap.domains:
            domain = self.ldap.domains["primary"]

        # get primary domain info
        domain_info = {}
        if domain in account.domains:
            domain_info = account.domains[domain]

        # get secure info
        if domain_info.get("secure"):
            ou = f"ou=Secure,{ou}"

        return f"cn={account.displayName},{ou}"

    def get_account_type_ou(self, account):
        """Return the OU based on the type."""
        if account.type == "saAccount":
            return "Admins"
        if account.type == "externalCollaborator":
            return "Collaborators"
        if account.type == "roleAccount":
            return "Role Accounts"
        if account.type == "sharedAccount":
            return "Shared Accounts"
        if account.type == "testAccount":
            return "Test Accounts"
        return None

    def get_person_dn(self, person):
        """Return the proper DN for a person."""
        # regular terminated users - suspended
        if person.terminated:
            ou = f"ou=Suspended,{self.ldap.base_dn}"

        # future hires starting beyond the "start" cutoff - suspended
        elif person.start_date > self.start:
            ou = f"ou=Future,{self.ldap.base_dn}"

        # all other people - active
        else:
            ou = f"ou=People,{self.ldap.base_dn}"

            # get trusted tester ou
            if person.trusted_tester and not person.terminated:
                ou = f"ou={person.trusted_tester},ou=Trusted Testers,{ou}"

            # otherwise, get workday ou
            else:
                ou = self.get_workday_orgunit(person, ou)

        # create dn
        dn = f"uid={person.username},{ou}"

        return str(dn)

    def get_person(self, person, supervisor_dn):
        """Return a person in the correct format."""
        # get username and email from person object
        username = str(person.username)

        # get email from person objects
        email = str(person.email)
        email_username = str(email.replace("@broadinstitute.org", ""))

        # get nicknames
        nicknames = []
        if person.nicknames:
            for nickname in person.nicknames:
                nicknames.append(str(nickname))  # noqa:PERF401

        # get primary and secondary domain from ldap object
        primary = self.ldap.domains.get("primary")
        secondary = self.ldap.domains.get("secondary")

        emails = []

        # set primary domian email
        if primary:
            primary = str(primary)

            # get email address based on broad email (may have alias override)
            email = f"{email_username}@{primary}"
            if email not in emails:
                emails.append(email)

            # get primary_email
            primary_email = f"{username}@{primary}"
            if primary_email not in emails:
                emails.append(primary_email)

            # get username/nickname emails for primary domain
            emails = self.get_person_domain_emails(username, nicknames, primary, emails)

        # add secondary domain email
        if secondary:
            secondary = str(secondary)

            # get username/nickname emails for primary domain
            emails = self.get_person_domain_emails(username, nicknames, secondary, emails)

        # convert object to ldap record
        ldap_person = person.to_google(supervisor_dn)

        # overwrite email
        ldap_person["description"] = [str(primary_email)]
        ldap_person["email"] = [str(email)]
        ldap_person["mail"] = emails

        return ldap_person

    def get_person_domain_emails(self, username, nicknames, domain, emails=None):
        """Return the list of domain emails for the user."""
        if emails is None:
            emails = []
        domain = str(domain)
        username = str(username)

        # get username email
        username_email = f"{username}@{domain}"
        if username_email not in emails:
            emails.append(username_email)

        # get nickname emails
        for nickname_orig in nicknames:
            nickname = str(nickname_orig)
            nickname_email = f"{nickname}@{domain}"
            if nickname_email not in emails:
                emails.append(nickname_email)

        return emails

    def get_workday_orgunit(self, person, ou):
        """Get the orgunit for a workday person."""
        # number of org levels to include
        depth = 2
        for org_orig in person.organization[:depth]:
            org = org_orig.replace(",", "")
            ou = f"ou={org},{ou}"
        return ou

    #
    # Assemled all records into a dict of new entries
    #
    def prepare_entries(self, ldap):
        """Prepare LDAP entries."""
        self.ldap = ldap
        self.prepare_entries_from_people()
        self.prepare_entries_from_accounts()
        self.prepare_entries_from_contacts()

    def prepare_entries_from_accounts(self):
        """Prepare entries from accounts."""
        if self.verbose:
            print("  Preparing accounts for Google LDAP...")
        self.accounts = self.prepare_accounts()
        if self.verbose:
            print(f"  Prepared {len(self.accounts)} accounts for Google LDAP.")
        # add contacts
        for dn in self.accounts:
            self.new_entries[dn] = self.accounts[dn]

    def prepare_entries_from_contacts(self):
        """Prepare entries from contacts."""
        if self.verbose:
            print("  Preparing contacts for Google LDAP...")
        self.contacts = self.prepare_contacts()
        if self.verbose:
            print(f"  Prepared {len(self.contacts)} contacts for Google LDAP.")
        # add contacts
        for dn in self.contacts:
            self.new_entries[dn] = self.contacts[dn]

    def prepare_entries_from_people(self):
        """Prepare entries from people."""
        if self.verbose:
            print("  Preparing people for Google LDAP...")
        self.new_entries = self.prepare_people()
        if self.verbose:
            print(f"  Prepared {len(self.new_entries)} people for Google LDAP.")

    def prepare_entries_from_resources(self):
        """Prepare entries from resources."""
        if self.verbose:
            print("  Preparing resources for Google LDAP...")
        self.resources = self.prepare_resources()
        if self.verbose:
            print(f"  Prepared {len(self.resources)} resources for Google LDAP.")
        # add resources
        for dn in self.resources:
            self.new_entries[dn] = self.resources[dn]

    #
    # Prepare actual resources for LDAP
    #
    def prepare_accounts(self):
        """Prepare other accounts from bitsdb."""
        accounts = {}
        for account in self.update.accounts_records:
            # get dn
            dn = self.get_account_dn(account)

            # get emails
            emails = []

            # get primary email
            primary = self.ldap.domains.get("primary")
            primary_info = account.domains.get(primary, {})
            email = primary_info.get("username")
            if email:
                emails.append(str(email))
            else:
                # skip users that have no email
                continue

            # check for sub domains
            subdomain = False
            if f".{primary}" in email:
                subdomain = True

            # check for users with primary email in secondary domain
            secondary_user = False
            if primary not in email:
                secondary_user = True

            # get secondary email
            secondary = self.ldap.domains.get("secondary")
            if email and secondary and not secondary_user and not subdomain:
                # create secondary email by replacing primary domain with secondary
                secondary_email = email.replace(primary, secondary)
                if secondary_email:
                    emails.append(str(secondary_email))

            # create record
            record = {
                "cn": [account.displayName],
                "carLicense": [account.gsuite_license],
                "description": [email],
                "givenName": [account.first_name],
                "co": ["Broad Institute of MIT and Harvard"],
                "mail": emails,
                "o": ["Broad Institute"],
                "objectClass": [
                    "top",
                    "inetOrgPerson",
                    "extensibleObject",
                ],
                "sn": [account.last_name],
            }

            # only add if the account has emails for this domain
            if email and emails:
                accounts[dn] = record

        return accounts

    def prepare_contacts(self):
        """Prepare contact records for Google LDAP."""
        contacts = {}
        for oid in self.update.shared_contacts:
            contact = self.update.shared_contacts[oid]

            # set cn and dn
            cn = str("{} {}".format(contact["first_name"], contact["last_name"]))
            ou = str(f"ou=Contacts,ou=Shared Contacts,{self.ldap.base_dn}")
            dn = str(f"cn={cn},{ou}")

            # create record
            record = {
                "cn": [cn],
                "description": [str(contact["email"])],
                "email": [str(contact["email"])],
                "givenName": [str(contact["first_name"])],
                "mail": [str(contact["email"])],
                "o": [str(contact["org"])],
                "objectClass": [
                    "top",
                    "inetOrgPerson",
                    "extensibleObject",
                ],
                "sn": [str(contact["last_name"])],
            }

            # telephone
            if contact.get("phone"):
                record["telephoneNumber"] = [str(contact["phone"])]

            # add contact to dictionar
            contacts[dn] = record

        return contacts

    def prepare_people(self):
        """Prepare people records for Google LDAP."""
        # get dates
        date_today = date.today()  # noqa:DTZ011
        start_date = date_today + timedelta(days=14)
        end_date = date_today - timedelta(days=90)

        # get date strings
        self.start = start_date.strftime("%Y-%m-%d")
        self.end = end_date.strftime("%Y-%m-%d")

        people = {}
        for pid in self.update.people_records:
            # get person object
            person = self.update.people_records[pid]

            # skip people are are past 90 days termination
            if person.end_date and person.end_date <= self.end:
                continue

            # for broadinstitute.us domains, skip employees
            primary_domain = self.ldap.domains.get("primary")
            if primary_domain and re.search("broadinstitute.us$", primary_domain) and person.type in ["Core Member", "Employee"]:
                    continue

            dn = self.get_person_dn(person)
            # get supervisor object
            supervisor_dn = None
            if person.supervisor_id:
                supervisor = self.update.people_records[person.supervisor_id]
                supervisor_dn = self.get_person_dn(supervisor)
            # get person in ldap format
            people[dn] = self.get_person(person, supervisor_dn)
        return people

    def prepare_resources(self):
        """Prepare calendar resources for Google LDAP."""
        resources = {}
        ou = f"ou=Resources,ou=Shared Contacts,{self.ldap.base_dn}"

        # create resource records
        for resource in self.update.resources:
            # only include conference rooms

            if "resourceType" not in resource:
                print(f"ERROR: No Resource Type: {resource}")
                continue

            if not re.search("Conference Room", resource["resourceType"]):
                continue

            # get dn
            dn = "cn={},{}".format(resource["resourceName"], ou)

            # get name
            name = str(resource["resourceName"].split(" (")[0].strip())

            # create record
            record = {
                "cn": [str(resource["resourceName"])],
                "description": [str(resource["resourceDescription"])],
                "email": [str(resource["resourceEmail"])],
                "employeeNumber": [str(resource["resourceId"])],
                "givenName": [name],
                "objectClass": [
                    "top",
                    "inetOrgPerson",
                    "extensibleObject",
                ],
                "sn": [str(resource["resourceType"])],
            }

            # save record
            resources[dn] = record

        return resources
