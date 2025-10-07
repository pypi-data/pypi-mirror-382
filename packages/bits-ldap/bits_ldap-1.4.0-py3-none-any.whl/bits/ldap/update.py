"""LDAP Update class file."""

from bits.ldap import LDAP

# object types
from bits.ldap.account import Account
from bits.ldap.forwarder import Forwarder

# ldap server types
from bits.ldap.gnarwl import Gnarwl
from bits.ldap.google import Google
from bits.ldap.person import Person
from bits.ldap.servicenow import ServiceNow


class LDAPUpdate:
    """LDAPUpdate class."""

    enterprise_group = "enterprise-gsuite-licenses@broadinstitute.org"

    def __init__(self, auth, settings):
        """Initialize a class instance."""
        self.auth = auth
        self.settings = settings
        self.verbose = auth.verbose

        # ldap server configs
        self.ldap_servers = settings.get("ldap_servers")

        self.other_accounts = {}

    def assemble_records(self, servers):  # noqa: ARG002
        """Assemble data into objects."""
        if self.verbose:
            print("Assembling data for LDAP update...")

        # assemble people data
        people_types = {"ad", "google", "servicenow"}
        if self.types.intersection(people_types):
            self.assemble_people_records()

        # assemble account data
        if "google" in self.types:
            self.assemble_account_records()

        # assemble gnarwl data
        if "gnarwl" in self.types:
            self.assemble_gnarwl_records()

    def assemble_account_records(self):
        """Assemble people data."""
        if self.verbose:
            print("  Assembling Account data...")

        accounts = [Account(self, x) for x in self.other_accounts]
        if self.verbose:
            print(f"    Created {len(accounts)} Account objects.")

        self.accounts_records = accounts

    def assemble_gnarwl_records(self):
        """Assemble gnarwl data."""
        if self.verbose:
            print("  Assembling Gnarwl data...")

        forwarders = [Forwarder(self, {"username": "nagios"})]

        for username in self.gnarwl:

            # add the user as a forwarder
            record = self.gnarwl[username]
            forwarders.append(Forwarder(self, record))

            # also add nicknames as forwarders
            if username in self.nicknames:
                nicknames = self.nicknames[username]["nicknames"]
                for nickname in nicknames:
                    record["username"] = nickname
                    forwarders.append(Forwarder(self, record))

        if self.verbose:
            print(f"    Created {len(forwarders)} Gnarwl objects.")

        self.gnarwl_records = forwarders

    def assemble_people_records(self):
        """Assemble people data."""
        if self.verbose:
            print("  Assembling People data...")

        people = {}

        for pid in self.people:
            people[pid] = Person(self, self.people[pid])

        if self.verbose:
            print(f"    Created {len(people)} Person objects.")

        self.people_records = people

    def get_data(self, servers):
        """Get data needed for the LDAP update."""
        if self.verbose:
            print("Getting data for LDAP update...")

        # determine which server types are being updated
        # Types: ad, gnarwl, google, localmail, servicenow
        self.types = self.get_server_types(servers)
        if self.verbose:
            print("  Types: {}".format(", ".join(sorted(self.types))))

        # get people data
        people_types = {"gnarwl", "google", "servicenow"}
        if self.types.intersection(people_types):
            self.get_people()
            self.get_nicknames()

        # additional data
        other_types = {"ad", "google", "servicenow"}
        if self.types.intersection(other_types):
            self.get_ad_users()
            self.get_enterprise_users()
            self.get_google_people()
            self.get_google_users()
            self.get_other_accounts()
            self.get_phones()
            self.get_resources()
            self.get_shared_contacts()
            self.get_trusted_testers()

        # get gnarwl data
        if "gnarwl" in self.types:
            self.get_gnarwl()

    def get_ad_users(self):
        """Get AD users data."""
        ad = self.auth.ad()
        attrlist = [
            "gidNumber",
            "homeDirectory",
            "loginShell",
            "sAMAccountName",
            "uidNumber",
            "unixHomeDirectory",
        ]
        if self.verbose:
            print("  Getting users from AD...")
        ad_users = ad.getUsers(attrlist=attrlist, full=False)
        if self.verbose:
            print(f"    Found {len(ad_users)} AD users.")
        self.ad_users = ad_users

    def get_enterprise_users(self):
        """Get users with gsuite enterprise license override."""
        g = self.auth.google()
        g.auth_service_account(g.scopes, g.subject)
        if self.verbose:
            print("  Getting G Suite Enterprise users from Google Groups...")
        enterprise = {}
        for member in g.directory().get_derived_members(
            self.enterprise_group,
        ):
            uid = member["id"]
            enterprise[uid] = member
        if self.verbose:
            print(f"    Found {len(enterprise)} Enterprise users.")
        self.enterprise_users = enterprise

    def get_gnarwl(self):
        """Get gnarwl forwarders."""
        m = self.auth.mongo()
        self.gnarwl = m.get_collection_dict("gnarwl")

    def get_google_people(self):
        """Get google people."""
        m = self.auth.mongo()
        self.google_people = m.get_collection_dict("google_people")

    def get_google_users(self):
        """Get google users."""
        g = self.auth.google()
        g.auth_service_account(g.scopes, g.subject)
        user_fields = [
            "id",
            "primaryEmail",
        ]
        fields = "nextPageToken,users({})".format(",".join(user_fields))
        if self.verbose:
            print("  Getting users from Google.")
        google_users = g.directory().get_users_dict(fields=fields, key="primaryEmail")
        if self.verbose:
            print(f"    Found {len(google_users)} Google users")
        self.google_users = google_users

    def get_nicknames(self):
        """Get nicknames."""
        m = self.auth.mongo()
        self.nicknames = m.get_collection_dict("nicknames")
        # also add nicknames to usernames
        for username in self.nicknames:
            if username not in self.usernames:
                continue
            person = self.usernames[username]
            nicknames = self.nicknames[username].get("nicknames", [])
            for nickname in nicknames:
                if nickname in self.usernames:
                    print(f"ERROR: Duplicate username: {nickname}")
                    continue
                self.usernames[nickname] = person

    def get_other_accounts(self):
        """Get other_accounts."""
        m = self.auth.mongo()
        other_accounts = m.get_collection_dict("other_accounts")

        accounts = []
        for oid in other_accounts:
            account = other_accounts[oid]

            # get google usernames from record
            google_username = account.get("google_username")
            google_test_username = account.get("google_test_username")
            google_us_username = account.get("google_us_username")
            google_us_test_username = account.get("google_us_test_username")

            # skip records with no google username
            if (
                not google_username
                and not google_test_username
                and not google_us_username
                and not google_us_test_username
            ):
                continue

            accounts.append(account)
        self.other_accounts = accounts

    def get_people(self):
        """Get people data."""
        g = self.auth.google()
        project = "broad-gaia-prod"
        firestore = g.firestore(project)
        if self.verbose:
            print("  Getting People from Firestore...")
        people = {}
        usernames = {}

        for person in firestore.get_collection("gaia_people"):
            emplid = person["emplid"]
            username = person["username"]
            if emplid and emplid not in people:
                people[emplid] = person
            elif emplid:
                print(f"WARNING: Duplicate or empty EMPLID: {emplid}")
            if username and username not in people:
                usernames[username] = person
            elif username:
                print(f"WARNING: Duplicate or empty Username: {username}")
        if self.verbose:
            print(f"    Found {len(people)} people.")
        self.people = people
        self.usernames = usernames

    def get_phones(self):
        """Get phone data."""
        p = self.auth.people()
        if self.verbose:
            print("  Getting phones from People...")
        phones = p.getTelephones()
        if self.verbose:
            print(f"    Found {len(phones)} phones.")
        self.phones = phones

    def get_resources(self):
        """Get calendar resources from Google."""
        g = self.auth.google()
        g.auth_service_account(g.scopes, g.subject)
        if self.verbose:
            print("  Getting resouces from Google...")
        resources = g.directory().get_resource_calendars()
        if self.verbose:
            print(f"    Found {len(resources)} resources.")
        self.resources = resources

    def get_server_types(self, servers):
        """Return a set of types from the servers list."""
        types = []
        for server in servers:
            config = self.ldap_servers[server]
            server_type = config["type"]
            types.append(server_type)
        return set(types)

    def get_shared_contacts(self):
        """Prepare shared contacts data."""
        m = self.auth.mongo()
        self.shared_contacts = m.get_collection_dict("google_shared_contacts")

    def get_trusted_testers(self):
        """Get trusted testers."""
        m = self.auth.mongo()
        self.trusted_testers = m.get_collection_dict("trusted_testers")

    def prepare_entries(self, server_type, ldap):
        """Prepare entries for an LDAP server update."""
        # get update class for Gnarwl records
        if server_type == "gnarwl":
            update = Gnarwl(self)

        # get update class for Google records
        if server_type == "google":
            update = Google(self)

        # get update class for ServiceNow servers
        elif server_type == "servicenow":
            update = ServiceNow(self)

        # prepare entries for this class
        update.prepare_entries(ldap)

        # return the update class that will be used for this server
        return update

    def update(self, servers):
        """Update a list of LDAP servers."""
        # retrieve raw data from sources
        self.get_data(servers)

        # assemble raw data into objects
        self.assemble_records(servers)

        # update ldap servers
        self.update_servers(servers)

    def update_all(self):
        """Update all LDAP servers."""
        self.update(self.ldap_servers)

    def update_server(self, server):
        """Update a single LDAP server."""
        # get ldap config for this server
        config = self.ldap_servers[server]

        # get server type
        server_type = config.get("type")

        # skip unsupported server types
        if server_type not in ["gnarwl", "google", "servicenow"]:
            return

        print(f"Server: {server}")

        # connect to ldap server
        ldap = LDAP(
            base_dn=config.get("base_dn"),
            bind_dn=config.get("bind_dn"),
            bind_pw=config.get("bind_pw"),
            bitsdb_key=config.get("bitsdb_key"),
            domains=config.get("domains"),
            server_type=config.get("type"),
            uri=config.get("uri"),
            verbose=self.verbose,
        )

        # prepare entries for this specific server
        update = self.prepare_entries(server_type, ldap)

        # skip servers with no update class
        if not update.new_entries:
            if self.verbose:
                print("  No new entries to compare. Skipping.\n")
            return

        # peform updates for this server
        update.perform_updates(server)

    def update_servers(self, servers):
        """Update the listed servers."""
        # update each server
        for server in sorted(servers):
            self.update_server(server)
