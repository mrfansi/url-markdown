CONTENT_SELECTORS = {
    'ids': [
        'content',
        'main-content',
        'article-content'
    ],
    'classes': [
        'rm-Article',
        'content-body', 
        'article',
        'post-content'
    ]
}

CLEANING_SELECTORS = {
    'unwanted_tags': [
        'script', 
        'style', 
        'iframe', 
        'button', 
        'header'
    ],
    'common_classes': [
        'rdmd-code-copy',
        'CodeTabs-toolbar',
        'heading-anchor-icon',
        'PageThumbs',
        'UpdatedAt'
    ],
    'common_ids': [
        'tutorialmodal-root'
    ]
}