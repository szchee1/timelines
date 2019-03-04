from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import locks, holidays, progress, verticals, types, countries, platforms, complexities, teams, categories, owners, regions, weeks, campaigns, comments, links, tasks, tasks_versions, tasks_comments
from django.core.serializers import serialize
from django.db.models import Q

import pandas as pd
import numpy as np
import itertools
import json
from datetime import datetime as dt, timezone, timedelta
import copy

year = 2019 # CHANGE to be scalable
vertical_list = verticals.objects.order_by('name').values('id', 'name').distinct()
type_list = types.objects.order_by('name').values('id', 'name').distinct()
complexity_list = json.dumps(list(complexities.objects.order_by('name').values('id', 'name').distinct()))
progress_list = progress.objects.order_by('name').values('id', 'name').distinct()
country_list = countries.objects.order_by('name').values('id', 'name').distinct()
platform_list = platforms.objects.order_by('name').values('id', 'name').distinct()
team_list = json.dumps(list(teams.objects.order_by('name').values('id', 'name').distinct()))

owner_list = owners.objects.order_by('name').values('id', 'name').distinct()
category_list = categories.objects.order_by('name').values('id', 'name').distinct()
owner_lcm_list = owners.objects.filter(team__name = 'LCM').order_by('name').values('id', 'name').distinct()
owner_ops_list = owners.objects.filter(team__name = 'Ops').order_by('name').values('id', 'name').distinct()
owner_analytics_list = owners.objects.filter(team__name = 'Analytics').order_by('name').values('id', 'name').distinct()

week_list = weeks.objects.order_by('no')

@login_required(login_url="login")
def home(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active').order_by('progress', 'vertical__name', 'type', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)


def campaign(request, campaignid):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', id=campaignid) #.order_by('progress', 'vertical__name', 'type', 'name')
    campaign_week_start = campaign_list.values_list('start', flat=True)[0].isocalendar()[1]
    campaign_week_end = campaign_list.values_list('end', flat=True)[0].isocalendar()[1]

    # week_list = weeks.objects.filter(no__gte = campaign_week_start , no__lte = campaign_week_end).order_by('no')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/campaign.html", data)


def campaign_type(request, campaigntype, campaignid):

    type = campaigntype.title()
    print(type)
    print(campaignid)
    if type == 'Template':
        campaign_list = campaigns.objects.filter(status='active', type__name='Template', id=campaignid) #.order_by('progress', 'vertical__name', 'name', 'id')

    elif type in ['Migration', 'New', 'Troubleshooting']:
        campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', id=campaignid, type__name=type) #.order_by('progress', 'vertical__name', 'type', 'name')

    else:
        campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', id=campaignid, vertical__name=type.upper()) #.order_by('progress', 'vertical__name', 'type', 'name')
        print(campaign_list)


    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/campaign.html", data)


def pax(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', vertical__name='PAX').order_by('progress', 'type', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)

def dax(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', vertical__name='DAX').order_by('progress', 'type', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)

def food(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', vertical__name='FOOD').order_by('progress', 'type', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)

def financial(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', vertical__name='FINANCIAL').order_by('progress', 'type', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)


def ventures(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', vertical__name='VENTURES').order_by('progress', 'type', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)

def new(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', type__name='New').order_by('progress', 'vertical__name', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)

def migration(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', type__name='Migration').order_by('progress', 'vertical__name', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)

def troubleshooting(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active', type__name='Troubleshooting').order_by('progress', 'vertical__name', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)

def template(request):
    campaign_list = campaigns.objects.filter(status='active', type__name='Template').order_by('progress', 'vertical__name', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/home.html", data)

def edit_week(request):
    if request.method == 'POST':
        request_post = request.POST
        weekid = int(request_post.get('weekid'))

        # Below is not necessary due to the method a new campaign is created:
        # if campaignid == 0:
        #     message = "New campaign created"
        #     print(message)
        #     response = 1

        # else:
        w = weeks.objects.get(id = weekid)
        print(w)
        print(weekid)
        lock_ = locks.objects.filter(type = 'week', identifier = weekid).order_by('-timestamp_utc')

        if len(lock_) > 0: # If lock records exist
            lock = lock_.first() # Most recent lock for this campaign
            print(lock)
            print(lock.status)

            time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
            print(time_diff_hours)

        else:
            time_diff_hours = 1000 # very first lock


        if time_diff_hours > 0.25: # 15 mins or new lock, as forms are short
            # release current campaign for editing
            # This happens in the event another user clicks edit but never saves
            locks.objects.create(
                user = request.user,
                type = 'week',
                identifier = weekid,
                status = 'locked'
            )

            response = 2
            message = str(request.user) + " is now editing"
            print(message)


        else: # time_diff_hours <= 30 mins
            if lock.status == 'locked':
                # Provide option for lock owner to release so fellow users can edit
                if lock.user == request.user:
                    response = 3
                    message = "WARNING: " + str(lock.user) + ", you have previously edited resource capacity for Week " + str(w.no) + " but not saved. You could possibly have this opened in edit mode on another window or refreshed the page without saving. Please ensure you do not have unsaved changes on another window before proceeding."
                    print(message)

                else:
                    message = str(lock.user) + " is currently editing resource capacity for Week " + str(w.no)
                    print(message)
                    response = 0


            else: # create new lock session
                locks.objects.create(
                    user = request.user,
                    type = 'week',
                    identifier = weekid,
                    status = 'locked'
                )

                message = "Resource capacity for Week " + str(w.no) + " is locked for you to edit"
                print(message)
                response = 1


        data = {
            'code': response,
            'message': message
        }

        return JsonResponse(data)


def edit_campaign_info(request):
    if request.method == 'POST':
        request_post = request.POST
        campaignid = int(request_post.get('campaignid'))
        edit_type = request_post.get('type')

        edit_type_text = ''

        if edit_type == 'campaign-info':
            edit_type_text = 'Background'
        elif edit_type == 'campaign-quantifiers':
            edit_type_text = 'Quantifiers'
        elif edit_type in ['jira', 'chart', 'perf', 'monitor']:
            edit_type_text = edit_type
        # elif edit_type == 'chart':
        #     edit_type_text = 'Lucidchart'

        campaign = campaigns.objects.get(id = campaignid)

        lock_ = locks.objects.filter(type = edit_type, identifier = campaignid).order_by('-timestamp_utc')

        # Below is not necessary due to the method a new campaign is created:
        # if campaignid == 0:
        #     message = "New campaign created"
        #     print(message)
        #     response = 1

        if len(lock_) > 0: # If lock records exist
            lock = lock_.first() # Most recent lock for this campaign
            print(lock)
            print(lock.status)

            time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
            print(time_diff_hours)

        else:
            time_diff_hours = 1000 # very first lock

        if time_diff_hours > 0.25: # 15 mins or new lock, as forms are short
            # release current campaign for editing
            # This happens in the event another user clicks edit but never saves
            locks.objects.create(
                user = request.user,
                type = edit_type,
                identifier = campaignid,
                status = 'locked'
            )

            response = 2
            message = str(request.user) + " is now editing"
            print(message)


        else: # time_diff_hours <= 30 mins
            if lock.status == 'locked':
                # Provide option for lock owner to release so fellow users can edit
                if lock.user == request.user:
                    response = 3
                    message = "WARNING: " + str(lock.user) + ", you have previously edited " + str(campaign.name) + ": " + edit_type_text + ", but not saved. You could possibly have this opened in edit mode on another window or refreshed the page without saving. Please ensure you do not have unsaved changes on another window before proceeding."
                    print(message)

                else:
                    message = str(lock.user) + " is currently editing " + str(campaign.name) + ": " + edit_type_text
                    print(message)
                    response = 0


            else: # create new lock session
                locks.objects.create(
                    user = request.user,
                    type = edit_type,
                    identifier = campaignid,
                    status = 'locked'
                )

                message = str(campaign.name) + ": " + edit_type_text + " is locked for you to edit"
                print(message)
                response = 1


    data = {
        'code': response,
        'message': message
    }

    return JsonResponse(data)


def edit_campaign(request):
    if request.method == 'POST':
        request_post = request.POST
        campaignid = int(request_post.get('campaignid'))

        # Below is not necessary due to the method a new campaign is created:
        # if campaignid == 0:
        #     message = "New campaign created"
        #     print(message)
        #     response = 1

        # else:
        campaign = campaigns.objects.get(id = campaignid)
        print(campaign)
        print(campaignid)
        lock_ = locks.objects.filter(type = 'campaign', identifier = campaignid).order_by('-timestamp_utc').first()

        taskids = list(campaign.tasks.values_list("id", flat=True)) # get task locks associated with campaign
        fifteen_mins_ago = dt.now(timezone.utc) - timedelta(hours=0.25)

        lock2_ = locks.objects.filter(type = 'task', identifier__in = taskids, timestamp_utc__gte = fifteen_mins_ago).order_by('identifier', '-timestamp_utc')

        lock2 = []
        lock_users = []
        lock_nos = []

        for lock in lock2_:
            lock_status = lock.status
            lock_no = lock.identifier

            if lock_no not in lock_nos: # get max lock status by task
                lock2.append(lock_status)
                lock_users.append(lock.user.username)
                lock_nos.append(lock_no)

        # lock2 = list(lock2_.values_list('status', flat=True))

        # if len(lock_) > 0: # If lock records exist
        #     lock = lock_.first() # Most recent lock for this campaign
        #     print(lock)
        #     print(lock.status)
        #
        #     time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
        #     print(time_diff_hours)
        #
        # elif len(lock2) > 0: # If lock records exist
        #     lock = lock2.first() # Most recent lock for this campaign
        #     print(lock)
        #     print(lock.status)
        #
        #     time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
        #     print(time_diff_hours)


        if lock_ is None:
            locks.objects.create(
                user = request.user,
                type = 'campaign',
                identifier = campaignid,
                status = 'locked'
            )

            time_diff_hours = 1000

            message = str(campaign.name) + " is locked for you to edit"
            print(message)
            response = 1

        elif lock_.status == 'locked':
            user = lock_.user
            time_diff_hours = ((dt.now(timezone.utc) - lock_.timestamp_utc).seconds)/3600
            print(time_diff_hours)

            if time_diff_hours > 0.25: # 15 mins or new lock, as forms are short
                # release current campaign for editing
                # This happens in the event another user clicks edit but never saves
                locks.objects.create(
                    user = request.user,
                    type = 'campaign',
                    identifier = campaignid,
                    status = 'locked'
                )

                response = 2
                message = str(request.user) + " is now editing"
                print(message)


            else: # time_diff_hours <= 30 mins & locked
                # if lock.status == 'locked':
                # Provide option for lock owner to release so fellow users can edit
                if user == request.user:
                    response = 3
                    message = "WARNING: " + str(lock_.user) + ", you have previously edited " + str(campaign.name) + " but not saved. You could possibly have this opened in edit mode on another window or refreshed the page without saving. Please ensure you do not have unsaved changes on another window before proceeding."
                    print(message)

                else:
                    message = str(user) + " is currently editing " + str(campaign.name)
                    print(message)
                    response = 0


        elif 'locked' in lock2:
            user = ', '.join(set(lock_users))   #(list(set(lock2_.values_list('user__username', flat=True))))
            # time_diff_hours = 0.25 # these were tasks from 15 mins ago

            message = "These users are currently editing " + str(campaign.name) + ": " + user
            print(message)
            response = 0

        else:
            time_diff_hours = 1000 # very first lock/released

            # else: # create new lock session
            locks.objects.create(
                user = request.user,
                type = 'campaign',
                identifier = campaignid,
                status = 'locked'
            )

            message = str(campaign.name) + " is locked for you to edit"
            print(message)
            response = 1


        data = {
            'code': response,
            'message': message
        }

        return JsonResponse(data)


def save_week(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        weekid = int(request_post.get('weekid'))

        ops_capacity = request_post.get('ops_capacity')
        agency_capacity = request_post.get('agency_capacity')
        analytics_capacity = request_post.get('analytics_capacity')
        comment = request_post.get('comment')


        if weekid > 0:
            w0 = weeks.objects.filter(id=weekid)

            for changes in w0:
                # Values are 'updated'.
                # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                changes.ops_capacity = ops_capacity
                changes.agency_capacity = agency_capacity
                changes.analytics_capacity = analytics_capacity
                changes.comment = comment

                changes.last_edited_by = request_user

                changes.save()

            w = weeks.objects.get(id=weekid)

        # THIS SHOULD NEVER HAPPEN due to the way new campaigns are created
        # else:
        #     c = campaigns.objects.create(
        #         ops_hours = ops_hours,
        #         agency_hours = agency_hours,
        #         analytics_hours = analytics_hours,
        #         last_edited_by = request_user
        #     )

    # lock for managing concurrent edits
    # For new edits it would just create a new entry
    # For existing edits it would "release" the campaign for editing
    locks.objects.create(
        user = request_user,
        type = 'week',
        identifier = w.id, # Be careful not to use campaignid! As the default for new campaigns is 0
        status = 'released'
    )

    return HttpResponse("Week " + str(w.no) + ": weekly capacity saved!")



def save_campaign(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        campaignid = int(request_post.get('campaignid'))
        prev = campaigns.objects.get(id=campaignid)
        # task_min = min(list(prev.tasks.values_list('start', flat=True)))
        # task_max = max(list(prev.tasks.values_list('end', flat=True)))

        # print(task_min)
        # print(task_max)

        name = request_post.get('name')
        type_val = request_post.get('type')
        vertical_val = request_post.get('vertical')
        progress_val = request_post.get('progress')
        date_type = request_post.get('date_type')
        print(date_type)
        date = request_post.get('date')
        print(date)
        date_ = dt.strptime(date, '%Y-%m-%d').date()
        # start = request_post.get('start')
        # end = request_post.get('end')
        # start_ = dt.strptime(start, '%Y-%m-%d').date()
        # end_ = dt.strptime(end, '%Y-%m-%d').date()
        countries = request_post.get('countries')[:-2]
        # shift_type = request_post.get('shift')
        current_url = request_post.get('current_url')

        tp = types.objects.get(id = type_val)
        p = progress.objects.get(id = progress_val)
        v = verticals.objects.get(id = vertical_val)

        holiday_list = [str(date) for date in holidays.objects.values_list('date', flat=True)]


        if date_.year != year:
            message = "Campign date (" + date + ") is beyond current year (" + str(year) + ")!"
            redirect = 0

        elif date_type is None or date_type == '0':
            message = "Date field cannot be empty!"
            redirect = 0

        # if start_.year != year:
        #     message = "Campign START date (" + start + ") is beyond current year (" + str(year) + ")!"
        #     redirect = 0
        #
        # elif end_.year != year:
        #      message = "Campign END date (" + end + ") is beyond current year (" + str(year) + ")!"
        #      redirect = 0

        # !!!! UI should only limit - either start OR end but not both!

        # elif (start_ > task_min) or (start_ > task_min) or (end_ < task_max) or (end_ < task_min):
        #     # This rule kinda means a campaign can be delayed, but if it were to be brought forward, owners have to adjust tasks individually
        #
        # # There shouldn't be a case where prev.start > task_max, etc.
        # # as checks should work to prevent task_min > task_max
        # # but just put in case
        #
        #     message = "Campaign dates are outside of the min & max tasks date range (" +  task_min.strftime('%Y-%m-%d') + " to " + task_max.strftime('%Y-%m-%d') + "). Please change the dates."
        #     redirect = 0

        # elif prev.end < prev.start:
        #     message = "Campaign END date ( " + prev.end.strftime('%Y-%m-%d') + " ) cannot be greater than campign START date (" + prev.start.strftime('%Y-%m-%d') + ")!"
        #     redirect = 0


        elif campaignid > 0:
            c0 = campaigns.objects.filter(id=campaignid)

            # if shift_type == '1':
            recalculate_type = 'bulk'

            # Campaign dates check
            # if (prev.start != start_) and (prev.end != end_):
            #     print("DIFF DATES 1")
            #     diff_start = np.busday_count(prev.start, start, weekmask='1111100', holidays=holiday_list)
            #     diff_end = np.busday_count(prev.end, end, weekmask='1111100', holidays=holiday_list)
            #
            #     for task in prev.tasks.all():
            #         task.start = np.busday_offset(task.start, diff_start, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # += timedelta(days=diff_start)
            #         task.end = np.busday_offset(task.end, diff_end, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # += timedelta(days=diff_end)
            #         task.last_edited_by = request_user
            #
            #         task.save(recalculate_type) # everytime this is called, RU should recalculate


            if date_type == 'start':
                start = date
                start_ = date_

                if prev.start != start_:
                    print("DIFF DATES 2")
                    diff = np.busday_count(prev.start, start, weekmask='1111100', holidays=holiday_list)

                    for task in prev.tasks.all():
                        t_start = task.start
                        task.start = np.busday_offset(t_start, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # task.start + timedelta(days=diff)

                        t_end = task.end
                        task.end = np.busday_offset(t_end, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt)

                        task.last_edited_by = request_user

                        task.save(recalculate_type) # everytime this is called, RU should recalculate


                    for changes in c0:
                        # Values are 'updated'.
                        # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                        changes.name = name
                        changes.type = tp
                        changes.vertical = v
                        changes.progress = p
                        changes.start = start
                        changes.end = np.busday_offset(prev.end, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt)
                        changes.countries = countries

                        changes.last_edited_by = request_user

                        changes.save() # This saev method shoud also perform the bulk re-calculation of weekly RUs

                    c = campaigns.objects.get(id=campaignid)

                else: # no change in date
                    for changes in c0:
                        # Values are 'updated'.
                        # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                        changes.name = name
                        changes.type = tp
                        changes.vertical = v
                        changes.progress = p
                        # changes.start = start
                        # changes.end = np.busday_offset(prev.end, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt)
                        changes.countries = countries

                        changes.last_edited_by = request_user

                        changes.save() # This saev method shoud also perform the bulk re-calculation of weekly RUs

                    c = campaigns.objects.get(id=campaignid)



            elif date_type == 'end':
                end = date
                end_ = date_

                if prev.end != end_:
                    print("DIFF DATES 3")
                    diff = np.busday_count(prev.end, end, weekmask='1111100', holidays=holiday_list)

                    for task in prev.tasks.all():
                        t_start = task.start
                        task.start = np.busday_offset(t_start, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # task.start + timedelta(days=diff)

                        t_end = task.end
                        task.end = np.busday_offset(t_end, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt)

                        task.last_edited_by = request_user

                        task.save(recalculate_type) # everytime this is called, RU should recalculate


                    for changes in c0:
                        # Values are 'updated'.
                        # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                        changes.name = name
                        changes.type = tp
                        changes.vertical = v
                        changes.progress = p
                        changes.start = np.busday_offset(prev.start, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt)
                        changes.end = end
                        changes.countries = countries

                        changes.last_edited_by = request_user

                        changes.save() # This saev method shoud also perform the bulk re-calculation of weekly RUs

                    c = campaigns.objects.get(id=campaignid)


                else:
                    for changes in c0:
                        # Values are 'updated'.
                        # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                        changes.name = name
                        changes.type = tp
                        changes.vertical = v
                        changes.progress = p
                        # changes.start = np.busday_offset(prev.start, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt)
                        # changes.end = end
                        changes.countries = countries

                        changes.last_edited_by = request_user

                        changes.save() # This saev method shoud also perform the bulk re-calculation of weekly RUs

                    c = campaigns.objects.get(id=campaignid)

            # else:
            #     recalculate_type = 'single'




            # WARNING DO NOT ENABLE THIS - current form setup shouldn't result in campaignid == 0
            # If it's enabled may accidentally create a new campaign!
            # else:
            #     c = campaigns.objects.create(
            #         name = name,
            #         type = tp,
            #         vertical = v,
            #         progress = p,
            #         start = start,
            #         end = end,
            #         last_edited_by = request_user
            #     )

            # lock for managing concurrent edits
            # For new edits it would just create a new entry
            # For existing edits it would "release" the campaign for editing
            locks.objects.create(
                user = request_user,
                type = 'campaign',
                identifier = c.id, # Be careful not to use campaignid! As the default for new campaigns is 0
                status = 'released'
            )

            url_split = list(filter(None, current_url.split("/")))
            print(url_split)
            print(url_split[1])

            vertical_list2 = list(vertical_list.values_list('name', flat=True))
            type_list2 = list(type_list.values_list('name', flat=True))

            print(vertical_list2)

            if len(url_split) > 2:
                if url_split[1].upper() in vertical_list2:
                    redirect = '/timelines/' + str(c.vertical.name.lower()) + '/' + str(c.id)

                elif url_split[1].title() in type_list2:
                    redirect = '/timelines/' + str(c.type.name.lower()) + '/' + str(c.id)

            else:
                redirect = '/timelines/' + str(c.id)

            print(redirect)

            message = name + " campaign saved!"


            # else: # shiftType == '0':


        data = {
            'redirect': redirect,
            'message': message
        }

        return JsonResponse(data)




def save_campaign_info(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        campaignid = int(request_post.get('campaignid'))
        phase = request_post.get('phase')
        complexity = request_post.get('complexity')
        lcm_owner = request_post.get('lcm_owner')
        ops_owner = request_post.get('ops_owner')
        analytics_owner = request_post.get('analytics_owner')
        platform = request_post.get('platform')[:-2]
        print(platform)

        cp = complexities.objects.get(id = complexity)
        lcm = owners.objects.get(id = lcm_owner)
        ops = owners.objects.get(id = ops_owner)
        analytics = owners.objects.get(id = analytics_owner)


        if campaignid > 0:
            c0 = campaigns.objects.filter(id=campaignid)

            for changes in c0:
                # Values are 'updated'.
                # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                changes.phase = phase
                changes.complexity = cp
                changes.lcm_owner = lcm
                changes.ops_owner = ops
                changes.analytics_owner = analytics
                changes.platform = platform
                changes.last_edited_by = request_user

                changes.save()

            c = campaigns.objects.get(id=campaignid)

        # THIS SHOULD NEVER HAPPEN due to the way new campaigns are created
        # else:
        #     c = campaigns.objects.create(
        #         phase = phase,
        #         complexity = cp,
        #         lcm_owner = lcm,
        #         ops_owner = ops,
        #         analytics_owner = analytics,
        #         platform = platform,
        #         last_edited_by = request_user
        #     )

    # lock for managing concurrent edits
    # For new edits it would just create a new entry
    # For existing edits it would "release" the campaign for editing
    locks.objects.create(
        user = request_user,
        type = 'campaign-info',
        identifier = c.id, # Be careful not to use campaignid! As the default for new campaigns is 0
        status = 'released'
    )

    return HttpResponse(c.name + " campaign Info saved!")


def save_campaign_capacity(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        campaignid = int(request_post.get('campaignid'))

        ops_hours = request_post.get('ops_hours')
        agency_hours = request_post.get('agency_hours')
        analytics_hours = request_post.get('analytics_hours')

        if campaignid > 0:
            c0 = campaigns.objects.filter(id=campaignid)

            for changes in c0:
                # Values are 'updated'.
                # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                changes.ops_hours = ops_hours
                changes.agency_hours = agency_hours
                changes.analytics_hours = analytics_hours

                changes.last_edited_by = request_user

                changes.save()

            c = campaigns.objects.get(id=campaignid)

        # THIS SHOULD NEVER HAPPEN due to the way new campaigns are created
        # else:
        #     c = campaigns.objects.create(
        #         ops_hours = ops_hours,
        #         agency_hours = agency_hours,
        #         analytics_hours = analytics_hours,
        #         last_edited_by = request_user
        #     )

    # lock for managing concurrent edits
    # For new edits it would just create a new entry
    # For existing edits it would "release" the campaign for editing
    locks.objects.create(
        user = request_user,
        type = 'campaign',
        identifier = c.id, # Be careful not to use campaignid! As the default for new campaigns is 0
        status = 'released'
    )

    return HttpResponse(c.name + ": Team RUs saved!")


def save_campaign_quantifiers(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        campaignid = int(request_post.get('campaignid'))

        no_channels = int(request_post.get('no_channels'))
        no_comms = int(request_post.get('no_comms'))
        no_languages = int(request_post.get('no_languages'))
        no_dynamic = int(request_post.get('no_dynamic'))
        no_query_attr = int(request_post.get('no_query_attr'))

        if campaignid > 0:
            c0 = campaigns.objects.filter(id=campaignid)

            for changes in c0:
                # Values are 'updated'.
                # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                changes.no_channels = no_channels
                changes.no_comms = no_comms
                changes.no_languages = no_languages
                changes.no_dynamic_fields = no_dynamic
                changes.no_query_attr = no_query_attr

                changes.last_edited_by = request_user

                changes.save()

            c = campaigns.objects.get(id=campaignid)

        # THIS SHOULD NEVER HAPPEN due to the way new campaigns are created
        # else:
        #     c = campaigns.objects.create(
        #         ops_hours = ops_hours,
        #         agency_hours = agency_hours,
        #         analytics_hours = analytics_hours,
        #         last_edited_by = request_user
        #     )

    # lock for managing concurrent edits
    # For new edits it would just create a new entry
    # For existing edits it would "release" the campaign for editing
    locks.objects.create(
        user = request_user,
        type = 'campaign-quantifiers',
        identifier = c.id, # Be careful not to use campaignid! As the default for new campaigns is 0
        status = 'released'
    )

    return HttpResponse(c.name + ": campaign Quantifiers saved!")


def save_campaign_link(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        campaignid = int(request_post.get('campaignid'))
        link = request_post.get('link')
        type = request_post.get('type')

        if campaignid > 0:
            c0 = campaigns.objects.filter(id=campaignid)

            if type == "jira":

                for changes in c0:
                    # Values are 'updated'.
                    # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                    changes.jira = link

                    changes.last_edited_by = request_user

                    changes.save()

            elif type == "chart":

                for changes in c0:
                    # Values are 'updated'.
                    # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                    changes.chart = link

                    changes.last_edited_by = request_user

                    changes.save()

            elif type == "perf":

                for changes in c0:
                    # Values are 'updated'.
                    # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                    changes.perf = link

                    changes.last_edited_by = request_user

                    changes.save()

            elif type == "monitor":

                for changes in c0:
                    # Values are 'updated'.
                    # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                    changes.monitor = link

                    changes.last_edited_by = request_user

                    changes.save()

            c = campaigns.objects.get(id=campaignid)

        # THIS SHOULD NEVER HAPPEN due to the way new campaigns are created
        # else:
        #     c = campaigns.objects.create(
        #         ops_hours = ops_hours,
        #         agency_hours = agency_hours,
        #         analytics_hours = analytics_hours,
        #         last_edited_by = request_user
        #     )

    # lock for managing concurrent edits
    # For new edits it would just create a new entry
    # For existing edits it would "release" the campaign for editing
    locks.objects.create(
        user = request_user,
        type = type,
        identifier = c.id, # Be careful not to use campaignid! As the default for new campaigns is 0
        status = 'released'
    )

    return HttpResponse(type.title() + " link saved!")


def edit_task(request):
    if request.method == 'POST':
        request_post = request.POST
        taskid = int(request_post.get('taskid'))
        campaignid = int(request_post.get('campaignid'))

        if taskid == 0:
            message = "New task created" # campaign start/end dates should change
            print(message)
            response = 1

        else:
            task = tasks.objects.get(id = taskid)
            print(task)
            print(taskid)

            lock_ = locks.objects.filter(type = 'task', identifier = taskid).order_by('-timestamp_utc').first()
            lock2 = locks.objects.filter(type = 'campaign', identifier = campaignid).order_by('-timestamp_utc').first() # do not allow task edit if campaign is in edit mode

            # if len(lock_) > 0: # If lock records exist
            #     lock = lock_.first() # Most recent lock for this campaign
            #     print(lock)
            #     print(lock.status)
            #
            #     time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
            #     print(time_diff_hours)
            #
            # elif len(lock2) > 0: # If campaign is being edited
            #     lock = lock2.first() # Most recent lock for this campaign
            #     print(lock)
            #     print(lock.status)
            #
            #     time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
            #     print(time_diff_hours)


            if lock_ is None:
                locks.objects.create(
                    user = request.user,
                    type = 'campaign',
                    identifier = campaignid,
                    status = 'locked'
                )

                message = str(task.name) + " is locked for you to edit"
                print(message)
                response = 1

                time_diff_hours = 1000


            elif lock_.status == 'locked':
                lock = lock_
                time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
                print(time_diff_hours)

            elif lock2.status == 'locked':
                lock = lock2
                time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
                print(time_diff_hours)

            else:
                time_diff_hours = 1000 # very first lock


            if time_diff_hours > 0.25: # 15 mins or new lock, as forms are short
                # release current campaign for editing
                # This happens in the event another user clicks edit but never saves
                locks.objects.create(
                    user = request.user,
                    type = 'task',
                    identifier = taskid,
                    status = 'locked'
                )

                response = 2
                message = str(request.user) + " is now editing"
                print(message)


            else: # time_diff_hours <= 30 mins
                if lock.status == 'locked':
                    # Provide option for lock owner to release so fellow users can edit
                    if lock.user == request.user:
                        response = 3
                        message = "WARNING: " + str(lock.user) + ", you have previously edited " + str(task.name) + " but not saved. You could possibly have this opened in edit mode on another window or refreshed the page without saving. Please ensure you do not have unsaved changes on another window before proceeding."
                        print(message)

                    else:
                        message = str(lock.user) + " is currently editing " + str(task.name)
                        print(message)
                        response = 0


                else: # create new lock session
                    locks.objects.create(
                        user = request.user,
                        type = 'task',
                        identifier = taskid,
                        status = 'locked'
                    )

                    message = str(task.name) + " is locked for you to edit"
                    print(message)
                    response = 1


        data = {
            'code': response,
            'message': message
        }

        return JsonResponse(data)


def edit_task_version(request):
    if request.method == 'POST':
        request_post = request.POST
        taskid = int(request_post.get('taskid'))

        if taskid == 0: # technically this would not happen due to the structureof the html
            message = "New task version created"
            print(message)
            response = 1

        else:
            task = tasks_versions.objects.get(id = taskid)
            print(task)
            print(taskid)
            lock_ = locks.objects.filter(type = 'task_version', identifier = taskid).order_by('-timestamp_utc')

            if len(lock_) > 0: # If lock records exist
                lock = lock_.first() # Most recent lock for this campaign
                print(lock)
                print(lock.status)

                time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
                print(time_diff_hours)

            else:
                time_diff_hours = 1000 # for very first lock


            if time_diff_hours > 0.25: # 15 mins or new lock, as forms are short
                # release current campaign for editing
                # This happens in the event another user clicks edit but never saves
                locks.objects.create(
                    user = request.user,
                    type = 'task_version',
                    identifier = taskid,
                    status = 'locked'
                )

                response = 2
                message = str(request.user) + " is now editing"
                print(message)


            else: # time_diff_hours <= 30 mins
                if lock.status == 'locked':
                    # Provide option for lock owner to release so fellow users can edit
                    if lock.user == request.user:
                        response = 3
                        message = "WARNING: " + str(lock.user) + ", you have previously edited " + str(task.name) + " but not saved. You could possibly have this opened in edit mode on another window or refreshed the page without saving. Please ensure you do not have unsaved changes on another window before proceeding."
                        print(message)

                    else:
                        message = str(lock.user) + " is currently editing " + str(task.name)
                        print(message)
                        response = 0


                else: # create new lock session
                    locks.objects.create(
                        user = request.user,
                        type = 'task_version',
                        identifier = taskid,
                        status = 'locked'
                    )

                    message = str(task.name) + " is locked for you to edit"
                    print(message)
                    response = 1


        data = {
            'code': response,
            'message': message
        }

        return JsonResponse(data)


def save_task(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        taskid = int(request_post.get('taskid'))
        print(taskid)
        campaignid = int(request_post.get('campaignid'))

        name = request_post.get('name')
        print(name)
        category_val = request_post.get('category')
        progress_val = request_post.get('progress')
        start = request_post.get('start')
        end = request_post.get('end')
        owner = request_post.get('owner')

        cat = categories.objects.get(id = category_val)
        p = progress.objects.get(id = progress_val)
        o = owners.objects.get(id = owner)

        campaign_prev = campaigns.objects.get(id=campaignid)

        recalculate_type = 'bulk' # change to bulk as campaign save method is called ultimately in this function

        # if start < campaign_start  or end < campaign_start or start > campaign_end or end > campaign_end:
        #     message = "Task dates are out of campaign range."


        if taskid > 0:
            # Validation:
            task = tasks.objects.get(id=taskid)
            # campaign_start = task.campaign.start
            # campaign_end = task.campaign.end

            t0 = tasks.objects.filter(id=taskid)

            for changes in t0:
                # Values are 'updated'.
                # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                changes.name = name
                changes.category = cat
                changes.progress = p
                changes.start = start
                changes.end = end
                changes.owner = o

                changes.last_edited_by = request_user

                changes.save(recalculate_type)

            t = tasks.objects.get(id=taskid)


        else:
            campaignid = int(request_post.get('campaignid'))
            c = campaigns.objects.get(id = campaignid)

            t = tasks (
                campaign = c,
                name = name,
                category = cat,
                progress = p,
                start = start,
                end = end,
                owner = o,
                last_edited_by = request_user
            )

            t.save(recalculate_type)


        version_data = json.loads(request_post.get('versions'))
        print(version_data)

        if len(version_data) - 2 > 0:

            for j in range(len(version_data) - 2):
                task_name = version_data[str(j)]["name"]
                task_progress = version_data[str(j)]["progress"]
                task_start = version_data[str(j)]["start"]
                task_end = version_data[str(j)]["end"]
                task_owner = version_data[str(j)]["owner"]

                t_p = progress.objects.get(id = task_progress)
                t_o = owners.objects.get(id = task_owner)

                tv = tasks_versions.objects.create(
                    task = t,
                    name = task_name,
                    progress = t_p,
                    start = task_start,
                    end = task_end,
                    owner = t_o,
                    last_edited_by = request_user
                )


        # "re-calculate campaign start & end, and RUs"
        # can optimise in future to only re-calculate when there's a change in dates
        task_min = min(list(campaign_prev.tasks.values_list('start', flat=True)))
        task_max = max(list(campaign_prev.tasks.values_list('end', flat=True)))

        print(task_min)
        print(task_max)

        c0 = campaigns.objects.filter(id=campaignid)

        for changes in c0:
            # Values are 'updated'.
            # Using this method instead of direct 'update' call so `simple-history` is able to log updates
            changes.start = task_min
            changes.end = task_max

            changes.last_edited_by = request_user

            changes.save() # This save method shoud also perform the bulk re-calculation of weekly RUs

        # c = campaigns.objects.get(id=campaignid)

    # lock for managing concurrent edits
    # For new edits it would just create a new entry
    # For existing edits it would "release" the campaign for editing
    locks.objects.create(
        user = request.user,
        type = 'task',
        identifier = t.id, # Be careful not to use taskid! As the default for new campaigns is 0
        status = 'released'
    )

    return HttpResponse(name + " saved!")


def save_task_adjust(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        campaignid = int(request_post.get('campaignid'))
        taskid = int(request_post.get('taskid'))
        name = request_post.get('name')
        campaign_prev = campaigns.objects.get(id=campaignid)
        prev = tasks.objects.get(id=taskid)

        name = request_post.get('name')
        category_val = request_post.get('category')
        progress_val = request_post.get('progress')
        start = request_post.get('start')
        end = request_post.get('end')
        start_ = dt.strptime(start, '%Y-%m-%d').date()
        end_ = dt.strptime(end, '%Y-%m-%d').date()
        owner = request_post.get('owner')

        cat = categories.objects.get(id = category_val)
        p = progress.objects.get(id = progress_val)
        o = owners.objects.get(id = owner)

        holiday_list = [str(date) for date in holidays.objects.values_list('date', flat=True)]
        c0 = campaigns.objects.filter(id = campaignid)

        if start_.year != year:
            message = "Task START date (" + start + ") is beyond current year (" + str(year) + ")!"
            # redirect = 0

        elif end_.year != year:
             message = "Task END date (" + end + ") is beyond current year (" + str(year) + ")!"
             # redirect = 0

        # elif (start_ > task_min) or (start_ > task_min) or (end_ < task_max) or (end_ < task_min):
        #     # This rule kinda means a campaign can be delayed, but if it were to be brought forward, owners have to adjust tasks individually
        #
        # # There shouldn't be a case where prev.start > task_max, etc.
        # # as checks should work to prevent task_min > task_max
        # # but just put in case
        #
        #     message = "Campaign dates are outside of the min & max tasks date range (" +  task_min.strftime('%Y-%m-%d') + " to " + task_max.strftime('%Y-%m-%d') + "). Please change the dates."
        #     redirect = 0

        elif prev.end < prev.start:
            message = "Task END date ( " + prev.end.strftime('%Y-%m-%d') + " ) cannot be greater than task START date (" + prev.start.strftime('%Y-%m-%d') + ")!"
            # redirect = 0

        elif taskid > 0:
            t0 = tasks.objects.filter(id=taskid)

            # if shift_type == '1':
            recalculate_type = 'bulk'

            # Task dates check
            if (prev.start != start_) and (prev.end != end_):
                print("DIFF DATES 1")
                # diff_start = np.busday_count(prev.start, start, weekmask='1111100', holidays=holiday_list)
                diff_end = np.busday_count(prev.end, end, weekmask='1111100', holidays=holiday_list)

                # Update current task
                for changes in t0:
                    # Values are 'updated'.
                    # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                    changes.name = name
                    changes.category = cat
                    changes.progress = p
                    changes.start = start
                    changes.end = end
                    changes.owner = o

                    changes.last_edited_by = request_user

                    changes.save(recalculate_type)

                t = tasks.objects.get(id=taskid)


                for task in campaign_prev.tasks.filter(start__gte=prev.start): # filter subsequent tasks
                    task.start = np.busday_offset(task.start, diff_end, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # += timedelta(days=diff_start)
                    task.end = np.busday_offset(task.end, diff_end, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # += timedelta(days=diff_end)
                    task.last_edited_by = request_user

                    task.save(recalculate_type)


            if prev.start != start_:
                print("DIFF DATES 2")
                diff = np.busday_count(prev.start, start, weekmask='1111100', holidays=holiday_list)
                adjust_end = np.busday_offset(prev.end, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt)

                # Update current task
                for changes in t0:
                    # Values are 'updated'.
                    # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                    changes.name = name
                    changes.category = cat
                    changes.progress = p
                    changes.start = start
                    changes.end = adjust_end # adjust end date according to change in start date
                    changes.owner = o

                    changes.last_edited_by = request_user

                    changes.save(recalculate_type)

                t = tasks.objects.get(id=taskid)

                for task in campaign_prev.tasks.filter(start__gte=prev.start): # filter subsequent tasks
                    task.start = np.busday_offset(task.start, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # += timedelta(days=diff_start)
                    task.end = np.busday_offset(task.end, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # += timedelta(days=diff_end)
                    task.last_edited_by = request_user

                    task.save(recalculate_type)

            elif prev.end != end_:
                print("DIFF DATES 3")
                diff = np.busday_count(prev.end, end, weekmask='1111100', holidays=holiday_list)
                adjust_start = np.busday_offset(prev.start, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt)

                # Update current task
                for changes in t0:
                    # Values are 'updated'.
                    # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                    changes.name = name
                    changes.category = cat
                    changes.progress = p
                    changes.start = adjust_start # adjust start date according to change in start date. Answers question like "in order to end by X date, when should this task start?"
                    changes.end = end
                    changes.owner = o

                    changes.last_edited_by = request_user

                    changes.save(recalculate_type)

                t = tasks.objects.get(id=taskid)

                for task in campaign_prev.tasks.filter(start__gte=prev.start): # filter subsequent tasks
                    task.start = np.busday_offset(task.start, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # += timedelta(days=diff_start)
                    task.end = np.busday_offset(task.end, diff, roll='forward', weekmask='1111100', holidays=holiday_list).astype(dt) # += timedelta(days=diff_end)
                    task.last_edited_by = request_user

                    task.save(recalculate_type)

            else: # no change in dates
                print("DIFF DATES 4")

                # Update current task
                for changes in t0:
                    # Values are 'updated'.
                    # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                    changes.name = name
                    changes.category = cat
                    changes.progress = p
                    changes.owner = o

                    changes.last_edited_by = request_user

                    changes.save(recalculate_type)

                t = tasks.objects.get(id=taskid)



            version_data = json.loads(request_post.get('versions'))
            print(version_data)

            if len(version_data) - 2 > 0:

                for j in range(len(version_data) - 2):
                    task_name = version_data[str(j)]["name"]
                    task_progress = version_data[str(j)]["progress"]
                    task_start = version_data[str(j)]["start"]
                    task_end = version_data[str(j)]["end"]
                    task_owner = version_data[str(j)]["owner"]

                    t_p = progress.objects.get(id = task_progress)
                    t_o = owners.objects.get(id = task_owner)

                    tv = tasks_versions.objects.create(
                        task = t,
                        name = task_name,
                        progress = t_p,
                        start = task_start,
                        end = task_end,
                        owner = t_o,
                        last_edited_by = request_user
                    )

                # else:
                #     recalculate_type = 'single'

            # "re-calculate campaign start & end, and RUs"
            # can optimise in future to only re-calculate when there's a change in dates
            task_min = min(list(campaign_prev.tasks.values_list('start', flat=True)))
            task_max = max(list(campaign_prev.tasks.values_list('end', flat=True)))

            print(task_min)
            print(task_max)

            for changes in c0:
                # Values are 'updated'.
                # Using this method instead of direct 'update' call so `simple-history` is able to log updates
                changes.start = task_min
                changes.end = task_max

                changes.last_edited_by = request_user

                changes.save() # This save method shoud also perform the bulk re-calculation of weekly RUs

            c = campaigns.objects.get(id=campaignid)


            # WARNING DO NOT ENABLE THIS - current form setup shouldn't result in campaignid == 0
            # If it's enabled may accidentally create a new campaign!
            # else:
            #     c = campaigns.objects.create(
            #         name = name,
            #         type = tp,
            #         vertical = v,
            #         progress = p,
            #         start = start,
            #         end = end,
            #         last_edited_by = request_user
            #     )

            # lock for managing concurrent edits
            # For new edits it would just create a new entry
            # For existing edits it would "release" the campaign for editing
            locks.objects.create(
                user = request_user,
                type = 'campaign',
                identifier = c.id, # Be careful not to use campaignid! As the default for new campaigns is 0
                status = 'released'
            )

            message = name + " saved & dates adjusted!"

            # else: # shiftType == '0':

            return HttpResponse(message)



def save_task_version(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        taskversionid = int(request_post.get('taskversionid'))
        name = request_post.get('name')
        progress_val = request_post.get('progress')
        start = request_post.get('start')
        end = request_post.get('end')
        owner = request_post.get('owner')

        p = progress.objects.get(id = progress_val)
        o = owners.objects.get(id = owner)

        # if start < campaign_start  or end < campaign_start or start > campaign_end or end > campaign_end:
        #     message = "Task dates are out of campaign range."


        # if taskversionid > 0: # This wouldn't happen due to nature of html interaction setup
        #     # Validation:
        #     task = tasks.objects.get(id=taskid)
        #     campaign_start = task.campaign.start
        #     campaign_end = task.campaign.end
        #
        #     t0 = tasks.objects.filter(id=taskid)
        #
        #     for changes in t0:
        #         # Values are 'updated'.
        #         # Using this method instead of direct 'update' call so `simple-history` is able to log updates
        #         changes.name = name
        #         changes.progress = p
        #         changes.start = start
        #         changes.end = end
        #         changes.owner = o
        #
        #         changes.last_edited_by = request_user
        #
        #         changes.save()
        #
        #     t = tasks.objects.get(id=taskid)
        #
        #
        # else:


        t0 = tasks_versions.objects.filter(id=taskversionid)

        for changes in t0:
            # Values are 'updated'.
            # Using this method instead of direct 'update' call so `simple-history` is able to log updates
            changes.name = name
            changes.progress = p
            changes.start = start
            changes.end = end
            changes.owner = o

            changes.last_edited_by = request_user

            changes.save()

        t = tasks_versions.objects.get(id=taskversionid)
        #
        # taskid = int(request_post.get('taskid'))
        # t = tasks.objects.get(id = taskid)
        # tv = tasks_versions.objects.filter(id = taskversionid )
        #
        # tv = tasks_versions.objects.create(
        #     task = t,
        #     name = name,
        #     progress = p,
        #     start = start,
        #     end = end,
        #     owner = o,
        #     last_edited_by = request_user
        # )


        # version_data = json.loads(request_post.get('versions'))
        # print(version_data)
        #
        # if len(version_data) - 2 > 0:
        #
        #     for j in range(len(version_data) - 2):
        #         task_name = version_data[str(j)]["name"]
        #         task_progress = version_data[str(j)]["progress"]
        #         task_start = version_data[str(j)]["start"]
        #         task_end = version_data[str(j)]["end"]
        #         task_owner = version_data[str(j)]["owner"]
        #
        #         t_p = progress.objects.get(id = task_progress)
        #         t_o = owners.objects.get(id = task_owner)
        #
        #         tv = tasks_versions.objects.create(
        #             task = t,
        #             name = task_name,
        #             progress = t_p,
        #             start = task_start,
        #             end = task_end,
        #             owner = t_o,
        #             last_edited_by = request_user
        #         )






    # lock for managing concurrent edits
    # For new edits it would just create a new entry
    # For existing edits it would "release" the campaign for editing
    locks.objects.create(
        user = request.user,
        type = 'task_version',
        identifier = t.id, # Be careful not to use taskid! As the default for new campaigns is 0
        status = 'released'
    )

    return HttpResponse(name + " saved!")


def cancel(request):

    if request.method == 'POST':
        request_post = request.POST
        type_ = request_post.get('type')
        item_id = request_post.get('identifier')

        if item_id is None: # New tasks
            identifier_ = 0
        else:
            identifier_ = int(item_id)

        if identifier_ > 0:
            locks.objects.create(
                user = request.user,
                type =  type_,
                identifier = identifier_,
                status = 'released'
            )

        else:
            print("Do nothing. The edit is on a newly cloned campaign.")

    return HttpResponse("Cancelled success")


def delete(request):
    if request.method == 'POST':
        request_post = request.POST
        print(request_post.get('type'))

        if request_post.get('type') == 'campaign':
            campaignid = int(request_post.get('identifier'))

            if campaignid > 0:
                c0 = campaigns.objects.filter(id=campaignid)

                for changes in c0:

                    changes.status = 'deleted'
                    changes.last_edited_by = request.user
                    changes.save()

                    # c = campaigns.objects.get(id=campaignid)

        elif request_post.get('type') == 'task':
            taskid = int(request_post.get('identifier'))

            if taskid > 0:
                t0 = tasks.objects.filter(id=taskid)
                recalculate_type = 'single'

                for changes in t0:

                    changes.status = 'deleted'
                    changes.last_edited_by = request.user
                    changes.save(recalculate_type)

                    # t = tasks.objects.get(id=taskid)

        elif request_post.get('type') == 'task-version':
            taskid = int(request_post.get('identifier'))

            if taskid > 0:
                t0 = tasks_versions.objects.filter(id=taskid)

                for changes in t0:

                    changes.status = 'deleted'
                    changes.last_edited_by = request.user
                    changes.save()

                    # t = tasks.objects.get(id=taskid)

        elif request_post.get('type') == 'comment':
            commentid = int(request_post.get('identifier'))

            if commentid > 0:
                c0 = comments.objects.filter(id=commentid)

                for changes in c0:

                    changes.status = 'deleted'
                    changes.last_edited_by = request.user
                    changes.save()

        elif request_post.get('type') == 'task-comment':
            commentid = int(request_post.get('identifier'))

            if commentid > 0:
                c0 = tasks_comments.objects.filter(id=commentid)

                for changes in c0:

                    changes.status = 'deleted'
                    changes.last_edited_by = request.user
                    changes.save()


        elif request_post.get('type') == 'link':
            linkid = int(request_post.get('identifier'))

            if linkid > 0:
                l0 = links.objects.filter(id=linkid)

                for changes in l0:

                    changes.status = 'deleted'
                    changes.last_edited_by = request.user
                    changes.save()

        return HttpResponse("Deleted")


def clone(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        print(request_user)

        campaignid = int(request_post.get('campaignid'))

        c = campaigns.objects.get(id=campaignid)
        new = copy.deepcopy(c)
        new.pk = None
        new.name += ' [CLONE]'
        new.save()

        recalculate_type = 'bulk'

        for task in c.tasks.all():
            new_task = copy.deepcopy(task)
            new_task.pk = None
            new_task.campaign = new
            new_task.save(recalculate_type)

        return HttpResponse("Clone successful!")


def edit_comment(request):
    if request.method == 'POST':

        request_post = request.POST
        commentid = int(request_post.get('commentid'))

        if commentid > 0:

            c = comments.objects.get(id=commentid)

            if c.commenter.username != request.user:
                print(c.commenter.username)
                print(request.user.username)
                message = "Edit disabled. You're trying to edit a comment created by someone else."
                response = 0

            else:
                message = ''
                response = 1

            data = {
                'code': response,
                'message': message
            }

            return JsonResponse(data)

def edit_task_comment(request):
    if request.method == 'POST':

        request_post = request.POST
        commentid = int(request_post.get('commentid'))

        if commentid > 0:

            c = tasks_comments.objects.get(id=commentid)

            if c.commenter.username != request.user:
                print(c.commenter.username)
                print(request.user.username)
                message = "Edit disabled. You're trying to edit a comment created by someone else."
                response = 0

            else:
                message = ''
                response = 1

            data = {
                'code': response,
                'message': message
            }

            return JsonResponse(data)


def save_comment(request):

    if request.method == 'POST':
        request_post = request.POST
        type = request_post.get('type')
        item_id = int(request_post.get('identifier'))
        commentid = int(request_post.get('commentid'))
        comment_text = request_post.get('comment')
        request_user = request.user

        o = owners.objects.get(username__username = request_user)

        if item_id == 0: # existing comments
            if type == 'campaign':
                c = comments.objects.filter(id=commentid)

                for changes in c:
                    changes.comment = comment_text
                    changes.last_edited_by = request_user

                    changes.save()

            elif type == 'task':
                c = tasks_comments.objects.filter(id=commentid)

                for changes in c:
                    changes.comment = comment_text
                    changes.last_edited_by = request_user

                    changes.save()


        else: # new comments
            if type == 'campaign':
                c = campaigns.objects.get(id=item_id)

                comments.objects.create(
                    campaign = c,
                    comment = comment_text,
                    commenter = o,
                    last_edited_by = request_user
                )

            elif type == 'task':
                t = tasks.objects.get(id=item_id)

                tasks_comments.objects.create(
                    task = t,
                    comment = comment_text,
                    commenter = o,
                    last_edited_by = request_user
                )

    return HttpResponse("Comment added!")


def edit_link(request):
    if request.method == 'POST':
        request_post = request.POST
        request_user = request.user
        linkid = int(request_post.get('linkid'))

        link = links.objects.get(id = linkid)

        lock_ = locks.objects.filter(type = 'campaign-link', identifier = linkid).order_by('-timestamp_utc')

        if len(lock_) > 0: # If lock records exist
            lock = lock_.first() # Most recent lock for this campaign
            print(lock)
            print(lock.status)

            time_diff_hours = ((dt.now(timezone.utc) - lock.timestamp_utc).seconds)/3600
            print(time_diff_hours)

        else:
            time_diff_hours = 1000 # very first lock

        if time_diff_hours > 0.25: # 15 mins or new lock, as forms are short
            # release current campaign for editing
            # This happens in the event another user clicks edit but never saves
            locks.objects.create(
                user = request_user,
                type = 'campaign-link',
                identifier = linkid,
                status = 'locked'
            )

            response = 2
            message = str(request_user) + " is now editing"
            print(message)


        else: # time_diff_hours <= 30 mins
            if lock.status == 'locked':
                # Provide option for lock owner to release so fellow users can edit
                if lock.user == request_user:
                    response = 3
                    message = "WARNING: " + str(lock.user) + ", you have previously edited this link: " + str(link.name) + ", but not saved. You could possibly have this opened in edit mode on another window or refreshed the page without saving. Please ensure you do not have unsaved changes on another window before proceeding."
                    print(message)

                else:
                    message = str(lock.user) + " is currently editing this link: " + str(link.name)
                    print(message)
                    response = 0


            else: # create new lock session
                locks.objects.create(
                    user = request_user,
                    type = 'campaign-link',
                    identifier = linkid,
                    status = 'locked'
                )

                message = str(link.name) + ": locked for you to edit"
                print(message)
                response = 1


    data = {
        'code': response,
        'message': message
    }

    return JsonResponse(data)

def save_link(request):

    if request.method == 'POST':
        request_post = request.POST

        campaignid = int(request_post.get('campaignid'))
        linkid = int(request_post.get('linkid'))
        link_name = request_post.get('link_name')
        link = request_post.get('link')
        request_user = request.user

        if linkid > 0: # existing links

            l0 = links.objects.filter(id=linkid)

            for changes in l0:
                changes.name = link_name
                changes.link = link
                changes.last_edited_by = request_user

                changes.save()

            l = links.objects.get(id=linkid)

            message = "Link edited!"


        else: # new links

            c = campaigns.objects.get(id=campaignid)

            l = links.objects.create(
                campaign = c,
                name = link_name,
                link = link,
                last_edited_by = request_user
            )

            message = "Link added!"


    locks.objects.create(
        user = request_user,
        type = 'campaign-link',
        identifier = l.id, # Be careful not to use linkid! As the default for new links is 0
        status = 'released'
    )

    return HttpResponse(message)



def ru_report(request):
    report = tasks.objects.filter(~Q(campaign__type__name='Template'), campaign__status = 'active').values('campaign__type__name', 'campaign__vertical__name', 'campaign__name', 'campaign__ops_hours', 'campaign__agency_hours', 'campaign__analytics_hours', 'campaign__complexity__name', 'campaign__countries').distinct().order_by('campaign__type__name', 'campaign__vertical__name', 'campaign__name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ru_report.csv"'

    df = pd.DataFrame.from_records(report)
    df = df [['campaign__type__name', 'campaign__vertical__name', 'campaign__name', 'campaign__ops_hours', 'campaign__agency_hours', 'campaign__analytics_hours', 'campaign__complexity__name', 'campaign__countries']]
    df.columns = ['Type', 'Vertical', 'Campaign', 'Ops RU', 'eClerx RU', 'Analytics RU', 'Complexity', 'Countries']
    df.to_csv(response, index = False)

    return response

def tasks_report(request):
    owner_ = owners.objects.get(username = request.user )
    tasks_ = tasks.objects.filter(~Q(campaign__type__name='Template'), campaign__status = 'active', owner = owner_ )
    report = tasks.objects.filter(~Q(campaign__type__name='Template'), campaign__status = 'active', owner = owner_ ).values('progress__name', 'campaign__vertical__name', 'campaign__name', 'name', 'owner__name', 'owner__team__name', 'end', 'start', 'end', 'campaign__analytics_owner__name', 'campaign__ops_owner__name', 'campaign__lcm_owner__name').distinct().order_by('campaign__name')

    for task in tasks_:
        task_comment_list = list(task.tasks_comments.filter(commenter = owner_, task__status = 'active').values('comment'))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="crm_projects_report_' + owner_.name + '.csv"'

    df = pd.DataFrame.from_records(report)

    df['functional_area'] = ''
    df['category'] = 'Campaign'

    df['project_desc'] = ''
    df['request'] = 'Regional'

    df['activity_task_desc'] = "\n".join(task_comment_list)
    print(df['activity_task_desc'])
    df['priority'] = ''

    df['dependency'] = ''

    df['actual_delivery_date'] = ''

    df['days_prep'] = df['end'] - df['start']

    # holiday_list = [str(date) for date in holidays.objects.values_list('date', flat=True)]
    # np.busday_count(self.start, self.end, weekmask='1111100', holidays=holiday_list)

    df['days'] = df['days_prep'].apply(lambda x: x.days)

    df['team_member'] = ''

    df = df [['progress__name', 'campaign__vertical__name', 'functional_area', 'category', 'campaign__name', 'project_desc', 'request', 'name', 'activity_task_desc', 'priority', 'owner__name', 'owner__team__name', 'dependency', 'end', 'days', 'actual_delivery_date', 'start', 'end', 'team_member', 'campaign__analytics_owner__name', 'campaign__ops_owner__name', 'campaign__lcm_owner__name']]


    df.columns = ['Status', 'Business Unit', 'Functional Area', 'Category', 'Project', 'Project Description', 'Local Request/Regional CRM', 'Activity/Task', 'Activity/Task Description', 'Priority', 'Team Lead Assigned', 'Team', 'Dependency', 'Expected Delivery Date', 'Estimated Time in Working Days', 'Actual Delivery Date', 'Start Date', 'End Date', 'Team Member', 'Analytics Team POC', 'LCM Team POC', 'Ops Team POC']
    df.to_csv(response, index = False)

    return response


''' OPS ANALYTICS'''


def analytics(request):
    campaign_list = campaigns.objects.filter(~Q(type__name='Template'), status='active').order_by('progress', 'type', 'name', 'id')
    progress_list = campaigns.objects.filter(~Q(type__name='Template'), status='active').order_by('progress', 'type', 'name', 'id')

    data = {
        'campaigns': campaign_list,
        'weeks': week_list,
        'types': type_list, # DON"T REMOVE THIS! It's being used for dropdown
        'verticals': vertical_list,
        'complexities': complexity_list,
        'progress': progress_list,
        'countries': country_list,
        'platforms': platform_list,
        'teams': team_list,
        'categories': category_list,
        'owners': owner_list,
        'owner_lcm': owner_lcm_list,
        'owner_ops': owner_ops_list,
        'owner_analytics': owner_analytics_list
    }

    return render(request, "timelines/analytics.html", data)
