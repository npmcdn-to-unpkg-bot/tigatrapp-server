from django.db import models
import uuid
import os
import datetime
from django.utils.timezone import utc


class TigaUser(models.Model):
    user_UUID = models.CharField(max_length=36, primary_key=True, help_text='UUID randomly generated on '
                                                                            'phone to identify each unique user. Must be exactly 36 '
                                                                            'characters (32 hex digits plus 4 hyphens).')
    registration_time = models.DateTimeField(auto_now=True, help_text='The date and time when user '
                                                                      'registered and consented to sharing '
                                                                 'data. Automatically set by '
                                                                 'server when user uploads registration.')

    def __unicode__(self):
        return self.user_UUID

    def number_of_fixes_uploaded(self):
        return Fix.objects.filter(user=self).count()

    def number_of_reports_uploaded(self):
        return Report.objects.filter(user=self).count()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


class Mission(models.Model):
    id = models.AutoField(primary_key=True, help_text='Unique identifier of the mission. Automatically generated by ' \
                                                  'server when mission created.')
    title = models.CharField(max_length=200, help_text='Title of mission')
    short_description = models.CharField(max_length=200, help_text='Text to be displayed in mission list.')
    long_description = models.CharField(max_length=1000, help_text='Text that fully explains mission to user')
    help_text = models.TextField(blank=True, help_text='Text to be displayed when user taps mission help button.')
    LANGUAGE_CHOICES = (('ca', 'Catalan'), ('es', 'Spanish'), ('en', 'English'), )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,  help_text='What language is mission '
                                                                                   'displayed in? (It will be sent '
                                                                                   'only users who have chosen this '
                                                                                   'language')
    PLATFORM_CHOICES = (('and', 'Android'), ('ios', 'iOS'), ('html', 'HTML5'), ('all', 'All platforms'),)
    platform = models.CharField(max_length=4, choices=PLATFORM_CHOICES, help_text='What type of device is this '
                                                                                   'mission is intended for? It will '
                                                                                   'be sent only to these devices')
    creation_time = models.DateTimeField(auto_now=True, help_text='Date and time mission was created by MoveLab. '
                                                                  'Automatically generated when mission saved.')
    expiration_time = models.DateTimeField(blank=True, null=True, help_text='Optional date and time when mission '
                                                                            'should expire (if ever). Mission will no longer be displayed to users after this date-time.')

    photo_mission = models.BooleanField(help_text='Should this mission allow users to attach photos to their '
                                                  'responses? (True/False).')
    url = models.URLField(blank=True, help_text='Optional URL that wll be displayed to user for this mission. (The '
                                                'entire mission can consist of user going to that URL and performing '
                                                'some action there. For security reasons, this URL must be within a '
                                                'MoveLab domain.')

    def __unicode__(self):
        return self.title

    def active_missions(self):
        return self.expiration_time >= datetime.datetime.utcnow().replace(tzinfo=utc)


class MissionTrigger(models.Model):
    mission = models.ForeignKey(Mission, related_name='triggers')
    lat_lower_bound = models.FloatField(blank=True, null=True, help_text='Optional lower-bound latitude for '
                                                                         'triggering mission to appear to user. Given in decimal degrees.')
    lat_upper_bound = models.FloatField(blank=True, null=True, help_text='Optional upper-bound latitude for '
                                                                         'triggering mission to appear to user. Given in decimal degrees.')
    lon_lower_bound = models.FloatField(blank=True, null=True, help_text='Optional lower-bound longitude for '
                                                                         'triggering mission to appear to user. Given in decimal degrees.')
    lon_upper_bound = models.FloatField(blank=True, null=True, help_text='Optional upper-bound longitude for '
                                                                         'triggering mission to appear to user. Given in decimal degrees.')
    time_lowerbound = models.TimeField(blank=True, null=True, help_text='Lower bound of optional time-of-day window '
                                                                        'for triggering mission. If '
                                                                        'location trigger also is specified, mission will '
                                                                        'be triggered only '
                                                                        'if user is found in that location within the window; if '
                                                                        'location is not specified, the mission will '
                                                                        'be triggered for all users who have their phones on during the '
                                                                        'time window. Given as time without date, '
                                                                        'formatted as ISO 8601 time string (e.g. '
                                                                        '"12:34:00") with no time zone specified (trigger '
                                                                        'is always based on local time zone of user.)')
    time_upperbound = models.TimeField(blank=True, null=True, help_text='Lower bound of optional time-of-day window '
                                                                        'for triggering mission. If '
                                                                        'location trigger also is specified, mission will '
                                                                        'be triggered only if user is found in that location within the window; if '
                                                                        'location is not specified, the mission will be '
                                                                        'triggered for all users who have their phones on during the '
                                                                        'time window. Given as time without date, '
                                                                        'formatted as ISO 8601 time string (e.g. '
                                                                        '"12:34:00") with no time zone specified (trigger '
                                                                        'is always based on local time zone of user.)')


class MissionItem(models.Model):
    mission = models.ForeignKey(Mission, related_name='items', help_text='Mission to which this item is associated.')
    question = models.CharField(max_length=1000, help_text='Question displayed to user.')
    answer_choices = models.CharField(max_length=1000, help_text='Response choices. Enter as strings separated by '
                                                                 'commas.')
    help_text = models.TextField(blank=True, help_text='Help text displayed to user for this item.')
    prepositioned_image_reference = models.IntegerField(blank=True, null=True, help_text='Optional image '
                                                                                         'displayed to user '
                                                                                         'within the help '
                                                                                         'message. Integer '
                                                                                         'reference to image '
                                                                                         'prepositioned on device.')
    attached_image = models.ImageField(upload_to='tigaserver_mission_images', blank=True, null=True,
                                       help_text='Optional Image displayed to user within the help message. File.')


class Report(models.Model):
    version_UUID = models.CharField(max_length=36, primary_key=True, help_text='UUID randomly generated on '
                                                'phone to identify each unique report version. Must be exactly 36 '
                                                'characters (32 hex digits plus 4 hyphens).')
    version_number = models.IntegerField(help_text='The report version number. Should be an integer that increments '
                                                   'by 1 for each repor version. Note that the user keeps only the '
                                                   'most recent version on the device, but all versions are stored on the server.')
    user = models.ForeignKey(TigaUser, help_text='user_UUID for the user sending this report. Must be exactly 36 '
                                                 'characters (32 hex digits plus 4 hyphens) and user must have '
                                                 'already registered this ID.')
    report_id = models.CharField(max_length=4, help_text='4-digit alpha-numeric code generated on user phone to '
                                                         'identify each unique report from that user. Digits should '
                                                         'lbe randomly drawn from the set of all lowercase and '
                                                         'uppercase alphabetic characters and 0-9, but excluding 0, '
                                                         'o, and O to avoid confusion if we ever need user to be able to refer to a report ID in correspondence with MoveLab (as was previously the case when we had them sending samples).')
    server_upload_time = models.DateTimeField(auto_now_add=True, help_text='Date and time on server when report '
                                                                           'uploaded. (Automatically generated by '
                                                                           'server.)')
    phone_upload_time = models.DateTimeField(help_text='Date and time on phone when it uploaded fix. Format '
                                                       'as ECMA '
                                                       '262 date time string (e.g. "2014-05-17T12:34:56'
                                                       '.123+01:00".')
    creation_time = models.DateTimeField(help_text='Date and time on phone when first version of repor was created. Format '
                                                       'as ECMA '
                                                       '262 date time string (e.g. "2014-05-17T12:34:56'
                                                       '.123+01:00".')
    version_time = models.DateTimeField(help_text='Date and time on phone when this version of repor was created. '
                                                  'Format '
                                                       'as ECMA '
                                                       '262 date time string (e.g. "2014-05-17T12:34:56'
                                                       '.123+01:00".')
    TYPE_CHOICES = (('adult', 'Adult'), ('site', 'Breeding Site'), ('mission', 'Mission'),)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, help_text="Type of report: 'adult', 'site', "
                                                                         "or 'mission'.", )
    mission = models.ForeignKey(Mission, blank=True, null=True, help_text='If this report was a response to a '
                                                                          'mission, the unique id field of that '
                                                                          'mission.')
    LOCATION_CHOICE_CHOICES = (('current', "Current location detected by user's device"), ('selected',
                                                                                           'Location selected by '
                                                                                           'user from map'),)
    location_choice = models.CharField(max_length=8, choices=LOCATION_CHOICE_CHOICES, help_text='Did user indicate '
                                                                                                'that report relates '
                                                                                                'to current location '
                                                                                                'of phone ("current") or to a location selected manually on the map ("selected")?')
    current_location_lon = models.FloatField(blank=True, null=True, help_text="Longitude of user's current location. "
                                                                              "In decimal degrees.")
    current_location_lat = models.FloatField(blank=True, null=True, help_text="Latitude of user's current location. "
                                                                              "In decimal degrees.")
    selected_location_lon = models.FloatField(blank=True, null=True, help_text="Latitude of location selected by "
                                                                               "user on map. "
                                                                              "In decimal degrees.")
    selected_location_lat = models.FloatField(blank=True, null=True, help_text="Longitude of location selected by "
                                                                               "user on map. "
                                                                              "In decimal degrees.")
    note = models.TextField(blank=True, help_text='Note user attached to report.')
    package_name = models.CharField(max_length=400, blank=True, help_text='Name of tigatrapp package from which this '
                                                                          'report was submitted.')
    package_version = models.IntegerField(blank=True, null=True, help_text='Version number of tigatrapp package from '
                                                                           'which this '
                                                                          'report was submitted.')
    device_manufacturer = models.CharField(max_length=200, blank=True, help_text='Manufacturer of device from which '
                                                                                'this '
                                                                          'report was submitted.')
    device_model = models.CharField(max_length=200, blank=True, help_text='Model of device from '
                                                                         'which this '
                                                                          'report was submitted.')
    os = models.CharField(max_length=200, blank=True, help_text='Operating system of device from which this '
                                                                          'report was submitted.')
    os_version = models.CharField(max_length=200, blank=True, help_text='Operating system version of device from '
                                                                        'which this '
                                                                          'report was submitted.')
    os_language = models.CharField(max_length=2, blank=True, help_text='Language setting of operating system on '
                                                                         'device from '
                                                                        'which this '
                                                                          'report was submitted. 2-digit '
                                                                        'ISO-639-1 language code.')
    app_language = models.CharField(max_length=2, blank=True, help_text='Language setting, within tigatrapp, '
                                                                        'of device '
                                                                          'from '
                                                                        'which this '
                                                                          'report was submitted. 2-digit '
                                                                        'ISO-639-1 language code.')

    def __unicode__(self):
        return self.version_UUID

    class Meta:
        unique_together = ("user", "version_UUID")


class ReportResponse(models.Model):
    report = models.ForeignKey(Report, related_name='responses', help_text='Report to which this response is ' \
                                                                          'associated.')
    question = models.CharField(max_length=1000, help_text='Question that the user responded to.')
    answer = models.CharField(max_length=1000, help_text='Answer that user selected.')

    def __unicode__(self):
        return str(self.id)


def make_image_uuid(path):
    def wrapper(instance, filename):
        extension = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), extension)
        return os.path.join(path, filename)
    return wrapper


class Photo(models.Model):
    """
    Photo uploaded by user.
    """
    photo = models.ImageField(upload_to=make_image_uuid('tigapics'), help_text='Phoeo uploaded by user.')
    report = models.ForeignKey(Report, help_text='Report and version to which this photo is associated (36-digit '
                                                 'report_UUID).')

    def __unicode__(self):
        return self.photo.name


class Fix(models.Model):
    """
    Location fix uploaded by user.
    """
    user = models.ForeignKey(TigaUser, help_text='The user_UUID for the user sending this location fix.')
    fix_time = models.DateTimeField(help_text='Date and time when fix was recorded on phone. Format as ECMA '
                                              '262 date time string (e.g. "2014-05-17T12:34:56'
                                              '.123+01:00".')
    server_upload_time = models.DateTimeField(auto_now_add=True, help_text='Date and time registered by server when '
                                                                           'it received fix upload. Automatically '
                                                                           'generated by server.')
    phone_upload_time = models.DateTimeField(help_text='Date and time on phone when it uploaded fix. Format '
                                                       'as ECMA '
                                                       '262 date time string (e.g. "2014-05-17T12:34:56'
                                                       '.123+01:00".')
    masked_lon = models.FloatField(help_text='Longitude rounded down to nearest 0.5 decimal degree (floor(lon/.5)*.5)'
                                             '.')
    masked_lat = models.FloatField(help_text='Latitude rounded down to nearest 0.5 decimal degree (floor(lat/.5)*.5).')
    power = models.FloatField(null=True, blank=True, help_text='Power level of phone at time fix recorded, '
                                                               'expressed as proportion of full charge. Range: 0-1.')

    def __unicode__(self):
        return self.user.user_UUID + " " + str(self.fix_time)

    class Meta:
        verbose_name = "fix"
        verbose_name_plural = "fixes"


class Configuration(models.Model):
    id = models.AutoField(primary_key=True, help_text='Auto-incremented primary key record ID.')
    samples_per_day = models.IntegerField(help_text="Number of randomly-timed location samples to take per day.")
    creation_time = models.DateTimeField(help_text='Date and time when this configuration was created by MoveLab. '
                                                   'Automatically generated when record is saved.',
                                         auto_now_add=True)

    def __unicode__(self):
        return str(self.samples_per_day)