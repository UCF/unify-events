import re
import settings
from datetime import datetime

from seo.models import InternalLink, InternalLinkRecord

def internal_links(event, process_time):
    value = event.description
    if not process_time:
        process_time = datetime.now()

    links = InternalLink.objects.find_in_text(value)
    for link in links:
        phrases = '|'.join(link.phrases.values_list('phrase', flat=True))
        anchor_re = f'(<a[^>]*>)(?P<content>.*{phrases}.*)(<\/a>)'
        match = re.search(anchor_re, value)

        if match and settings.SEO_AUTO_ANCHORS_FORCE_UPDATE:
            value = re.sub(
                f'(<a[^>]*>)(?P<content>.*{phrases}.*)(<\/a>)',
                f'<a href="{link.url}" target="_blank">{match.group("content")}</a>',
                value,
                1
            )

            phrase = next(link.phrases.get(phrase=p) for p in phrases.split('|') if p in value)
            try:
                record = InternalLinkRecord.objects.get(
                    keyword_phrase=phrase,
                    event=event,
                    internal_link=link
                )
                record.updated_at = process_time
                record.save()
            except InternalLinkRecord.DoesNotExist:
                record = InternalLinkRecord(
                    keyword_phrase=phrase,
                    event=event,
                    internal_link=link,
                    updated_at=process_time
                )
                record.save()


            # Don't do the replacement again if regex replace happened
            continue
        elif match and settings.SEO_AUTO_ANCHORS_FORCE_UPDATE == False:
            continue

        for phrase in link.phrases.all():
            if phrase.phrase in value:
                value = value.replace(phrase.phrase,
                    f'<a href="{link.url}" target="_blank">{phrase.phrase}</a>', 1)
                break

    return value
