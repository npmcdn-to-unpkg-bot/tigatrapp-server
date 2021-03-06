from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.managers import TaggableManager


def score_computation(n_total, n_yes, n_no, n_unknown = 0, n_undefined =0):
    return float(n_yes - n_no)/n_total


class CrowdcraftingTask(models.Model):
    task_id = models.IntegerField(unique=True, null=True, default=None)
    photo = models.OneToOneField('tigaserver_app.Photo')

    def __unicode__(self):
        return str(self.task_id)

    def get_mosquito_validation_score(self):
        n_total = CrowdcraftingResponse.objects.filter(task=self).count()
        if n_total == 0:
            return None
        else:
            n_yes = CrowdcraftingResponse.objects.filter(task=self, mosquito_question_response='mosquito-yes').count()
            n_no = CrowdcraftingResponse.objects.filter(task=self, mosquito_question_response='mosquito-no').count()
            return score_computation(n_total=n_total, n_yes=n_yes, n_no=n_no)

    def get_tiger_validation_score(self):
        n_total = CrowdcraftingResponse.objects.filter(task=self).count()
        if n_total == 0:
            return None
        else:
            n_yes = CrowdcraftingResponse.objects.filter(task=self, tiger_question_response='tiger-yes').count()
            n_no = CrowdcraftingResponse.objects.filter(task=self, tiger_question_response='tiger-no').count() + CrowdcraftingResponse.objects.filter(task=self, tiger_question_response='undefined', mosquito_question_response='mosquito-no').count()
            return score_computation(n_total=n_total, n_yes=n_yes, n_no=n_no)

    def get_tiger_validation_score_cat(self):
        if self.get_tiger_validation_score() is not None:
            return int(round(2.499999 * self.get_tiger_validation_score(), 0))
        else:
            return None

    def get_site_validation_score(self):
        n_total = CrowdcraftingResponse.objects.filter(task=self).count()
        if n_total == 0:
            return None
        else:
            n_yes = CrowdcraftingResponse.objects.filter(task=self, site_question_response='site-yes').count()
            n_no = CrowdcraftingResponse.objects.filter(task=self, site_question_response='site-no').count()
            return score_computation(n_total=n_total, n_yes=n_yes, n_no=n_no)

    def get_site_validation_score_cat(self):
        if self.get_site_validation_score() is not None:
            return int(round(2.499999 * self.get_site_validation_score(), 0))
        else:
            return None

    def get_site_individual_responses_html(self):
        n_total = CrowdcraftingResponse.objects.filter(task=self).count()
        if n_total == 0:
            return None
        else:
            n_anon_yes = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, site_question_response='site-yes').count()
            n_anon_no = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, site_question_response='site-no').count()
            n_reg_yes = CrowdcraftingResponse.objects.filter(task=self, site_question_response='site-yes').exclude(user__user_id=None).count()
            n_reg_no = CrowdcraftingResponse.objects.filter(task=self, site_question_response='site-no').exclude(user__user_id=None).count()
            n_anon_unknown = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, site_question_response='site-unknown').count()
            n_anon_blank = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, site_question_response='undefined').count()
            n_reg_unknown = CrowdcraftingResponse.objects.filter(task=self, site_question_response='site-unknown').exclude(user__user_id=None).count()
            n_reg_blank = CrowdcraftingResponse.objects.filter(task=self, site_question_response='undefined').exclude(user__user_id=None).count()
            return '<table><tr><th>Resp.</th><th>Reg. Users</th><th>Anon. Users</th><th>Total</th></tr><tr><td>Yes</td><td>' + str(n_reg_yes) + '</td><td>' + str(n_anon_yes) + '</td><td>' + str(n_reg_yes + n_anon_yes) + '</td></tr><tr><td>No</td><td>' + str(n_reg_no) + '</td><td>' + str(n_anon_no) + '</td><td>' + str(n_reg_no + n_anon_no) + '</td></tr><tr><td>Not sure</td><td>' + str(n_reg_unknown) + '</td><td>' + str(n_anon_unknown) + '</td><td>' + str(0 + n_reg_unknown + n_anon_unknown) + '</td></tr><tr><td>Blank</td><td>' + str(n_reg_blank) + '</td><td>' + str(n_anon_blank) + '</td><td>' + str(n_reg_blank + n_anon_blank) + '</td></tr><tr><td>Total</td><td>' + str(n_reg_yes + n_reg_no + n_reg_unknown + n_reg_blank) + '</td><td>' + str(n_anon_yes + n_anon_no + n_anon_unknown + n_anon_blank) + '</td><td>' + str(n_anon_yes + n_anon_no + n_anon_unknown + n_anon_blank + n_reg_yes + n_reg_no + n_reg_unknown + n_reg_blank) + '</td></tr></table>'

    def get_tiger_individual_responses_html(self):
        n_total = CrowdcraftingResponse.objects.filter(task=self).count()
        if n_total == 0:
            return None
        else:
            n_anon_yes = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, tiger_question_response='tiger-yes').count()
            n_anon_no = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, tiger_question_response='tiger-no').count() + CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, mosquito_question_response='mosquito-no', tiger_question_response='undefined').count()
            n_reg_yes = CrowdcraftingResponse.objects.filter(task=self, tiger_question_response='tiger-yes').exclude(user__user_id=None).count()
            n_reg_no = CrowdcraftingResponse.objects.filter(task=self, tiger_question_response='tiger-no').exclude(user__user_id=None).count() + CrowdcraftingResponse.objects.filter(task=self, mosquito_question_response='mosquito-no', tiger_question_response='undefined').exclude(user__user_id=None).count()
            n_anon_unknown = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, tiger_question_response='tiger-unknown').count()
            n_anon_blank = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, tiger_question_response='undefined').exclude(mosquito_question_response='mosquito-no').count()
            n_reg_unknown = CrowdcraftingResponse.objects.filter(task=self, tiger_question_response='tiger-unknown').exclude(user__user_id=None).count()
            n_reg_blank = CrowdcraftingResponse.objects.filter(task=self, tiger_question_response='undefined').exclude(mosquito_question_response='mosquito-no').exclude(user__user_id=None).count()
            return '<table><tr><th>Resp.</th><th>Reg. Users</th><th>Anon. Users</th><th>Total</th></tr><tr><td>Yes</td><td>' + str(n_reg_yes) + '</td><td>' + str(n_anon_yes) + '</td><td>' + str(n_reg_yes + n_anon_yes) + '</td></tr><tr><td>No</td><td>' + str(n_reg_no) + '</td><td>' + str(n_anon_no) + '</td><td>' + str(n_reg_no + n_anon_no) + '</td></tr><tr><td>Not sure</td><td>' + str(n_reg_unknown) + '</td><td>' + str(n_anon_unknown) + '</td><td>' + str(0 + n_reg_unknown + n_anon_unknown) + '</td></tr><tr><td>Blank</td><td>' + str(n_reg_blank) + '</td><td>' + str(n_anon_blank) + '</td><td>' + str(n_reg_blank + n_anon_blank) + '</td></tr><tr><td>Total</td><td>' + str(n_reg_yes + n_reg_no + n_reg_unknown + n_reg_blank) + '</td><td>' + str(n_anon_yes + n_anon_no + n_anon_unknown + n_anon_blank) + '</td><td>' + str(n_anon_yes + n_anon_no + n_anon_unknown + n_anon_blank + n_reg_yes + n_reg_no + n_reg_unknown + n_reg_blank) + '</td></tr></table>'

    def get_mosquito_individual_responses_html(self):
        n_total = CrowdcraftingResponse.objects.filter(task=self).count()
        if n_total == 0:
            return None
        else:
            n_anon_yes = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, mosquito_question_response='mosquito-yes').count()
            n_anon_no = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, mosquito_question_response='mosquito-no').count()
            n_reg_yes = CrowdcraftingResponse.objects.filter(task=self, mosquito_question_response='mosquito-yes').exclude(user__user_id=None).count()
            n_reg_no = CrowdcraftingResponse.objects.filter(task=self, mosquito_question_response='mosquito-no').exclude(user__user_id=None).count()
            n_anon_unknown = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, mosquito_question_response='mosquito-unknown').count()
            n_anon_blank = CrowdcraftingResponse.objects.filter(task=self, user__user_id=None, mosquito_question_response='undefined').count()
            n_reg_unknown = CrowdcraftingResponse.objects.filter(task=self, mosquito_question_response='mosquito-unknown').exclude(user__user_id=None).count()
            n_reg_blank = CrowdcraftingResponse.objects.filter(task=self, mosquito_question_response='undefined').exclude(user__user_id=None).count()
            return '<table><tr><th>Resp.</th><th>Reg. Users</th><th>Anon. Users</th><th>Total</th></tr><tr><td>Yes</td><td>' + str(n_reg_yes) + '</td><td>' + str(n_anon_yes) + '</td><td>' + str(n_reg_yes + n_anon_yes) + '</td></tr><tr><td>No</td><td>' + str(n_reg_no) + '</td><td>' + str(n_anon_no) + '</td><td>' + str(n_reg_no + n_anon_no) + '</td></tr><tr><td>Not sure</td><td>' + str(n_reg_unknown) + '</td><td>' + str(n_anon_unknown) + '</td><td>' + str(0 + n_reg_unknown + n_anon_unknown) + '</td></tr><tr><td>Blank</td><td>' + str(n_reg_blank) + '</td><td>' + str(n_anon_blank) + '</td><td>' + str(n_reg_blank + n_anon_blank) + '</td></tr><tr><td>Total</td><td>' + str(n_reg_yes + n_reg_no + n_reg_unknown + n_reg_blank) + '</td><td>' + str(n_anon_yes + n_anon_no + n_anon_unknown + n_anon_blank) + '</td><td>' + str(n_anon_yes + n_anon_no + n_anon_unknown + n_anon_blank + n_reg_yes + n_reg_no + n_reg_unknown + n_reg_blank) + '</td></tr></table>'

    def get_crowdcrafting_n_responses(self):
        return CrowdcraftingResponse.objects.filter(task=self).count()

    mosquito_validation_score = property(get_mosquito_validation_score)
    tiger_validation_score = property(get_tiger_validation_score)
    site_validation_score = property(get_site_validation_score)
    site_individual_responses_html = property(get_site_individual_responses_html)
    tiger_individual_responses_html = property(get_tiger_individual_responses_html)
    mosquito_individual_responses_html = property(get_mosquito_individual_responses_html)
    crowdcrafting_n_responses = property(get_crowdcrafting_n_responses)
    tiger_validation_score_cat = property(get_tiger_validation_score_cat)
    site_validation_score_cat = property(get_site_validation_score_cat)


class CrowdcraftingUser(models.Model):
    user_id = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return str(self.id)


class CrowdcraftingResponse(models.Model):
    response_id = models.IntegerField()
    task = models.ForeignKey(CrowdcraftingTask, related_name="responses")
    user = models.ForeignKey(CrowdcraftingUser, related_name="responses", blank=True, null=True)
    user_lang = models.CharField(max_length=10, blank=True)
    mosquito_question_response = models.CharField(max_length=100)
    tiger_question_response = models.CharField(max_length=100)
    site_question_response = models.CharField(max_length=100)
    created = models.DateTimeField(blank=True, null=True)
    finish_time = models.DateTimeField(blank=True, null=True)
    user_ip = models.IPAddressField(blank=True, null=True)

    def __unicode__(self):
        return str(self.id)


class Annotation(models.Model):
    user = models.ForeignKey(User, related_name='annotations')
    task = models.ForeignKey(CrowdcraftingTask, related_name='annotations')
    tiger_certainty_percent = models.IntegerField('Degree of belief', validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    value_changed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    working_on = models.BooleanField(default=False)

    def __unicode__(self):
        return "Annotation: " + str(self.id) + ", Task: " + str(self.task.task_id)


class MoveLabAnnotation(models.Model):
    task = models.OneToOneField(CrowdcraftingTask, related_name='movelab_annotation')
    CATEGORIES = ((-2, 'Definitely not a tiger mosquito'), (-1, 'Probably not a tiger mosquito'), (0, 'Not sure'), (1, 'Probably a tiger mosquito'), (2, 'Definitely a tiger mosquito'))
    tiger_certainty_category = models.IntegerField('Certainty', choices=CATEGORIES, blank=True, null=True)
    certainty_notes = models.TextField(blank=True)
    hide = models.BooleanField('Hide photo from public', default=False)
    edited_user_notes = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

TIGER_CATEGORIES = ((2, 'Definitely Aedes albopictus'), (1, 'Probably Aedes albopictus'),  (0, 'Not sure'), (-1, 'Probably neither albopictus nor aegypti'), (-2, 'Definitely not albopictus or aegypti'))

#WARNING!! THIS IS USED FOR VISUALIZATION ONLY, NEVER SHOULD BE USED FOR DATA INPUT!!!
TIGER_CATEGORIES_SEPARATED = ((2, 'Definitely Aedes albopictus'), (1, 'Probably Aedes albopictus'),  (0, 'Not sure'), (-1, 'Probably not albopictus'), (-2, 'Definitely not albopictus'))

AEGYPTI_CATEGORIES = ((2, 'Definitely Aedes aegypti'), (1, 'Probably Aedes aegypti'),  (0, 'Not sure'), (-1, 'Probably neither albopictus nor aegypti'), (-2, 'Definitely not albopictus or aegypti'))

#WARNING!! THIS IS USED FOR VISUALIZATION ONLY, NEVER SHOULD BE USED FOR DATA INPUT!!!
AEGYPTI_CATEGORIES_SEPARATED = ((2, 'Definitely Aedes aegypti'), (1, 'Probably Aedes aegypti'),  (0, 'Not sure'), (-1, 'Probably not aegypti'), (-2, 'Definitely not aegypti'))

SITE_CATEGORIES = ((2, 'Definitely a breeding site'), (1, 'Probably a breeding site'), (0, 'Not sure'), (-1, 'Probably not a breeding site'), (-2, 'Definitely not a breeding site'))

STATUS_CATEGORIES = ((1, 'public'), (0, 'flagged'), (-1, 'hidden'))


class ExpertReportAnnotation(models.Model):
    user = models.ForeignKey(User, related_name="expert_report_annotations")
    report = models.ForeignKey('tigaserver_app.Report', related_name='expert_report_annotations')
    tiger_certainty_category = models.IntegerField('Tiger Certainty', choices=TIGER_CATEGORIES, default=None, blank=True, null=True, help_text='Your degree of belief that at least one photo shows a tiger mosquito')
    aegypti_certainty_category = models.IntegerField('Aegypti Certainty', choices=AEGYPTI_CATEGORIES, default=None, blank=True, null=True, help_text='Your degree of belief that at least one photo shows an Aedes aegypti')
    tiger_certainty_notes = models.TextField('Internal Aedes Certainty Comments', blank=True, help_text='Internal notes for yourself or other experts')
    site_certainty_category = models.IntegerField('Site Certainty', choices=SITE_CATEGORIES, default=None, blank=True, null=True, help_text='Your degree of belief that at least one photo shows a tiger mosquito breeding site')
    site_certainty_notes = models.TextField('Internal Site Certainty Comments', blank=True, help_text='Internal notes for yourself or other experts')
    edited_user_notes = models.TextField('Public Note', blank=True, help_text='Notes to display on public map')
    message_for_user = models.TextField('Message to User', blank=True, help_text='Message that user will receive when viewing report on phone')
    status = models.IntegerField('Status', choices=STATUS_CATEGORIES, default=1, help_text='Whether report should be displayed on public map, flagged for further checking before public display), or hidden.')
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    validation_complete = models.BooleanField(default=False, help_text='Mark this when you have completed your review and are ready for your annotation to be displayed to public.')
    revise = models.BooleanField(default=False, help_text='For superexperts: Mark this if you want to substitute your annotation for the existing Expert annotations. Make sure to also complete your annotation form and then mark the "validation complete" box.')
    best_photo = models.ForeignKey('tigaserver_app.Photo', related_name='expert_report_annotations', null=True, blank=True)
    linked_id = models.CharField('Linked ID', max_length=10, help_text='Use this field to add any other ID that you want to associate the record with (e.g., from some other database).', blank=True)
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    simplified_annotation = models.BooleanField(default=False, help_text='If True, the report annotation interface shows less input controls')
    tags = TaggableManager(blank=True)

    def is_superexpert(self):
        return 'superexpert' in self.user.groups.values_list('name', flat=True)

    def is_expert(self):
        return 'expert' in self.user.groups.values_list('name', flat=True)

    def get_others_annotation_html(self):
        result = ''
        this_user = self.user
        this_report = self.report
        other_annotations = ExpertReportAnnotation.objects.filter(report=this_report).exclude(user=this_user)
        for ano in other_annotations.all():
            result += '<p>User: ' + ano.user.username + '</p>'
            result += '<p>Last Edited: ' + ano.last_modified.strftime("%d %b %Y %H:%m") + ' UTC</p>'
            if this_report.type == 'adult':
                result += '<p>Tiger Certainty: ' + (ano.get_tiger_certainty_category_display() if ano.get_tiger_certainty_category_display() else "") + '</p>'
                result += '<p>Tiger Notes: ' + ano.tiger_certainty_notes + '</p>'
            elif this_report.type == 'site':
                result += '<p>Site Certainty: ' + (ano.get_site_certainty_category_display() if ano.get_site_certainty_category_display() else "") + '</p>'
                result += '<p>Site Notes: ' + ano.site_certainty_notes + '</p>'
            result += '<p>Selected photo: ' + (ano.best_photo.popup_image() if ano.best_photo else "") + '</p>'
            result += '<p>Edited User Notes: ' + ano.edited_user_notes + '</p>'
            result += '<p>Message To User: ' + ano.message_for_user + '</p>'
            result += '<p>Status: ' + ano.get_status_display() if ano.get_status_display() else "" + '</p>'
            result += '<p>Validation Complete? ' + str(ano.validation_complete) + '</p><hr>'
        return result

    def get_score(self):
        score = -3
        if self.report.type == 'site':
            score = self.site_certainty_category
        elif self.report.type == 'adult':
            if self.aegypti_certainty_category == 2:
                score = 4
            elif self.aegypti_certainty_category == 1:
                score = 3
            else:
                score = self.tiger_certainty_category
        if score is not None:
            return score
        else:
            return -3

    def get_category(self):
        if self.report.type == 'site':
            return dict([(-3, 'Unclassified')] + list(SITE_CATEGORIES))[self.get_score()]
        elif self.report.type == 'adult':
            if self.get_score() > 2:
                return dict([(-3, 'Unclassified')] + list(AEGYPTI_CATEGORIES))[self.get_score()-2]
            else:
                return dict([(-3, 'Unclassified')] + list(TIGER_CATEGORIES))[self.get_score()]

    def get_status_bootstrap(self):
        result = '<span data-toggle="tooltip" data-placement="bottom" title="' + self.get_status_display() + '" class="' + ('glyphicon glyphicon-eye-open' if self.status == 1 else ('glyphicon glyphicon-flag' if self.status == 0 else 'glyphicon glyphicon-eye-close')) + '"></span>'
        return result

    def get_score_bootstrap(self):
        result = '<span class="label label-default" style="background-color:' + ('red' if self.get_score() == 2 else ('orange' if self.get_score() == 1 else ('white' if self.get_score() == 0 else ('grey' if self.get_score() == -1 else 'black')))) + ';">' + self.get_category() + '</span>'
        return result


class UserStat(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    grabbed_reports = models.IntegerField('Grabbed reports', default=0, help_text='Number of reports grabbed since implementation of simplified reports. For each 3 reports grabbed, one is simplified')

    def is_expert(self):
        return self.user.groups.filter(name="expert").exists()

    def is_superexpert(self):
        return self.user.groups.filter(name="superexpert").exists()

    def is_movelab(self):
        return self.user.groups.filter(name="movelab").exists()

    def is_team_bcn(self):
        return self.user.groups.filter(name="team_bcn").exists()

    def is_team_not_bcn(self):
        return self.user.groups.filter(name="team_not_bcn").exists()

    def is_team_everywhere(self):
        return self.user.groups.exclude(name="team_not_bcn").exclude(name="team_bcn").exists()

    def n_completed_annotations(self):
        return self.user.expert_report_annotations.filter(validation_complete=True).count()

    def n_pending_annotations(self):
        return self.user.expert_report_annotations.filter(validation_complete=False).count()
