"""Person class file."""
from datetime import date, timedelta


class Person:
    """Person class."""

    def __init__(self, update, person):
        """Initialize a person instance."""
        self.person = person
        self.update = update
        self.verbose = update.verbose

        # get people data
        self.get_people_data(person)
        self.get_ad_data()
        self.get_google_data()
        self.get_nickname_data()
        self.get_phone_data()
        self.get_supervisor_data(person)
        self.get_trusted_tester_data()
        self.get_calculated_fields()

    def get_people_data(self, person):
        """Get data from People."""
        # email address
        email = person.get("email")
        if email:
            self.email = str(email)

        # emplid
        self.emplid = "{}".format(person.get("emplid", ""))

        # end date
        self.end_date = person.get("end_date")

        # first name
        first_name = person.get("first_name_ascii")
        if first_name:
            self.first_name = str(first_name)
        else:
            self.first_name = "EMPTY"

        # last name
        last_name = person.get("last_name_ascii")
        if last_name:
            self.last_name = str(last_name)
        else:
            self.last_name = "EMPTY"

        # full name
        full_name = person.get("full_name_ascii")
        if full_name:
            self.full_name = str(full_name)
        else:
            self.full_name = str(f"{self.first_name} {self.last_name}")

        self.home_institution = person.get("home_institution_ascii")
        self.org_unit = person.get("org_unit", "")
        self.person_id = person.get("person_id")
        if self.person_id:
            self.person_id = int(self.person_id)
        self.start_date = person.get("start_date")
        self.terminated = person.get("terminated")
        self.title = person.get("title")
        self.type = person.get("job_class")
        self.workday_delegates = person.get("workday_delegates")
        self.worker_type = person.get("worker_type")
        if self.worker_type == "Employee":
            self.type = "Employee"
        self.worker_sub_type = person.get("worker_sub_type")

        # username
        username = person.get("username")
        if username:
            self.username = username

    def get_ad_data(self):
        """Get data from AD."""
        self.nis_user = None

        if not self.update.ad_users:
            return

        if self.username in self.update.ad_users:
            ad_user = self.update.ad_users[self.username]

            gid_number = ad_user.get("gidNumber")
            login_shell = ad_user.get("loginShell")
            uid_number = ad_user.get("uidNumber")
            unix_home_directory = ad_user.get("unixHomeDirectory")

            if gid_number:
                self.gid = gid_number[0]
            if login_shell:
                self.login_shell = login_shell[0]
            if uid_number:
                self.uid = uid_number[0]
            if unix_home_directory:
                self.unix_home_directory = unix_home_directory[0]

            # check if all nis attributes are set
            if gid_number and login_shell and uid_number and unix_home_directory:
                self.nis_user = True

    def get_nickname_data(self):
        """Get Nickname data."""
        self.nicknames = None
        if self.username in self.update.nicknames:
            nicknames = self.update.nicknames[self.username]
            self.nicknames = nicknames["nicknames"]

    def get_phone_data(self):
        """Get Phone data."""
        self.phone = None
        if self.person_id in self.update.phones:
            phones = self.update.phones[self.person_id]
            phone = phones[0]
            self.phone = phone["phone"]

    def get_supervisor_data(self, person):
        """Get Supervisor."""
        self.supervisor_id = None
        supervisor_id = person.get("manager_id")
        if supervisor_id and supervisor_id in self.update.people and supervisor_id != self.emplid:
            self.supervisor_id = supervisor_id

    def get_google_data(self):
        """Get Google Data."""
        self.enterprise = False
        self.url = None

        # set the googe primaryEmail based on the broad email address
        google_email = f"{self.username}@broadinstitute.org"

        if google_email in self.update.google_users:
            google_user = self.update.google_users[google_email]
            google_id = google_user["id"]

            # check for enterprise license
            if google_id in self.update.enterprise_users:
                self.enterprise = True

            # check for google people record
            if google_id in self.update.google_people:
                person = self.update.google_people[google_id]
                # check for urls
                if person.get("urls") and not self.url:
                    self.url = str(person["urls"][0]["value"])

    def get_trusted_tester_data(self):
        """Get Trusted Tester data."""
        self.trusted_tester = None
        if self.username in self.update.trusted_testers:
            program = self.update.trusted_testers[self.username]
            self.trusted_tester = program["program"]

    def get_calculated_fields(self):
        """Get calculated fields."""
        if self.email:
            self.emails = [self.email]
        if self.org_unit:
            self.organization = self.org_unit.split(" > ")

        # set future hire cutoff date
        date_today = date.today()  # noqa:DTZ011
        start_date = date_today + timedelta(days=14)
        start = start_date.strftime("%Y-%m-%d")

        self.future_hire = False
        if self.start_date and self.start_date > start:
            self.future_hire = True

    def to_google(self, supervisor_dn):
        """Return a Person in Google LDAP format."""
        person = self.to_ldap(supervisor_dn)

        # set userPassword
        person["userPassword"] = ["*"]

        # set default gsuite license to Enterprise:
        gsuite_license = "Google-Workspace-Enterprise-Plus"
        if self.future_hire:
            gsuite_license = "Cloud-Identity"
        person["carLicense"] = [gsuite_license]

        # fix home directory
        if "homeDirectory" in person:
            person["homeDirectory"] = [f"/home/{self.username}"]

        person["pager"] = ["unarchive"]

        return person

    def to_ldap(self, supervisor_dn=None):
        """Return a Person in generic LDAP format."""
        person = {
            "cn": [self.full_name],
            "co": [self.home_institution],
            "description": [self.email],
            "displayName": [self.full_name],
            "email": [self.email],
            "employeeNumber": [self.emplid],
            "employeeType": [self.type],
            "givenName": [self.first_name],
            "mail": [self.email],
            "objectClass": [
                "top",
                "inetOrgPerson",
                "extensibleObject",
            ],
            "sn": [self.last_name],
            "title": [self.title],
            "uid": [self.username],
        }

        # org_unit info
        if self.org_unit:
            person["businessCategory"] = [self.org_unit]
            person["o"] = self.organization

        # check for nis info
        if self.nis_user:
            person["uidNumber"] = [self.uid]
            person["gecos"] = [self.full_name]
            person["gidNumber"] = [self.gid]
            person["loginShell"] = [self.login_shell]
            person["homeDirectory"] = [self.unix_home_directory]
            # update objectClass
            person["objectClass"].append("posixAccount")

        # check for phone info:
        if self.phone:
            person["telephoneNumber"] = [self.phone]

        # dn of supervisor
        if supervisor_dn:
            person["manager"] = [supervisor_dn]

        return person

    def to_servicenow(self, supervisor_dn):
        """Return a Person in Google LDAP format."""
        person = self.to_ldap(supervisor_dn)

        # set start date
        person["info"] = [self.start_date]

        # set workday_delegates
        if self.workday_delegates:
            person["documentPublisher"] = self.workday_delegates

        # set worker_sub_type
        person["employeeType"] = [self.worker_type]

        # set shadowExpire
        person["shadowExpire"] = ["0"]
        if not self.terminated:
            person["shadowExpire"] = ["1"]

        # set userPassword
        if self.nis_user:
            person["userPassword"] = [f"{{SASL}}{self.username}"]

        return person
