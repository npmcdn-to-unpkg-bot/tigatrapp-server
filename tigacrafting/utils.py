from models import ExpertReportAnnotation
from django.contrib.auth.models import User, Group
from sets import Set
import datetime

# Returns string with delta time between now and oldest created report anotation. Time is returned in days if possible,
# else hours. If delay is smaller than hours, no delay is returned
def get_oldest_pending_report_delay(some_user):
    pending = ExpertReportAnnotation.objects.filter(user=some_user).filter(validation_complete=False).extra(order_by = ['-created'])
    if pending.exists():
        most_delayed_annotation = pending[0]
        timedelta = annotation_timedelta(most_delayed_annotation)
        return get_formatted_timedelta(timedelta,most_delayed_annotation)
    return "No delays, everything up-to-date!"

# Given a timedelta and the annotation which it refers to, returns a formatted readable string with the delay and the
# report name
def get_formatted_timedelta(timedelta,annotation):
    if(timedelta.days != 0):
        return str(timedelta.days) + " days, caused by report " + annotation.report_id
    else:
        if(timedelta.seconds != 0):
            return str(timedelta.seconds / 3600) + " hours, caused by report " + annotation.report_id

# Returns timedelta between the created time of annotation and now
def annotation_timedelta(annotation):
    return datetime.datetime.now() - annotation.created.replace(tzinfo=None)

def get_most_delayed_expert():
    #retrieve experts
    group = Group.objects.get(name="expert")
    usersList = group.user_set.all()
    longest_timedelta = datetime.timedelta.min
    most_delayed_expert = None
    most_delayed_annotation = None
    for user_n in usersList:
        pending = ExpertReportAnnotation.objects.filter(user=user_n).filter(validation_complete=False).extra(order_by = ['-created'])
        if pending.exists():
            delayed_annotation = pending[0]
            timedelta = annotation_timedelta(delayed_annotation)
            if timedelta > longest_timedelta:
                longest_timedelta = timedelta
                most_delayed_expert = user_n
                most_delayed_annotation = delayed_annotation
    if most_delayed_expert is None:
        return {'user':'No one', 'delay': 'No delays, everything up-to-date!'}
    return {'user':most_delayed_expert.username, 'delay': get_formatted_timedelta(longest_timedelta,most_delayed_annotation)}

def get_number_reports_pending_one_validation():
    group = Group.objects.get(name="expert")
    usersList = group.user_set.all()
    reports = Set()
    for user_n in usersList:
        pending_annot = ExpertReportAnnotation.objects.filter(user=user_n).filter(validation_complete=False)
        for anno in pending_annot:
            related_report = anno.report
            these_annotations = ExpertReportAnnotation.objects.filter(report=related_report)
            if check_lacking_one_validation(these_annotations):
                reports.add(related_report)
    return len(reports)

def check_lacking_one_validation(annotations):
    non_validated = 0
    for anno in annotations:
        if not anno.validation_complete:
            non_validated += 1
    return non_validated == 1