from bleach_whitelist.bleach_whitelist import markdown_tags, markdown_attrs

tags = markdown_tags
attrs = markdown_attrs

tags_allowed = [
    'pre', 'table', 'thead', 'tbody', 'th', 'td', 'tr', 'sup'
]
tags.extend(tags_allowed)
