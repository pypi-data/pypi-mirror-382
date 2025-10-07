"""LDAP class file."""

import ldap as ldapmodule
from ldap import modlist


class LDAP:
    """LDAP class."""

    # default page size (for Active Directory servers)
    pagesize = 1000

    # Ignore errors related to self-signed certificates
    ldapmodule.set_option(ldapmodule.OPT_X_TLS_REQUIRE_CERT, ldapmodule.OPT_X_TLS_ALLOW)

    # Don't follow referrals
    ldapmodule.set_option(ldapmodule.OPT_REFERRALS, 0)

    def __init__(  # noqa: PLR0913
        self,
        uri,
        bind_dn,
        bind_pw,
        base_dn,
        server_type=None,
        domains=None,
        bitsdb_key=None,
        verbose=None
    ):
        """Initialize an instance."""
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_pw = bind_pw
        self.bitsdb_key = bitsdb_key
        self.domains = domains
        self.server_type = server_type
        self.uri = uri
        self.verbose = False
        if verbose:
            self.verbose = verbose

        # ldap module
        self.ldapmodule = ldapmodule
        self.modlist = modlist

        # Initialize the LDAP connection
        self.ldapobject = ldapmodule.initialize(uri)
        if self.verbose:
            print(f"  Connected to LDAP server: {uri}")

        # set the protocol version to version 3
        self.ldapobject.protocol_version = ldapmodule.VERSION3

        # Bind to LDAP
        self.ldapobject.simple_bind_s(bind_dn, bind_pw)
        if self.verbose:
            print(f"  Bound to LDAP server as: {bind_dn}")

        # get domains
        self.primary = None
        self.secondary = None
        if self.domains:
            if "primary" in self.domains:
                self.primary = self.domains["primary"]
            if "secondary" in self.domains:
                self.secondary = self.domains["secondary"]

    @staticmethod
    def format_exception_string(exc):
        """Return a nicely formatted string built from the passed exception."""
        exc_str = ""
        errdata = getattr(exc, "args", None)
        if errdata and len(errdata) > 0:
            if "desc" in errdata[0]:
                exc_str = f"{errdata[0]['desc']}: "
            if "info" in errdata[0]:
                exc_str += f"{errdata[0]['info']}"

        return exc_str.strip()

    def convert_entry(self, entry):
        """Convert a single entry to bytes instead of string."""
        for key in entry:
            items = []
            for i in entry[key]:
                val = i
                if isinstance(i, str):
                    val = i.encode("utf-8")
                items.append(val)
            entry[key] = items
        return entry

    def convert_entry_to_strings(self, entry):
        """Convert a single entry to strings instead of bytes."""
        for key in entry:
            items = []
            for i in entry[key]:
                val = i
                if isinstance(i, bytes):
                    val = i.decode("utf-8")
                items.append(val)
            entry[key] = items
        return entry

    def get_entries(self, filterstr="(objectClass=*)", attrlist=None, pagesize=None):
        """Return LDAP entries as a dict by dn."""
        base = self.base_dn
        scope = ldapmodule.SCOPE_SUBTREE
        results = self.search(base, scope, filterstr, attrlist, pagesize)
        entries = {}
        for dn, entry in results:
            if not dn:
                continue
            entries[dn] = entry
        return entries

    def get_ous(self):
        """Return a list of OUs."""
        return self.get_entries("(objectClass=organizationalUnit)")

    def search(self, base, scope, filterstr="(objectClass=*)", attrlist=None, pagesize=None):
        """Perform an LDAP search."""
        # for ad servers, use simple paged resuls
        if self.server_type == "ad":
            return self.get_paged_results(base, scope, filterstr, attrlist, pagesize)

        # Assumed defaults passed to search_ext_s:
        # attrsonly => 0,
        # serverctrls => None,
        # clientctrls => None,
        # timeout => -1,
        # sizelimit => 0,
        return self.ldapobject.search_ext_s(
            base=base,
            scope=scope,
            filterstr=filterstr,
            attrlist=attrlist,
        )

    def get_ldap_controls(self, pagesize=None, cookie=""):
        """Return LDAP Controls."""
        # set page size for simple paged results
        if not pagesize:
            pagesize = self.pagesize

        return ldapmodule.controls.SimplePagedResultsControl(
            cookie=cookie,
            criticality=True,
            size=pagesize,
        )

    def get_paged_results(self, base, scope, filterstr, attrlist, pagesize=None):
        """Perform a paged search query."""
        items = []

        # define ldap controls for paged results with our pagesize
        lc = self.get_ldap_controls(pagesize)

        # get all pages of results
        cookie = True
        while cookie:

            # Assumed defaults passed to search_ext:
            # attrsonly => 0,
            # clientctrls => None,
            # timeout => -1,
            # sizelimit => 0,

            # get a page of results
            msgid = self.ldapobject.search_ext(
                base=base,
                scope=scope,
                filterstr=filterstr,
                attrlist=attrlist,
                serverctrls=[lc],
            )

            # get the details of the query result:
            _, rdata, _, serverctrls = self.ldapobject.result3(msgid)

            # add the results data to the items list
            items.extend(rdata)

            # get the cookie for the next request
            cookie = self.set_cookie(lc, serverctrls)

        return items

    def add_entry(self, dn, new):
        """Add an entry in LDAP."""
        ldif = modlist.addModlist(self.convert_entry(new))
        try:
            self.ldapobject.add_s(dn, ldif)
        except ldapmodule.LDAPError as e:
            print(f"ERROR adding entry: {dn}")
            exc_str = self.format_exception_string(e)
            if exc_str:
                print(exc_str)
            return False
        return True

    def delete_entry(self, dn):
        """Delete an entry in LDAP."""
        try:
            self.ldapobject.delete_s(dn)
        except ldapmodule.LDAPError as e:
            print(f"ERROR deleting entry: {dn}")
            exc_str = self.format_exception_string(e)
            if exc_str:
                print(exc_str)
            return False
        return True

    def modify_entry(self, dn, current, new):
        """Modify an entry in LDAP."""
        ldif = modlist.modifyModlist(current, new)
        try:
            self.ldapobject.modify_s(dn, ldif)
        except ldapmodule.LDAPError as e:
            print(f"ERROR modifying entry: {dn}")
            exc_str = self.format_exception_string(e)
            if exc_str:
                print(exc_str)
            return False
        return True

    def create_ou(self, dn):
        """Create a new ou in LDAP."""
        ou = str(dn).split(",")[0].replace("ou=", "")
        record = {
            "objectClass": [
                "top",
                "organizationalUnit",
            ],
            "ou": [ou],
        }
        self.add_entry(dn, record)

    def set_cookie(self, lc, serverctrls):
        """Return the cookie for the next page of results."""
        # get the cookie from the serverctrls
        cookie = serverctrls[0].cookie

        # update the ldap controls object with the new cookie
        lc.cookie = cookie

        # return the cookie
        return cookie
