from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import locks, holidays, progress, verticals, types, countries, platforms, complexities, teams, categories, owners, regions, weeks, campaigns, comments, links, tasks, tasks_comments, tasks_versions

# Options
admin.site.register(locks, SimpleHistoryAdmin)
admin.site.register(holidays, SimpleHistoryAdmin)
admin.site.register(progress, SimpleHistoryAdmin)
admin.site.register(verticals, SimpleHistoryAdmin)
admin.site.register(types, SimpleHistoryAdmin)
admin.site.register(countries, SimpleHistoryAdmin)
admin.site.register(platforms, SimpleHistoryAdmin)
admin.site.register(complexities, SimpleHistoryAdmin)
admin.site.register(teams, SimpleHistoryAdmin)
admin.site.register(categories, SimpleHistoryAdmin)
admin.site.register(owners, SimpleHistoryAdmin)
admin.site.register(regions, SimpleHistoryAdmin)

# Campaigns
admin.site.register(weeks, SimpleHistoryAdmin)
admin.site.register(campaigns, SimpleHistoryAdmin)
admin.site.register(comments, SimpleHistoryAdmin)
admin.site.register(links, SimpleHistoryAdmin)
admin.site.register(tasks, SimpleHistoryAdmin)
admin.site.register(tasks_comments, SimpleHistoryAdmin)
admin.site.register(tasks_versions, SimpleHistoryAdmin)
