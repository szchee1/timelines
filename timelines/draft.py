# Set this to run annually?
editor = User.objects.get(username='joanna.chee')

for week in range(1,54):
    weeks.objects.create(
        no = week,
        last_edited_by = editor
    )
