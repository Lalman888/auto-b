from urllib.parse import urlparse

def extract_domain(url):
    url = url.lower()
    if not ("http://" in url or "https://" in url):
        url = "http://" + url
    domain = urlparse(url).netloc
    if 'www.' in domain:
        return domain.replace('www.', '')
    else:
        return domain

if __name__ == "__main__":
    print(extract_domain('https://www.loveforeverpets.com/'))  # Output: loveforeverpets.com
    print(extract_domain('www.loveforeverpets.com'))           # Output: loveforeverpets.com
