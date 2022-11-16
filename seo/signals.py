def pre_save_auto_anchor(sender, instance, raw, using, update_fields, **kwargs):
    if getattr(instance, 'from_admin_site', False):
        instance.imported = False
