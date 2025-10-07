"""LDAP Update class for Active Directory."""
import datetime
import logging
import re
import time

import pytz

from bits.ldap import LDAP

LOGGER = logging.getLogger(__name__)


class AD(LDAP):
    """AD LDAP Update class."""

    def __init__(  # noqa: PLR0913
            self,
            uri,
            bind_dn,
            bind_pw,
            base_dn,
            server_type=None,
            domains=None,
            bitsdb_key=None,
            verbose=None):
        """Initialize a class instance."""
        LDAP.__init__(self, uri, bind_dn, bind_pw, base_dn, server_type, domains, bitsdb_key, verbose)

        self.group_attributes = [
            "cn",
            "dSCorePropagationData",
            "description",
            "distinguishedName",
            "gidNumber",
            "groupType",
            "info",
            "instanceType",
            "managedBy",
            # member => range=0-1499
            "member",
            "name",
            "objectCategory",
            "objectClass",
            "sAMAccountName",
            "sAMAccountType",
            "uSNChanged",
            "uSNCreated",
            "whenChanged",
            "whenCreated",
        ]

        self.user_attributes = [
            "accountExpires",
            # 'adminCount',
            # 'badPasswordTime',
            # 'badPwdCount',
            "cn",
            "co",
            # 'codePage',
            "company",
            # 'countryCode',
            # 'dSCorePropagationData',
            "department",
            "departmentNumber",
            "description",
            "directReports",
            "displayName",
            "distinguishedName",
            "division",
            "employeeNumber",
            "employeeType",
            "extensionAttribute11",
            "gidNumber",
            "givenName",
            "homeDirectory",
            "homeDrive",
            "info",
            "initials",
            # 'instanceType',
            # 'lastLogoff',
            # 'lastLogon',
            # 'lastLogonTimestamp',
            "l",
            # 'lockoutTime',
            "loginShell",
            # 'logonCount',
            # 'logonHours',
            "mail",
            "managedObjects",
            "manager",
            "maxPwdAge",
            "member",
            "memberOf",
            "msRADIUSCallbackNumber",
            "msRADIUSFramedIPAddress",
            "msRADIUSServiceType",
            # 'msTSExpireDate',
            # 'msTSLicenseVersion',
            # 'msTSLicenseVersion2',
            # 'msTSLicenseVersion3',
            # 'msTSManagingLS',
            "name",
            "o",
            "objectCategory",
            # 'objectClass',
            # 'objectGUID',
            # 'objectSid',
            "personalPager",
            "postalCode",
            "primaryGroupID",
            "profilePath",
            "pwdLastSet",
            "sAMAccountName",
            "sAMAccountType",
            # 'scriptPath'
            "sn",
            "st",
            "streetAddress",
            "telephoneNumber",
            # 'terminalServer'
            "title",
            # 'uSNChanged',
            # 'uSNCreated',
            "uid",
            "uidNumber",
            "unixHomeDirectory",
            "userAccountControl",
            # 'userCertificate',
            "userPrincipalName",
            "whenChanged",
            "whenCreated",
        ]

        self.groups = {}
        self.google_users = {}
        self.users = {}
        self.users_by_dn = {}
        self.verbose = False
        if verbose:
            self.verbose = verbose

    #
    # Helpers
    #
    def get_expire_date(self, last, maxDays=None):  # noqa: N803
        """Convert pwd last set date to a datetime."""
        if not last:
            return datetime.datetime(year=1970, month=1, day=1)  # noqa: DTZ001
        max_days = maxDays
        if not max_days:
            max_days = 90
        epoch = datetime.datetime(year=1601, month=1, day=1)  # noqa: DTZ001
        last_set = datetime.timedelta(seconds=last/10**7)
        max_age = datetime.timedelta(days=max_days)
        return epoch + last_set + max_age

    def get_pwd_last_set_date(self, last):
        """Convert pwd last set date to an expiration date."""
        epoch = datetime.datetime(year=1601, month=1, day=1)  # noqa: DTZ001
        pwdlastset = datetime.timedelta(seconds=last/10**7)
        return epoch + pwdlastset

    #
    # Groups
    #
    def check_group(self, groupname):
        """Check if an Active Directory group exists."""
        try:
            if self.get_group(groupname):
                return True
        except Exception:  # noqa: BLE001
            return False

    def get_group(self, groupname, bytes_mode=True):  # noqa:FBT002
        """Return a single group."""
        filterstr = f"(sAMAccountName={groupname})"

        # bytes mode
        if bytes_mode:
            entries = self.get_entries(filterstr, self.group_attributes)
            for dn in entries:
                return entries[dn]

        # unicode strings mode
        entries = self.get_entries(filterstr, self.group_attributes)
        for dn in entries:
            return self.convert_entry_to_strings(entries[dn])
        return None

    def get_groups(self, attrlist=None, bytes_mode=True, key="sAMAccountName"):  # noqa:FBT002
        """Return a dict of groups by groupname."""
        entries = self.get_groups_by_dn(attrlist=attrlist, bytes_mode=bytes_mode)
        groups = {}
        for dn in entries:
            e = entries[dn]
            k = e[key][0]
            if isinstance(k, bytes):
                k = k.decode("utf-8")
            groups[k] = e
        return groups

    def get_groups_by_dn(self, attrlist=None, bytes_mode=True):  # noqa:FBT002
        """Return a dict of groups from Active Directory."""
        filterstr = "(&(objectCategory=group)(sAMAccountName=*))"

        if not attrlist:
            attrlist = self.user_attributes

        # bytes mode
        if bytes_mode:
            return self.get_entries(filterstr, self.user_attributes)

        # unicode strings mode
        entries = self.get_entries(filterstr, self.user_attributes)
        groups = {}
        for dn in entries:
            groups[dn] = self.convert_entry_to_strings(entries[dn])
        return groups

    def get_groups_by_gid(self, bytes_mode=True):  # noqa:FBT002
        """Return a dict of groups by gid."""
        groups = self.get_groups(bytes_mode=bytes_mode)
        gid_groups = {}
        for groupname in groups:
            g = groups[groupname]
            if "gidNumber" in g and g["gidNumber"] and int(g["gidNumber"][0]) >= 0:
                gid = int(g["gidNumber"][0])
                if gid in gid_groups:
                    gid_groups[gid] = [groupname]
                else:
                    gid_groups[gid] = [groupname]
        return gid_groups

    def get_groups_by_username(self, bytes_mode=True):  # noqa:FBT002,ARG002
        """Return a dict of groups by username."""
        groups = self.get_groups_for_nis()
        user_groups = {}
        for groupname in groups:
            g = groups[groupname]
            members = g["users"]
            for m in members:
                if not m:
                    continue
                if m not in user_groups:
                    user_groups[m] = []
                user_groups[m].append(groupname)

        return user_groups

    def get_groups_for_nis(self, bytes_mode=True, people=None):  # noqa:FBT002,ARG002
        """Return a dict of groups for NIS."""
        groups = self.get_groups(bytes_mode=False)
        users = self.get_users_by_dn(bytes_mode=False)

        nis_groups = {}
        notfound = []
        for groupname in groups:
            g = groups[groupname]

            # only get groups that have a gid
            if "gidNumber" not in g or int(g["gidNumber"][0]) < 0:
                continue

            gid = int(g["gidNumber"][0])

            members = []

            # see if the group has members:
            if "member" in g:

                # cycle through the members
                for m in g["member"]:

                    # skip users without a dn
                    if not m:
                        continue

                    # check if user exists in AD
                    if m in users:
                        u = users[m]

                        # set the username
                        username = u["sAMAccountName"][0].lower()

                        if people and username in people and people[username]["terminated"]:
                            continue

                        # add the username to the list of members
                        members.append(username)

                    else:
                        print(f"ERROR: AD user not found!: {m} ({groupname})")
                        notfound.append(m)

            data = {
                "name": groupname,
                "gid": gid,
                "password": "*",
                "users": members,
            }

            nis_groups[groupname] = data

        return nis_groups

    def update_groups(self, auth):
        """Update groups in Active Directory."""
        b = auth.bitsdbapi()
        ad_group_syncs = b.get_ad_group_syncs()

        g = auth.google()
        g.auth_service_account(g.scopes, g.subject)

        if auth.verbose:
            print("Getting Google Users...")
        self.google_users = g.directory().get_users_dict()

        default_users = {
            # "engineering": [
            #     "devopsci",
            #     "itweb",
            #     "rpmbuild",
            #     "svcnow",
            # ],
        }

        if auth.verbose:
            print("Getting AD Users...")
        self.get_users(bytes_mode=False)

        print("Updating AD group members from Google Groups...")
        for sync in ad_group_syncs:
            ad_group_name = sync["ad_group_name"]
            google_group_email = sync["google_group_email"]
            if auth.verbose:
                print(f'\nUpdating AD group "{ad_group_name}" from {google_group_email}...')

            members = default_users.get(ad_group_name, [])
            members.extend(self.get_google_group_members(google_group_email, auth))
            self.update_group_members(ad_group_name, members)

    #
    # Members
    #
    def add_group_member(self, groupname, username):
        """Add a user to an Active Directory group."""
        group = self.get_group(groupname, bytes_mode=False)
        if not group:
            print(f"ERROR: No such group: {groupname}")
            return None

        user = self.get_user(username, bytes_mode=False)
        if not user:
            print(f"ERROR: No such user: {username}")
            return None

        # get dns
        group_dn = group["distinguishedName"][0]
        user_dn = user["distinguishedName"][0]

        # check if group has any members
        if "member" not in group:
            group["member"] = []

        # check if user is already in group
        if user_dn in group["member"]:
            return True

        modlist = [(self.ldapmodule.MOD_ADD, "member", user_dn.encode("utf-8"))]
        return self.ldapobject.modify_s(group_dn, modlist)

    def get_google_group_members(self, groupname, auth):
        """Return the members from a Google Group for syncing with AD."""
        g = auth.google()
        g.auth_service_account(g.scopes, g.subject)

        # add domain name
        group_email = groupname
        if "@" not in groupname:
            group_email = f"{groupname}@broadinstitute.org"

        # get members
        members = g.directory().get_derived_members(group_email)

        # create users list
        users = []
        for m in members:
            email = m["email"]
            uid = m["id"]

            if uid in self.google_users:
                email = self.google_users[uid]["primaryEmail"]

            username = email.replace("@broadinstitute.org", "")
            users.append(username)

        return sorted(set(users))

    def remove_group_member(self, groupname, username):
        """Remove a user from an Active Directory group."""
        group = self.get_group(groupname, bytes_mode=False)
        if not group:
            print(f"ERROR: No such group: {groupname}")
            return None

        user = self.get_user(username, bytes_mode=False)
        if not user:
            print(f"ERROR: No such user: {username}")
            return None

        # get dns
        group_dn = group["distinguishedName"][0]
        user_dn = user["distinguishedName"][0]

        # check if group has any members
        if "member" not in group:
            group["member"] = []

        # check if user is already in group
        if user_dn not in group["member"]:
            return True

        modlist = [(self.ldapmodule.MOD_DELETE, "member", user_dn.encode("utf-8"))]
        return self.ldapobject.modify_s(group_dn, modlist)

    def update_group_members(self, groupname, groupusers):  # noqa:C901,PLR0912
        """Update the members of an Active Directory groups."""
        group = self.get_group(groupname, bytes_mode=False)
        if not group:
            LOGGER.error(f"AD Group not found: {groupname}")
            return
        members = group.get("member", [])

        # find members to add
        add = []
        for username in sorted(groupusers):
            if username not in self.users:
                if self.verbose:
                    print(f"WARNING: AD username not found [{groupname}]: {username}")
                continue

            user = self.users[username]
            dn = user["distinguishedName"][0]
            if dn not in members:
                add.append(username)

        # find members to remove
        remove = []
        for dn in sorted(members):
            if dn not in self.users_by_dn:
                print(f"ERROR: AD user DN not found [{groupname}]: {dn}")
                continue

            user = self.users_by_dn[dn]
            username = user["sAMAccountName"][0]
            if username not in groupusers:
                remove.append(username)

        if add or remove:
            print(f"Updating AD group: {groupname}")

        # add users
        if add:
            print("  Adding users:")
            for username in sorted(add):
                print(f"   + {username}")
                self.add_group_member(groupname, username)

        # remove users
        if remove:
            print("  Removing users:")
            for username in sorted(remove):
                print(f"   - {username}")
                self.remove_group_member(groupname, username)

    #
    # OUs
    #
    def get_ous(self, bytes_mode=True):  # noqa:FBT002
        """Return a dict of ous from Active Directory."""
        attrlist = ["ou"]
        filterstr = "(ou=*)"

        # bytes mode
        if bytes_mode:
            return self.get_entries(filterstr, attrlist)

        # unicode strings mode
        entries = self.get_entries(filterstr, attrlist)
        ous = {}
        for dn in entries:
            ous[dn] = self.convert_entry_to_strings(entries[dn])
        return ous

    #
    # Users
    #
    def check_user(self, username):
        """Check if an Active Directory user exists."""
        try:
            if self.get_user(username):
                return True
        except Exception:  # noqa:BLE001
            return False

    def create_user(self, username):
        """Create a user in Active Directory."""
        """TODO"""

    def delete_user(self, username):
        """Delete a user in Active Directory."""
        user = self.get_user(username, bytes_mode=False)
        if not user:
            print(f"ERROR: No such user: {username}")
            return None

        # get dn
        dn = user["distinguishedName"][0]

        # delete user
        self.delete_entry(dn)

        return user

    def get_user(self, username, bytes_mode=True):  # noqa:FBT002
        """Return a single user."""
        filterstr = f"(sAMAccountName={username})"

        # bytes mode
        if bytes_mode:
            entries = self.get_entries(filterstr, self.user_attributes)
            for dn in entries:
                return entries[dn]

        # unicode strings mode
        entries = self.get_entries(filterstr, self.user_attributes)
        for dn in entries:
            return self.convert_entry_to_strings(entries[dn])
        return None

    def get_users(self, attrlist=None, bytes_mode=True, key="sAMAccountName"):  # noqa:FBT002
        """Return a dict of users by username."""
        entries = self.get_users_by_dn(attrlist=attrlist, bytes_mode=bytes_mode)
        users = {}
        for dn in entries:
            e = entries[dn]
            k = e[key][0]
            if isinstance(k, bytes):
                k = k.decode("utf-8")
            users[k] = e
        self.users = users
        return users

    def get_users_by_dn(self, attrlist=None, bytes_mode=True):  # noqa:FBT002
        """Return a dict of users from Active Directory."""
        filterstr = "(&(objectCategory=person)(sAMAccountName=*))"

        if not attrlist:
            attrlist = self.user_attributes

        # bytes mode
        if bytes_mode:
            return self.get_entries(filterstr, attrlist)

        # unicode strings mode
        entries = self.get_entries(filterstr, attrlist)
        users = {}
        for dn in entries:
            users[dn] = self.convert_entry_to_strings(entries[dn])
        self.users_by_dn = users
        return users

    def get_users_for_nis(self):
        """Return a dict of users for NIS."""
        users = self.get_users(bytes_mode=False)
        nis_users = {}
        for username in sorted(users):
            if not username:
                continue

            u = users[username]

            if not u:
                print(f"ERROR: AD user not found: {username}")
                continue

            if "uidNumber" not in u or int(u["uidNumber"][0]) < 0:
                continue

            if "gidNumber" not in u or int(u["gidNumber"][0]) < 0:
                continue

            if "loginShell" not in u or not str(u["loginShell"][0]):
                continue

            if "unixHomeDirectory" not in u or not str(u["unixHomeDirectory"][0]):
                continue

            if "displayName" not in u or not str(u["displayName"][0]):
                continue

            uid = int(u["uidNumber"][0])
            gid = int(u["gidNumber"][0])
            home_dir = u["unixHomeDirectory"][0]
            shell = u["loginShell"][0]
            gecos = u["displayName"][0]

            user = {
                "username": username,
                "uid": uid,
                "gid": gid,
                "gecos": gecos,
                "password": "*",
                "shell": shell,
                "home_dir": home_dir,
            }

            nis_users[username] = user

        return nis_users

    def lock_user(self, username):
        """Lock a user in Active Directory."""
        user = self.get_user(username, bytes_mode=False)
        if not user:
            print(f"ERROR: No such user: {username}")
            return None

        dn = user["distinguishedName"][0]

        # lock account
        locked = False
        if user["userAccountControl"][0] != "514":
            modlist = [(self.ldapmodule.MOD_REPLACE, "userAccountControl", b"514")]
            try:
                self.ldapobject.modify_s(dn, modlist)
                locked = True
            except Exception as e:  # noqa:BLE001
                print(type(e))
                print(e)
                print(f"ERROR: Failed to unlock AD user: {username}")

        # move user
        moved = False
        if not re.search("Disabled Accounts", dn):
            self.move_user(username, "OU=Disabled Accounts,DC=broad,DC=mit,DC=edu")
            moved = True

        if locked or moved:
            return True
        return None

    def move_user(self, username, newParent):  # noqa:N803
        """Move a user in Active Directory."""
        user = self.get_user(username, bytes_mode=False)
        if not user:
            print(f"ERROR: No such user: {username}")
            return None

        dn = user["distinguishedName"][0]
        rdn = "CN={}".format(user["cn"][0])
        return self.ldapobject.rename_s(dn, rdn, newParent)

    def prepare_user(self):
        """Prepare a single user for in Active Directory."""
        """TODO"""

    def rename_user(self, username, newrdn):
        """Rename a user in Active Directory."""
        user = self.get_user(username, bytes_mode=False)
        if not user:
            print(f"ERROR: No such user: {username}")
            return None

        dn = user["distinguishedName"][0]
        return self.ldapobject.rename_s(dn, newrdn)

    def set_password(self, username, password):
        """Set a user's password in Active Directory."""
        user = self.get_user(username, bytes_mode=False)
        if not user:
            print(f"ERROR: No such user: {username}")
            return None

        dn = user["distinguishedName"][0]
        ad_password = f'"{password}"'.encode("utf-16-le")
        modlist = [(self.ldapmodule.MOD_REPLACE, "unicodePwd", [ad_password])]
        return self.ldapobject.modify_s(dn, modlist)

    def unlock_user(self, username):
        """Unlock a user in Active Directory."""
        user = self.get_user(username, bytes_mode=False)
        if not user:
            print(f"ERROR: No such user: {username}")
            return None

        dn = user["distinguishedName"][0]

        # check if account needs to be unlocked
        unlocked = False
        if user["userAccountControl"][0] != "512":
            modlist = [
                (self.ldapmodule.MOD_REPLACE, "userAccountControl", b"512"),
                (self.ldapmodule.MOD_REPLACE, "loginShell", b"/bin/bash")
            ]
            try:
                self.ldapobject.modify_s(dn, modlist)
                unlocked = True
            except Exception as e:  # noqa:BLE001
                print(type(e))
                print(e)
                print(f"ERROR: Failed to unlock AD user: {username}")

        # check if account needs to be moved
        moved = False
        if not re.search("UserOU", dn):
            try:
                self.move_user(username, "OU=UserOU,DC=broad,DC=mit,DC=edu")
                moved = True
            except Exception as e:  # noqa:BLE001
                print(type(e))
                print(e)
                print(f"ERROR: Failed to move AD user: {username}")

        if unlocked or moved:
            return True
        return None

    # def update_user(self):
    #     """Update a single user in Active Directory."""
    #     """TODO"""

    # def update_users(self):
    #     """Update users in Active Directory."""
    #     """TODO"""

    #
    # Update Users
    #
    def compare_user(self, old, new):
        """Compare a single user for update."""
        exclude = [
            "distinguishedName",
            "directReports",
            "homeDrive",
            "info",
            "managedObjects",
            "memberOf",
            "msRADIUSCallbackNumber",
            "msRADIUSFramedIPAddress",
            "msRADIUSServiceType",
            # 'name',
            "pwdLastSet",
            "whenChanged",
            "whenCreated",
        ]

        # copy dicts
        new = dict(new)
        old = dict(old)

        # reverse organization for comparisions (FIFO)
        if old.get("o"):
            old["o"].reverse()

        output = []
        for key in set(list(old) + list(new)):
            if key in exclude:
                if key in old:
                    del old[key]
                if key in new:
                    del new[key]
                continue

            n = new.get(key, [None])
            o = old.get(key, [None])

            if n != o:
                output.append(f"{key}: {o} -> {n}")

        ldif = None
        if output:
            ldif = self.ldapmodule.modlist.modifyModlist(old, new)

        return ldif, output

    def get_person_dn(self, person):  # noqa:ARG002
        """Return the DN of a person."""
        return

    def prepare_person(self, p, u):  # noqa:C901,PLR0912,PLR0915
        """Prepare a single person for Active Directory."""
        company_max = 64
        username = p["username"]
        username_email = f"{username}@broadinstitute.org"
        terminated = p["terminated"]

        dn = self.get_person_dn(p)

        # set the date when accountExpires
        account_expires = "0"
        if p.get("end_date"):
            date_format = "%Y-%m-%d %H:%M:%S"
            end_date = p["end_date"]
            est = pytz.timezone("US/Eastern")
            # set expire time to 9am GMT 4am EST on day after termination date
            expire_string = f"{end_date} 05:00:00"
            expire_time = datetime.datetime.strptime(expire_string, date_format) + datetime.timedelta(days=1)  # noqa:DTZ007
            # handle daylight savings time
            expire_time -= est.localize(expire_time).dst()
            # convert to unix timestamp
            unix_expire = int(time.mktime(expire_time.timetuple()))
            # conver to AD timestamp
            account_expires = str((unix_expire + 11644473600) * 10000000)

        # set the address fields
        street_address = None
        city = None
        state = None
        postal_code = None
        country = None
        if p.get("address"):
            street_address = p["address"]["street"]
            city = p["address"]["city"]
            state = p["address"]["state"]
            postal_code = p["address"]["zip_code"]
            country = p["address"]["country"]

        # set the company
        company = p["home_institution_ascii"]
        if len(company) > company_max:
            company = company[0:company_max]

        # set the department:
        department = None
        if p.get("org_unit"):
            org_unit = p["org_unit"]
            org_unit = org_unit.replace("Administration > ", "Admin > ")
            org_unit = org_unit.replace("Research > ", "")
            org_unit = org_unit.replace("Specialized Service Facilities > ", "")

            department = org_unit.split(" > ")[-1]
            department = department.replace("&", "-").replace("/", "-")

        # set the department numb
        department_number = p["department_id"]

        # set the description
        description = p["worker_sub_type"]

        # set the division
        division = None
        if p.get("org_unit"):
            division = p["org_unit"]

        # set the initials
        initials = None

        # set the name
        first_name = p["first_name_ascii"]
        last_name = p["last_name_ascii"]
        full_name = p["full_name_ascii"]

        # set the email
        email = p["email"]

        # set the personal email
        email_home = p.get("email_home")

        # set the employee number
        employee_number = p["emplid"]

        # set the employee type
        employee_type = p["worker_type"]

        # set the homeDirectory and homeDrive
        home_directory = f"\\\\krypton\\{username}"
        home_drive = "I:"

        # set the manager
        manager = None
        if p.get("manager_dn"):
            manager = p["manager_dn"]

        # set the orgaization
        organization = [None]
        if p.get("department"):
            organization = p["department"][1:]

        # set objectCategory
        object_category = "CN=Person,CN=Schema,CN=Configuration,DC=broad,DC=mit,DC=edu"

        # set primaryGroupID
        primary_group_id = "513"

        # set samAccountType
        sam_account_type = "805306368"

        # set the telephoneNumber
        telephone_number = None
        if p.get("primary_work_phone"):
            telephone_number = p["primary_work_phone"]

        # set the title
        title = p["title"]

        # set userAccountControl and extensionAttribute11
        extension_attribute11 = "SciQuest"
        user_account_control = "512"
        if terminated:
            extension_attribute11 = None
            user_account_control = "514"

        # get nis account info
        login_shell = None
        if u and u.get("loginShell"):
            login_shell = u["loginShell"][0]
            if terminated:
                login_shell = "/bin/false"
            elif login_shell == "/bin/false":
                login_shell = "/bin/bash"
        elif not terminated:
            print(f"WARNING: No login shell for user: {username}")

        gid_number = None
        if u and u.get("gidNumber"):
            gid_number = u["gidNumber"][0]
        elif not terminated:
            print(f"WARNING: No gid number for user: {username}")

        uid_number = None
        if u and u.get("uidNumber"):
            uid_number = u["uidNumber"][0]
        elif not terminated:
            print(f"WARNING: No uid number for user: {username}")

        unix_home_directory = None
        if u and u.get("unixHomeDirectory"):
            unix_home_directory = f"/home/unix/{username}"
        elif not terminated:
            print(f"WARNING: No UNIX home directory for user: {username}")

        return {
            "accountExpires": [account_expires],
            "cn": [username],
            "co": [country],
            "company": [company],
            "department": [department],
            "departmentNumber": [department_number],
            "description": [description],
            "displayName": [full_name],
            "distinguishedName": [dn],
            "division": [division],
            "employeeNumber": [employee_number],
            "employeeType": [employee_type],
            "extensionAttribute11": [extension_attribute11],
            "gidNumber": [gid_number],
            "givenName": [first_name],
            "homeDirectory": [home_directory],
            "homeDrive": [home_drive],
            "initials": [initials],
            "l": [city],
            "loginShell": [login_shell],
            "mail": [email],
            "manager": [manager],
            "name": [username],
            "o": organization,
            "objectCategory": [object_category],
            "personalPager": [email_home],
            "postalCode": [postal_code],
            "primaryGroupID": [primary_group_id],
            "sAMAccountName": [username],
            "sAMAccountType": [sam_account_type],
            "sn": [last_name],
            "st": [state],
            "streetAddress": [street_address],
            "telephoneNumber": [telephone_number],
            "title": [title],
            "uid": [username],
            "uidNumber": [uid_number],
            "unixHomeDirectory": [unix_home_directory],
            "userAccountControl": [user_account_control],
            "userPrincipalName": [username_email],
        }

    def prepare_people(self, people, users):
        """Prepare people data for AD."""
        data = {}
        for emplid in people:
            p = people[emplid].to_dict()

            # get manager
            if p["manager_id"] and p["manager_id"] in people:
                manager_id = p["manager_id"]
                manager_username = people[manager_id].to_dict()["username"]
                if manager_username in users:
                    p["manager_dn"] = users[manager_username]["distinguishedName"][0]

            username = p["username"]
            u = users.get(username)
            entry = self.prepare_person(p, u)
            data[username] = entry
        return data

    def prepare_users(self, auth, users):
        """Prepare user data for AD."""
        g = auth.google()
        g.auth_service_account(g.scopes)

        project = "broad-bitsdb-firestore"
        collection = "people_people"

        firestore = g.firestore(project)
        print("Getting people from Firestore...")
        people = firestore.get_docs_dict(collection)
        print(f"Found {len(people)} people.")

        return self.prepare_people(people, users)


    def update_users(self, auth):
        """Update users in AD."""
        print("Getting Users from AD...")
        users = self.get_users()
        print(f"Found {len(users)} AD users.")

        data = self.prepare_users(auth, users)

        add = []
        delete = []
        update = {}

        # find users to update
        for username in sorted(users):
            if username in data:
                new = self.convert_entry(data[username])
                old = users[username]
                ldif, output = self.compare_user(old, new)
                if output:
                    dn = old["distinguishedName"][0].decode("utf-8")
                    print(f"\nUpdates for: {username} [{dn}]")
                    print("   * " + "\n   * ".join(output))
                    dn = old["distinguishedName"][0].decode("utf-8")
                    update[dn] = ldif

        print(f"Add: {len(add)}, Delete: {len(delete)}, Update: {len(update)}")

        # perform updates
        if update:
            print("\nPerforming updates...")
        for dn in sorted(update):
            ldif = update[dn]
            try:
                self.ldapobject.modify_s(dn, ldif)
            except Exception as e:  # noqa:BLE001
                print(f"\nERROR Updating: {dn}")
                print(e)
                print(ldif)
        if update:
            print("Done.")
