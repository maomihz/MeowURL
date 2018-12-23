from bleach_whitelist.bleach_whitelist import markdown_tags, markdown_attrs

tags = markdown_tags
attrs = markdown_attrs

# Additionally, allow these tags
tags.extend([
    'pre', 'table', 'thead', 'tbody', 'th', 'td', 'tr', 'sup'
])
