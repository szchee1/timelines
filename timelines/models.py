from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Max, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords

from datetime import datetime as dt, timedelta
import pytz
import numpy as np
import itertools
import pandas as pd

# All dates should be in SGT, unless specified as UTC.

'''RU Calculation'''

def ru_calc_task(team):

    if team == 'agency':
        campaign_team_hours = 'campaign__agency_hours'
        team_name = 'eClerx' # Magic here essential to calculate eClerx RUs

    else:
        campaign_team_hours = 'campaign__' + team + '_hours'
        team_name = team.title()

    tasks_list = tasks.objects.filter(~Q(campaign__type__name='Template'), owner__team__name=team_name).values('campaign__id', campaign_team_hours, 'id', 'start', 'end')

    if len(tasks_list) > 0:

        holiday_list = [str(date) for date in holidays.objects.values_list('date', flat=True)]
        tasks_list2 = [dict(task, dates = pd.bdate_range(task['start'], task['end'], freq='C', weekmask='1111100', holidays=holiday_list, closed='left')) for task in tasks_list]
        df = pd.DataFrame.from_records(tasks_list2)
        df2 = df.groupby(['campaign__id', campaign_team_hours])['dates'].apply(list)

        df3 = pd.Series.to_frame(df2).reset_index()
        df3['dates2']=df3['dates'].apply(lambda x: list(itertools.chain.from_iterable(x))) # unpack list of lists

        ''' Resource Utilization Calculation '''
        df3['days']=df3['dates2'].apply(lambda x: len(x))
        df3['avg_daily_hours']=df3[campaign_team_hours]/df3['days']

        df4 = df3.drop(columns=['dates']).set_index(['campaign__id', campaign_team_hours, 'days', 'avg_daily_hours'])
        # df4 = df4['dates2'].reset_index()
        df5 = df4['dates2'].apply(pd.Series).stack().reset_index()[['campaign__id', 'avg_daily_hours', 0]]
        df5.rename(columns={0: 'date'}, inplace=True)
        print(df5)
        df5['week'] = df5['date'].apply(lambda x: x.isocalendar()[1])
        df5['year'] = df5['date'].apply(lambda x: x.year)
        df5['week_start_prep'] = df5['year'].map(str) + '-' + df5['week'].apply(lambda x: x-1).map(str) + '-1'
        df5['week_start'] = df5['week_start_prep'].apply(lambda x: dt.strptime(x, '%Y-%W-%w'))

        final_df = df5.groupby(['week']).agg({'avg_daily_hours': np.sum}).reset_index()
        final_df.rename(columns={'avg_daily_hours': 'total_hours'}, inplace=True)

        final = final_df.to_dict('records')

    else:
        final = tasks_list

    return final


def campaign_count():
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status="active").values('id', 'start', 'end')

    if len(campaign_list) > 0: # This condition should be for sure to happen

        holiday_list = [str(date) for date in holidays.objects.values_list('date', flat=True)]
        campaign_list2 = [dict(campaign, dates = pd.bdate_range(campaign['start'], campaign['end'], freq='C', weekmask='1111100', holidays=holiday_list, closed='left')) for campaign in campaign_list]

        df = pd.DataFrame.from_records(campaign_list2)
        df2 = df.groupby(['id'])['dates'].apply(list)
        df3 = pd.Series.to_frame(df2).reset_index()
        df3['dates2']=df3['dates'].apply(lambda x: list(itertools.chain.from_iterable(x))) # unpack list of lists

        df4 = df3.drop(columns=['dates']).set_index(['id'])
        df5 = df4['dates2'].apply(pd.Series).stack().reset_index()[['id', 0]]
        df5.rename(columns={0: 'date'}, inplace=True)
        df5['week'] = df5['date'].apply(lambda x: x.isocalendar()[1])
        df5['year'] = df5['date'].apply(lambda x: x.year)
        df5['week_start_prep'] = df5['year'].map(str) + '-' + df5['week'].apply(lambda x: x-1).map(str) + '-1'
        df5['week_start'] = df5['week_start_prep'].apply(lambda x: dt.strptime(x, '%Y-%W-%w'))

        final_df = df5.groupby(['week']).agg({'id': pd.Series.nunique}).reset_index()
        final_df.rename(columns={'id': 'total_campaigns'}, inplace=True)

        final = final_df.to_dict('records')

        return final


        # final_df = df5.groupby(['week']).agg({'avg_daily_hours': np.sum, 'campaign__id': pd.Series.nunique}).reset_index()
        # final_df.rename(columns={'avg_daily_hours': 'total_hours', 'campaign__id': 'total_campaigns'}, inplace=True)


def recalculate(editor):
    # Set re-calculated values
    # Reset all values:
    for week in weeks.objects.all():
        week.ops_hours = 0
        week.agency_hours = 0
        week.analytics_hours = 0

        week.save()

    team_list = ['ops', 'agency', 'analytics']
    # [i.lower() for i in list(teams.objects.filter(~Q(name='LCM')).values_list('name'.lower(), flat=True))]

    # To be safe for now just re-calculate whenever save happens.
    # Can be optimised later to only update if dates/new campiagn is added:
    for team in team_list:
        final = ru_calc_task(team)  #, campaign_start, campaign_end)

        if len(final) > 0:
            for i in final:
                week_no = i['week']
                week_hours = i['total_hours']

                w0 = weeks.objects.filter(no=week_no)

                for changes in w0:
                    if team == 'ops':
                        print("OPS")
                        changes.ops_hours = week_hours

                    elif team == 'analytics':
                        print("ANALYTICS")
                        changes.analytics_hours = week_hours

                    # elif team == 'agency':
                    # CHANGE this to be scalable to include more than 1 agency.
                    # How can new admin add new agency?

                    else: # all other teams - i.e. agencies
                        print("AGENCY")
                        changes.agency_hours = week_hours

                    changes.last_edited_by = editor

                    changes.save()


    # To be safe for now just re-calculate whenever save happens.
    campaign_count_ = campaign_count()


    for week in weeks.objects.all():
        week.no_campaign = 0
        week.save()

    for week_no in campaign_count_:
        w0 = weeks.objects.get(no=week_no['week'])
        w0.no_campaign = week_no['total_campaigns']
        w0.last_edited_by = editor

        w0.save()


def recalculate_task(editor):
    # Reset all values:
    for week in weeks.objects.all():
        week.ops_hours = 0
        week.agency_hours = 0
        week.analytics_hours = 0

        week.save()

    team_list = ['ops', 'agency', 'analytics']

    for team in team_list:

        final = ru_calc_task(team)

        for i in final:
            week_no = i['week']
            week_hours = i['total_hours']

            w0 = weeks.objects.filter(no=week_no)

            for changes in w0:
                if team == 'ops':
                    changes.ops_hours = week_hours
                elif team == 'agency':
                    changes.agency_hours = week_hours
                elif team == 'analytics':
                    changes.analytics_hours = week_hours

                # changes.no_campaign = week_campaigns
                changes.last_edited_by = editor

                changes.save()


'''Locks should restrict dates edit on campaign level, as all task dates are dependant.
Even if we could auto set all tasks to update after campaign has updated, user experience would be affected -
some users would question why has the date changed after they just recently changed the date'''
class locks(models.Model):
    user = models.ForeignKey(User, related_name='locks_user', on_delete = models.PROTECT)
    type = models.CharField(max_length=100) # campaign, task, campaign info, campaign ru, campaign extend, progress
    identifier = models.IntegerField() # campaignid, taskid, etc.
    status = models.CharField(max_length=100) # locked / released
    timestamp_utc = models.DateTimeField(default = timezone.now)

    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "locks"

# OPTIONS
class holidays(models.Model):
    date = models.DateField()
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "holidays"

    def __str__(self):
        return str(self.date)


class progress(models.Model):
    name = models.CharField(max_length = 200)
    history = HistoricalRecords()

    @property
    def progress_text(self):
        if self.name == "On Track":
            color = "on-track-text"
        elif self.name == "Potential Delay":
            color = "potential-delay-text"
        elif self.name == "Delayed":
            color = "delay-text"
        elif self.name == "Completed":
            color = "complete-text"
        elif self.name == "Cancelled":
            color = "complete-text"

        return color

    @property
    def progress_icon(self):
        if self.name == "On Track":
            color = "on-track-circle"
        elif self.name == "Potential Delay":
            color = "potential-delay-circle"
        elif self.name == "Delayed":
            color = "delay-circle"
        elif self.name == "Completed":
            color = "complete-circle"
        elif self.name == "Cancelled":
            color = "cancel-circle"

        return color

    class Meta:
        verbose_name_plural = "progress"

    def __str__(self):
        return self.name


class verticals(models.Model):
    name = models.CharField(max_length = 200)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "verticals"

    def __str__(self):
        return self.name


class types(models.Model):
    name = models.CharField(max_length = 200)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "types"

    def __str__(self):
        return self.name

'''Countries & Platforms won't actually be used as ForeignKeys. They serve 2 functions:
1. To control form input so analysis can be done.
2. To allow administrators to add new country/platform(s) whenever, rather than having to change the HTML.'''

class countries(models.Model):
    name = models.CharField(max_length = 200)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class platforms(models.Model):
    name = models.CharField(max_length = 200)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "platforms"

    def __str__(self):
        return self.name


class complexities(models.Model):
    name = models.CharField(max_length = 200)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "complexities"

    def __str__(self):
        return self.name


class teams(models.Model):
    name = models.CharField(max_length = 200)
    history = HistoricalRecords()


    class Meta:
        verbose_name_plural = "teams"

    def __str__(self):
        return self.name


class categories(models.Model):
    name = models.CharField(max_length = 200)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


'''This was created to list owners who aren't part of CRM & do not have access to CRM timelines'''
class owners(models.Model):
    name = models.CharField(max_length = 200)
    team = models.ForeignKey(teams, related_name='owners_team', on_delete = models.PROTECT, null=True, blank=True)
    username = models.ForeignKey(User, related_name='owners_username', on_delete = models.PROTECT, null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "owners"

    def __str__(self):
        return self.name

class regions(models.Model):
    name = models.CharField(max_length = 100)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "region"

    def __str__(self):
        return self.name


class weeks(models.Model):
    no = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(54)]) # week number in current year
    # weekly_hours = models.FloatField()

    ops_hours = models.FloatField(default=0, validators=[MinValueValidator(0)])
    ops_capacity = models.FloatField(default=75, validators=[MinValueValidator(1)]) # capacity in hours for the week. Random value 15 to prevent zero-division

    agency_hours = models.FloatField(default=0, validators=[MinValueValidator(0)])
    agency_capacity = models.FloatField(default=75, validators=[MinValueValidator(1)]) # capacity in hours for the week. Random value 15 to prevent zero-division

    analytics_hours = models.FloatField(default=0, validators=[MinValueValidator(0)])
    analytics_capacity = models.FloatField(default=75, validators=[MinValueValidator(1)]) # capacity in hours for the week. Random value 15 to prevent zero-division

    no_campaign = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    # team = models.ForeignKey(teams, on_delete = models.PROTECT) # to calculate RUs by team

    comment = models.TextField(null=True, blank=True)

    last_edited_by = models.ForeignKey(User, related_name='weeks_editor', on_delete = models.PROTECT)
    timestamp_utc = models.DateTimeField(default = timezone.now)

    # objects = models.Manager()

    history = HistoricalRecords()

    @property
    def start_date(self):
        return dt.strptime(str(dt.now().year) + '-' + str(self.no - 1) + '-1', '%Y-%W-%w') # CHANGE year?


    @property
    def today(self):
        return dt.today().isocalendar()[1] == self.no

    @property
    def ops_ru(self):
        return (self.ops_hours / self.ops_capacity)*100

    @property
    def agency_ru(self):
        return (self.agency_hours / self.agency_capacity)*100

    @property
    def analytics_ru(self):
        return (self.analytics_hours / self.analytics_capacity)*100


    class Meta:
        verbose_name_plural = "Resource Utilization"


    def __str__(self):
        return 'Week ' + str(self.no)




class CampaignsManager(models.Manager):
    def get_queryset(self):
        ordered_campaigns = super().get_queryset().filter(status='active').order_by('start', 'name')
        # Filter only tasks associated to active campaigns
        return ordered_campaigns

class campaigns(models.Model):
    name = models.CharField(max_length = 200)
    start = models.DateField()
    end = models.DateField()
    progress = models.ForeignKey(progress, on_delete = models.PROTECT)
    status = models.CharField(max_length = 100) # deleted or active

    region = models.ForeignKey(regions, on_delete = models.PROTECT) # Regional, Ad-Hoc
    vertical = models.ForeignKey(verticals, on_delete = models.PROTECT) # PAX, DAX, FOOD, etc.
    countries = models.CharField(max_length = 200)
    type = models.ForeignKey(types, on_delete = models.PROTECT) # migration, new, template
    phase = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)]) # to define staggered phases
    complexity = models.ForeignKey(complexities, on_delete = models.PROTECT) # high mid low
    platform = models.CharField(max_length = 200)

    jira = models.URLField(max_length = 1000) # JIRA link
    chart = models.URLField(max_length = 1000) # Lucidchart link
    perf = models.URLField(max_length = 1000, null=True, blank=True) # Performance Dash
    monitor = models.URLField(max_length = 1000, null=True, blank=True) # Monitoring Dash

    lcm_owner = models.ForeignKey(owners, related_name = "campaigns_lcm", on_delete = models.PROTECT)
    ops_owner = models.ForeignKey(owners, related_name = "campaigns_ops", on_delete = models.PROTECT)
    analytics_owner = models.ForeignKey(owners, related_name = "campaigns_analytics", on_delete = models.PROTECT)

    # CHANGE? in future perhaps can move these to another model
    no_channels = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    no_comms = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    no_languages = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    no_dynamic_fields = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    no_query_attr = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    ops_hours = models.FloatField(default = 0, validators=[MinValueValidator(0)])
    agency_hours = models.FloatField(default = 0, validators=[MinValueValidator(0)])
    analytics_hours = models.FloatField(default = 0, validators=[MinValueValidator(0)])

    last_edited_by = models.ForeignKey(User, related_name='campaigns_editor', on_delete = models.PROTECT)
    timestamp_utc = models.DateTimeField(default = timezone.now)

    # objects = models.Manager()
    objects = CampaignsManager()

    history = HistoricalRecords() # Historicalcampaigns

    @property
    def days(self):
        holiday_list = [str(date) for date in holidays.objects.values_list('date', flat=True)]
        return np.busday_count(self.start, self.end, weekmask='1111100', holidays=holiday_list)

    @property
    def bar_start(self):
        date_chosen = self.start

        return date_chosen.isocalendar()[1]

    @property
    def bar_end(self):
        date_chosen = self.end

        return date_chosen.isocalendar()[1] + 1

    @property
    def no_countries(self):

        return len(self.countries.split(", "))

    def clean(self):
        if (self.end - self.start).days < 0: # when data is sent from form to backend, noth dates will be populated
            raise ValidationError({'end': ['Campaign end date cannot come before campaign start date: ' + str(self.start)]})

    def save(self, *args, **kwargs):

        prev_ = campaigns.objects.filter(id=self.id)
        editor = self.last_edited_by
        print("check1")

        if len(prev_) > 0: # if exists
            prev = campaigns.objects.get(id=self.id)
            print("check2")

            # Check if dates/RU capacity change, as only these need to be re-calculated:
            if (prev.start != self.start) or (prev.end != self.end) or (prev.ops_hours != self.ops_hours) or (prev.agency_hours != self.agency_hours) or (prev.analytics_hours != self.analytics_hours) or (prev.status != self.status):
                # AFTER comparing prev, can save:
                super(campaigns, self).save(*args, **kwargs) # CAREFUL about indentation! Here we save regardles if it existed before
                print("check3")
                print("RE-CALCULATE")

                # POST SAVE:
                recalculate(editor)
                # Re-calculate RUs - should be re-calculate anytome when task dates change, when ops_hours etc. change.
                # Ignore task-based changes here as it'll be re-caluclated by tasks save logic itself.

            else:
                super(campaigns, self).save(*args, **kwargs) # CAREFUL about indentation! Here we save regardles if it existed before
                # DO NOT place this at th very top although all conditions leade to a super save!!!
                # This is because for some case we need the prev value before it was saved

        else: # If it's clone:
            print("check4")
            super(campaigns, self).save(*args, **kwargs)
            print("RE-CALCULATE")
            recalculate(editor)


    class Meta:
        verbose_name_plural = "campaigns"

    def __str__(self):
        return str(self.id) + ' | ' + self.vertical.name + ' | ' + self.name



class CommentsManager(models.Manager):
    def get_queryset(self):
        latest_comments = super().get_queryset().filter(status='active').order_by('-timestamp_utc', 'commenter')

        return latest_comments # latest comments on top


class comments(models.Model):
    campaign = models.ForeignKey(campaigns, related_name='comments', on_delete = models.CASCADE)
    comment = models.CharField(max_length = 2000)
    commenter = models.ForeignKey(owners, related_name='comments_commenter', null=True, blank=True, on_delete=models.PROTECT)
    # comment_date = models.DateField(default = timezone.now)
    status = models.CharField(max_length = 100, default='active') # deleted or active

    last_edited_by = models.ForeignKey(User, related_name='comments_editor', on_delete = models.PROTECT)
    timestamp_utc = models.DateTimeField(auto_now=True) # default = timezone.now,

    objects = CommentsManager()

    history = HistoricalRecords()

    @property
    def date(self):
        sgt_date = timezone.localtime(self.timestamp_utc, pytz.timezone('Asia/Singapore'))
        return sgt_date

    class Meta:
        verbose_name_plural = "comments"

    # DO NOT CHANGE back to the below:
    # def __str__(self):
        # return self.campaign.name + " | " + self.commenter.name + " | " + str(self.comment_date)


class LinksManager(models.Manager):
    def get_queryset(self):
        latest_links = super().get_queryset().filter(status='active').order_by('name')

        return latest_links

class links(models.Model):
    campaign = models.ForeignKey(campaigns, related_name='links', on_delete = models.CASCADE)
    name = models.CharField(max_length = 100)
    link = models.URLField(max_length = 1000) # Lucidchart link
    status = models.CharField(max_length = 100, default='active') # deleted or active

    last_edited_by = models.ForeignKey(User, related_name='links_editor', on_delete = models.PROTECT)
    timestamp_utc = models.DateTimeField(default = timezone.now)

    objects = LinksManager()

    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "links"


# Validation for task dates based on campaign
# def validate_task_start(self, value):
#     if value < self.campaign.start:
#         raise ValidationError('Task start date cannot come before campaign start date')
#     elif value > self.campaign.end:
#         raise ValidationError('Task start date cannot come after campaign end date')
#     elif (self.end - value) < 0: # when data is sent from form to backend, noth dates will be populated
#         raise ValidationError('Task end date cannot come before task start date')
#
# def validate_task_end(self, value):
#     if value < self.campaign.start:
#         raise ValidationError('Task end date cannot come before campaign start date')
#     elif value > self.campaign.end:
#         raise ValidationError('Task end date cannot come after campaign end date')


class TasksManager(models.Manager):
    def get_queryset(self):
        ordered_tasks = super().get_queryset().filter(campaign__status='active', status='active').order_by('start', 'end', 'name')
        # Filter only tasks associated to active campaigns
        return ordered_tasks


class tasks(models.Model):
    campaign = models.ForeignKey(campaigns, related_name='tasks', on_delete = models.CASCADE)

    name = models.CharField(max_length = 200)
    start = models.DateField()  # DateField(validators=[validate_task_start])
    end = models.DateField() # DateField(validators=[validate_task_end])
    progress = models.ForeignKey(progress, on_delete = models.PROTECT)
    owner = models.ForeignKey(owners, on_delete = models.PROTECT)
    dependency = models.ForeignKey('self', related_name='tasks_dependencies', on_delete = models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length = 100, default='active')
    hours = models.FloatField(null=True, blank=True, default=0, validators=[MinValueValidator(0)])
    category = models.ForeignKey(categories, on_delete = models.PROTECT, default=1)

    last_edited_by = models.ForeignKey(User, related_name='tasks_editor', on_delete = models.PROTECT)
    timestamp_utc = models.DateTimeField(default = timezone.now)

    objects = TasksManager()

    history = HistoricalRecords()

    @property
    def days(self):
        holiday_list = [str(date) for date in holidays.objects.values_list('date', flat=True)]
        return np.busday_count(self.start, self.end, weekmask='1111100', holidays=holiday_list)

    @property
    def bar_start(self):
        date_start = dt.now().date().replace(month=1, day=1)
        date_chosen = self.start

        return date_chosen.isocalendar()[1]

    @property
    def text_start(self):
        date_end = dt.now().date().replace(month=1, day=1)
        date_chosen = self.end - timedelta(days=100)

        return date_chosen.isocalendar()[1]

    @property
    def bar_end(self):
        date_start = dt.now().date().replace(month=1, day=1)
        date_chosen = self.end

        return date_chosen.isocalendar()[1] + 1

    @property
    def version_count(self):
        versions = len(tasks_versions.objects.filter(status='active', task = self))

        return versions

    @property
    def team(self):
        return self.owner.team.name

    # def clean(self):
    #     if self.start < self.campaign.start:
    #         raise ValidationError({'start': ['Task start date cannot come before campaign start date: ' + str(self.campaign.start) ]})
    #     elif self.start > self.campaign.end:
    #         raise ValidationError({'start': ['Task start date cannot come after campaign end date: ' + str(self.campaign.end)]})
    #     elif self.end < self.campaign.start:
    #         raise ValidationError({'end': ['Task end date cannot come before campaign start date: ' + str(self.campaign.start)]})
    #     elif self.end > self.campaign.end:
    #         raise ValidationError({'end': ['Task end date cannot come after campaign end date: ' + str(self.campaign.end)]})
    #     elif (self.end - self.start).days < 0: # when data is sent from form to backend, noth dates will be populated
    #         raise ValidationError({'end': ['Task end date cannot come before task start date: ' + str(self.start)]})


    def save(self, recalculate_type, *args, **kwargs):

        if recalculate_type is None:
            recalculate_type = 'single'

        prev_ = tasks.objects.filter(pk=self.pk)
        editor =  self.last_edited_by

        print("check1")

        if len(prev_) > 0: # if task currently exists
            print("check2")
            prev = tasks.objects.get(pk=self.pk)

            # Change active status for existing tasks versions (not new ones). New ones will default to active
            if prev.status != self.status: # be it set to deleted or restore back to active
                print("check3")
                status = self.status
                # editor = self.last_edited_by

                for task_version in prev.tasks_versions.all():
                    task_version.status = status
                    task_version.last_edited_by = editor

                    task_version.save() # everytime this is called, RU should recalculate

            if (prev.start != self.start) or (prev.end != self.end) or (prev.status != self.status):
                print("check4")
                super(tasks, self).save(*args, **kwargs) # NEVER PUT this at the top, as we need prev values for comparison!

                print("RECALCULATE")
                recalculate_determinant = 1
                # POST SAVE
                # Re-calculate RUs - should be re-calculate anytome when task dates change, when ops_hours etc. change, so just recalculate everytime.
                # if self.owner.team.name == 'Ops': # Each task can only belong to one team # Remove this as a task may change ownership & owners can be from another team, thus affecting the RU by team

                # recalculate_task(editor) DO NOT RE-CALCULATE HERE - it will loop through every single task for cases where campaign dates change and subsequently all task dates change!

            else:
                print("check5")
                super(tasks, self).save(*args, **kwargs) # NEVER PUT this at the top, as we need prev values for comparison!
                recalculate_determinant = 0

        else: # If it's clone
            print("check5")
            super(tasks, self).save(*args, **kwargs)
            recalculate_determinant = 1

        if recalculate_type != 'bulk' and recalculate_determinant == 1: # bulk re-calculation will be done in campaign mode
            recalculate_task(editor)


    class Meta:
        verbose_name_plural = "tasks"

    def __str__(self):
        return self.campaign.name + " | "  + self.name



class TasksVersionsManager(models.Manager):
    def get_queryset(self):
        ordered_tasks = super().get_queryset().filter(status='active').order_by('id')
        # Order by recency
        return ordered_tasks

class tasks_versions(models.Model):
    task = models.ForeignKey(tasks, related_name='tasks_versions', on_delete = models.CASCADE)

    name = models.CharField(max_length = 200)
    start = models.DateField()
    end = models.DateField()
    progress = models.ForeignKey(progress, on_delete = models.PROTECT)
    owner = models.ForeignKey(owners, on_delete = models.PROTECT)
    status = models.CharField(max_length = 100, default='active') # deleted or active # showed on UI
    hours = models.FloatField(null=True, blank=True, default=0, validators=[MinValueValidator(0)])

    last_edited_by = models.ForeignKey(User, related_name='tasks_versions_editor', on_delete = models.PROTECT)
    timestamp_utc = models.DateTimeField(default = timezone.now)

    objects = TasksVersionsManager()

    history = HistoricalRecords()


    @property
    def days(self):
        holiday_list = [str(date) for date in holidays.objects.values_list('date', flat=True)]
        return np.busday_count(self.start, self.end, weekmask='1111100', holidays=holiday_list)

    @property
    def bar_start(self):
        date_start = dt.now().date().replace(month=1, day=1)
        date_chosen = self.start

        return date_chosen.isocalendar()[1]

    @property
    def bar_end(self):
        date_start = dt.now().date().replace(month=1, day=1)
        date_chosen = self.end

        return date_chosen.isocalendar()[1] + 1

    @property
    def team(self):
        return self.owner.team.name


    class Meta:
        verbose_name_plural = "Tasks Versions"

    def __str__(self):
        return self.task.campaign.name + " | " + self.task.owner.team.name + " | "  + self.task.name + " | "  + self.name


class TasksCommentsManager(models.Manager):
    def get_queryset(self):
        latest_comments = super().get_queryset().filter(status='active').order_by('-timestamp_utc', 'commenter')

        return latest_comments # latest comments on top

class tasks_comments(models.Model):
    task = models.ForeignKey(tasks, related_name='tasks_comments', on_delete = models.CASCADE)
    comment = models.CharField(max_length = 2000)
    commenter = models.ForeignKey(owners, related_name='tasks_comments_commenter', on_delete=models.PROTECT)
    # comment_date = models.DateField() # Allow user to update comment without changing timestamp
    status = models.CharField(max_length = 100, default='active') # deleted or active

    last_edited_by = models.ForeignKey(User, related_name='tasks_comments_editor', on_delete = models.PROTECT)
    timestamp_utc = models.DateTimeField(auto_now=True) # default = timezone.now,

    objects = TasksCommentsManager()

    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "Task comments"

    def __str__(self):
        return str(self.task.id) + " | " + self.task.campaign.name + " | " + self.task.name + " | "  + self.commenter.name
