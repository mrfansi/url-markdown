CONTENT_SELECTORS = {
    'ids': [
        'content',
        'main-content',
        'article-content'
    ],
    'classes': [
        'rm-Article',  # Add readme.com article class
        'content-body', 
        'article',
        'post-content'
    ]
}

CLEANING_SELECTORS = {
    'unwanted_tags': [
        'script', 'style', 'iframe', 'button'
    ],
    'common_classes': [
        'rdmd-code-copy',  # Remove copy code buttons
        'CodeTabs-toolbar', # Remove code tab buttons
        'heading-anchor-icon', # Remove anchor icons
        'PageThumbs', # Remove feedback section
        'UpdatedAt'  # Remove update timestamp
    ],
    'common_ids': [
        'tutorialmodal-root'
    ]
}