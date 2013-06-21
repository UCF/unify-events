def override_event_instances(instances, overrides):
    """
    Combines the instances and the overriden events
    and returns a single list.
    """
    new_instances = []
    if overrides:
        lookup = [((instance.event, instance.start, instance.end), instance) for
                instance in overrides]
        lookup = dict(lookup)

        for base_instance in instances:
            save_instance = base_instance
            if (base_instance.event, base_instance.start, base_instance.end) in lookup:
                save_instance = lookup.pop((base_instance.event, base_instance.start, base_instance.end))

            new_instances.append(save_instance)

        new_instances.sort(key=lambda instance: instance.start)

    return new_instances