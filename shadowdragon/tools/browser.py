import webbrowser

class BrowserTools:
    def open_url(self, url):
        if not url.startswith("http"):
            url = f"https://{url}"
        webbrowser.open(url)
        return f"Opening {url}."
