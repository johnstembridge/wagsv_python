
def render_link(url, text="", image=None):
    if image:
        return '<a href="{}"><img title="{}" src="{}"></a>'.format(url, text, image)
    if text:
        return '<a href="{}">{}</a>'.format(url, text)