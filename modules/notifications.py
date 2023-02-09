"""
    name: notifications
    once: false
    origin: tgpy://module/notifications
    priority: 10000
    save_locals: true
"""

# config_loader module
NotificationsConfig = UniversalModuleConfig('notifications', ['notification_channel_id'], [int])


@dot  # dot module
async def notify(text, *args, **kwargs):
    if not text:
        text = "Something happened"
    await client.send_message(NotificationsConfig.notification_channel_id, text, *args, **kwargs)
