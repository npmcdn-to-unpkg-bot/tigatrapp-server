from models import ExpertReportAnnotation
from django.contrib.auth.models import User, Group
from tigaserver_app.models import Report
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


def get_most_recently_validated_report():
    # group = Group.objects.get(name="expert")
    # usersList = group.user_set.all()
    # shorter_timedelta = datetime.timedelta.max
    # report_dict = {}
    # for user_n in usersList:
    #     completed_annot = ExpertReportAnnotation.objects.filter(user=user_n).filter(validation_complete=True)
    #     for anno in completed_annot:
    #         related_report = anno.report
    #         these_annotations = ExpertReportAnnotation.objects.filter(report=related_report).filter(user__groups__name='expert').extra(order_by=['-last_modified'])
    #         if is_validated_by_three(these_annotations):
    #             most_recently_validated_in_annotations = annotation_timedelta(these_annotations[0])
    #             if most_recently_validated_in_annotations < shorter_timedelta:
    #                 shorter_timedelta = most_recently_validated_in_annotations
    #                 report_dict[related_report] = shorter_timedelta
    # return report_dict
    completed_annot = ExpertReportAnnotation.objects.filter(validation_complete=True).filter(user__groups__name='expert').extra(order_by=['-last_modified'])
    for anno in completed_annot:
        related_report = anno.report
        report_annotations = completed_annot.filter(report=related_report)
        if is_validated_by_three(report_annotations):
            most_recently_validated_in_annotations = annotation_timedelta(report_annotations[0])
            return get_formatted_timedelta(most_recently_validated_in_annotations,report_annotations[0])
    return "No validated reports available!"

def get_shortest_timedelta(annotations):
    shorter_timedelta = datetime.timedelta.max
    for annotation in annotations:
        if annotation_timedelta(annotation) < shorter_timedelta:
            shorter_timedelta = annotation_timedelta(annotation)
    return shorter_timedelta

# Given a timedelta and the annotation which it refers to, returns a formatted readable string with the delay and the
# report name
def get_formatted_timedelta(timedelta,annotation):
    if(timedelta.days != 0):
        return str(timedelta.days) + " days, report " + annotation.report_id
    else:
        if(timedelta.seconds != 0):
            return str(timedelta.seconds / 3600) + " hours, report " + annotation.report_id

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

def is_validated_by_three(annotations):
    count = 0
    for anno in annotations:
        if not anno.validation_complete:
            return False
        else:
            count +=1
    return count == 3
