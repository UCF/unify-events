# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models


class UNLAccount(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300, blank=True)
    streetaddress1 = models.CharField(max_length=765, blank=True)
    streetaddress2 = models.CharField(max_length=765, blank=True)
    city = models.CharField(max_length=300, blank=True)
    state = models.CharField(max_length=6, blank=True)
    zip = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=150, blank=True)
    fax = models.CharField(max_length=150, blank=True)
    email = models.CharField(max_length=300, blank=True)
    accountstatus = models.CharField(max_length=300, blank=True)
    datecreated = models.DateTimeField(null=True, blank=True)
    datelastupdated = models.DateTimeField(null=True, blank=True)
    sponsor_id = models.IntegerField()
    website = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = 'account'


class UNLAdmissioncharge(models.Model):
    id = models.IntegerField(primary_key=True)
    admissioninfogroup_id = models.IntegerField()
    price = models.CharField(max_length=300, blank=True)
    description = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = 'admissioncharge'


class UNLAdmissioninfo(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    type = models.CharField(max_length=765, blank=True)
    obligation = models.CharField(max_length=300, blank=True)
    contactname = models.CharField(max_length=300, blank=True)
    contactphone = models.CharField(max_length=150, blank=True)
    contactemail = models.CharField(max_length=765, blank=True)
    contacturl = models.TextField(blank=True)
    status = models.CharField(max_length=765, blank=True)
    additionalinfo = models.TextField(blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    opendate = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'admissioninfo'

class UNLAttendancerestriction(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'attendancerestriction'


class UNLAudience(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300, blank=True)
    standard = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'audience'


class UNLCalendar(models.Model):
    id = models.IntegerField(primary_key=True)
    account_id = models.IntegerField()
    name = models.CharField(max_length=765, blank=True)
    shortname = models.CharField(max_length=300, blank=True)
    website = models.CharField(max_length=765, blank=True)
    recommendationswithinaccount = models.IntegerField(null=True, blank=True)
    eventreleasepreference = models.CharField(max_length=765, blank=True)
    calendardaterange = models.IntegerField(null=True, blank=True)
    formatcalendardata = models.TextField(blank=True)
    uploadedcss = models.TextField(blank=True)
    uploadedxsl = models.TextField(blank=True)
    emaillists = models.TextField(blank=True)
    calendarstatus = models.CharField(max_length=765, blank=True)
    datecreated = models.DateTimeField(null=True, blank=True)
    uidcreated = models.CharField(max_length=765, blank=True)
    datelastupdated = models.DateTimeField(null=True, blank=True)
    uidlastupdated = models.CharField(max_length=765, blank=True)
    externalforms = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = 'calendar'


class UNLCalendarHasEvent(models.Model):
    id = models.IntegerField(primary_key=True)
    calendar_id = models.IntegerField()
    event_id = models.IntegerField()
    status = models.CharField(max_length=300, blank=True)
    source = models.CharField(max_length=300, blank=True)
    datecreated = models.DateTimeField(null=True, blank=True)
    uidcreated = models.CharField(max_length=300, blank=True)
    datelastupdated = models.DateTimeField(null=True, blank=True)
    uidlastupdated = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'calendar_has_event'


class UNLDocument(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    name = models.CharField(max_length=300, blank=True)
    url = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = 'document'


class UNLEvent(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True)
    othereventtype = models.CharField(max_length=765, blank=True)
    description = models.TextField(blank=True)
    shortdescription = models.CharField(max_length=765, blank=True)
    refreshments = models.CharField(max_length=765, blank=True)
    classification = models.CharField(max_length=300, blank=True)
    approvedforcirculation = models.IntegerField(null=True, blank=True)
    transparency = models.CharField(max_length=765, blank=True)
    status = models.CharField(max_length=300, blank=True)
    privatecomment = models.TextField(blank=True)
    otherkeywords = models.CharField(max_length=765, blank=True)
    imagetitle = models.CharField(max_length=300, blank=True)
    imageurl = models.TextField(blank=True)
    webpageurl = models.TextField(blank=True)
    listingcontactuid = models.CharField(max_length=765, blank=True)
    listingcontactname = models.CharField(max_length=300, blank=True)
    listingcontactphone = models.CharField(max_length=765, blank=True)
    listingcontactemail = models.CharField(max_length=765, blank=True)
    icalendar = models.TextField(blank=True)
    imagedata = models.TextField(blank=True)
    imagemime = models.CharField(max_length=765, blank=True)
    datecreated = models.DateTimeField(null=True, blank=True)
    uidcreated = models.CharField(max_length=300, blank=True)
    datelastupdated = models.DateTimeField(null=True, blank=True)
    uidlastupdated = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'event'


class UNLEventHasEventtype(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    eventtype_id = models.IntegerField()

    class Meta:
        db_table = 'event_has_eventtype'


class UNLEventHasKeyword(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    keyword_id = models.IntegerField()

    class Meta:
        db_table = 'event_has_keyword'


class UNLEventHasSponsor(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField(null=True, blank=True)
    sponsor_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'event_has_sponsor'


class UNLEventIsopentoAudience(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    audience_id = models.IntegerField()

    class Meta:
        db_table = 'event_isopento_audience'


class UNLEventTargetsAudience(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    audience_id = models.IntegerField()

    class Meta:
        db_table = 'event_targets_audience'


class UNLEventdatetime(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    location_id = models.IntegerField()
    starttime = models.DateTimeField(null=True, blank=True)
    endtime = models.DateTimeField(null=True, blank=True)
    room = models.CharField(max_length=765, blank=True)
    hours = models.CharField(max_length=765, blank=True)
    directions = models.TextField(blank=True)
    additionalpublicinfo = models.TextField(blank=True)

    class Meta:
        db_table = 'eventdatetime'


class UNLEventtype(models.Model):
    id = models.IntegerField(primary_key=True)
    calendar_id = models.IntegerField()
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=765, blank=True)
    eventtypegroup = models.CharField(max_length=24, blank=True)
    standard = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'eventtype'


class UNLKeyword(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        db_table = 'keyword'


class UNLLocation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300, blank=True)
    streetaddress1 = models.CharField(max_length=765, blank=True)
    streetaddress2 = models.CharField(max_length=765, blank=True)
    room = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=300, blank=True)
    state = models.CharField(max_length=6, blank=True)
    zip = models.CharField(max_length=30, blank=True)
    mapurl = models.TextField(blank=True)
    webpageurl = models.TextField(blank=True)
    hours = models.CharField(max_length=765, blank=True)
    directions = models.TextField(blank=True)
    additionalpublicinfo = models.CharField(max_length=765, blank=True)
    type = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=150, blank=True)

    class Meta:
        #standard = models.IntegerField(null=True, blank=True)
        db_table = 'location'


class UNLPerformer(models.Model):
    id = models.IntegerField(primary_key=True)
    performer_id = models.IntegerField()
    role_id = models.IntegerField()
    event_id = models.IntegerField()
    personalname = models.CharField(max_length=300, blank=True)
    name = models.CharField(max_length=765, blank=True)
    jobtitle = models.CharField(max_length=300, blank=True)
    organizationname = models.CharField(max_length=300, blank=True)
    personalwebpageurl = models.TextField(blank=True)
    organizationwebpageurl = models.TextField(blank=True)
    type = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = 'performer'


class UNLPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300, blank=True)
    description = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = 'permission'


class UNLPubliccontact(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    name = models.CharField(max_length=300, blank=True)
    jobtitle = models.CharField(max_length=300, blank=True)
    organization = models.CharField(max_length=300, blank=True)
    addressline1 = models.CharField(max_length=765, blank=True)
    addressline2 = models.CharField(max_length=765, blank=True)
    room = models.CharField(max_length=765, blank=True)
    city = models.CharField(max_length=300, blank=True)
    state = models.CharField(max_length=6, blank=True)
    zip = models.CharField(max_length=30, blank=True)
    emailaddress = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=150, blank=True)
    fax = models.CharField(max_length=150, blank=True)
    webpageurl = models.TextField(blank=True)

    class Meta:
        db_table = 'publiccontact'

class UNLRelatedevent(models.Model):
    event_id = models.IntegerField()
    related_event_id = models.IntegerField()
    relationtype = models.CharField(max_length=300)

    class Meta:
        db_table = 'relatedevent'


class UNLRole(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    standard = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'role'


class UNLSession(models.Model):
    user_uid = models.CharField(max_length=255, primary_key=True)
    lastaction = models.DateTimeField()
    data = models.TextField(blank=True)

    class Meta:
        db_table = 'session'


class UNLSponsor(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=765, blank=True)
    standard = models.IntegerField(null=True, blank=True)
    sponsortype = models.CharField(max_length=765, blank=True)
    webpageurl = models.TextField(blank=True)

    class Meta:
        db_table = 'sponsor'


class UNLSubscription(models.Model):
    id = models.IntegerField(primary_key=True)
    calendar_id = models.IntegerField()
    name = models.CharField(max_length=300, blank=True)
    automaticapproval = models.IntegerField()
    timeperiod = models.DateField(null=True, blank=True)
    expirationdate = models.DateField(null=True, blank=True)
    searchcriteria = models.TextField(blank=True)
    datecreated = models.DateTimeField(null=True, blank=True)
    uidcreated = models.CharField(max_length=300, blank=True)
    datelastupdated = models.DateTimeField(null=True, blank=True)
    uidlastupdated = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'subscription'


class UNLTestTable(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        db_table = 'test_table'


class UNLUser(models.Model):
    uid = models.CharField(max_length=255, primary_key=True)
    account_id = models.IntegerField()
    calendar_id = models.IntegerField(null=True, blank=True)
    accountstatus = models.CharField(max_length=300, blank=True)
    datecreated = models.DateTimeField(null=True, blank=True)
    uidcreated = models.CharField(max_length=300, blank=True)
    datelastupdated = models.DateTimeField(null=True, blank=True)
    uidlastupdated = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'user'


class UNLUserHasPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    permission_id = models.IntegerField()
    user_uid = models.CharField(max_length=300)
    calendar_id = models.IntegerField()

    class Meta:
        db_table = 'user_has_permission'


class UNLWebcast(models.Model):
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    title = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=300, blank=True)
    dateavailable = models.DateTimeField(null=True, blank=True)
    playertype = models.CharField(max_length=300, blank=True)
    bandwidth = models.CharField(max_length=765, blank=True)
    additionalinfo = models.TextField(blank=True)

    class Meta:
        db_table = 'webcast'


class UNLWebcastlink(models.Model):
    id = models.IntegerField(primary_key=True)
    webcast_id = models.IntegerField()
    url = models.TextField(blank=True)
    sequencenumber = models.IntegerField(null=True, blank=True)
    related = models.CharField(max_length=3, blank=True)

    class Meta:
        db_table = 'webcastlink'
