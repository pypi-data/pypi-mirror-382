def url_transform(url: str) -> str:
    
    if url.endswith('/'):
        return url[:-1]
    
    return url