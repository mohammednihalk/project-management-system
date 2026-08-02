from django.contrib import admin
from .models import User, Project, Notification, Event


# ===== REGISTER BASIC MODELS =====
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Event)


# ===== DEFAULT MESSAGE =====
@admin.action(description="General Admin Message")
def send_message(modeladmin, request, queryset):
    users = User.objects.all()

    for user in users:
        Notification.objects.create(
            user=user,
            title="Admin Message",
            message="System update from admin",
            type="admin"
        )

    modeladmin.message_user(request, "General message sent")


# ===== MAINTENANCE =====
@admin.action(description="Server Maintenance Alert")
def maintenance_message(modeladmin, request, queryset):
    users = User.objects.all()

    for user in users:
        Notification.objects.create(
            user=user,
            title="Maintenance Notice",
            message="Server will be down today at 10 PM",
            type="admin"
        )

    modeladmin.message_user(request, "Maintenance message sent")


# ===== NEW FEATURE =====
@admin.action(description="New Feature Announcement")
def feature_message(modeladmin, request, queryset):
    users = User.objects.all()

    for user in users:
        Notification.objects.create(
            user=user,
            title="New Feature",
            message="New feature has been added",
            type="admin"
        )

    modeladmin.message_user(request, "Feature message sent")


# ===== CUSTOM ADMIN =====
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'created_at')
    actions = [send_message, maintenance_message, feature_message]


admin.site.register(Notification, NotificationAdmin)