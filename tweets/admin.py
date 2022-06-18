from django.contrib import admin
from tweets.models import Tweet


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    # 在界面会把下面像表格一样列出来
    list_display = (
        'created_at',
        'user',
        'content',
    )
