

def scrub_default_image_url(form):
    if form.image_url.data == '/static/images/noun-weights-49996.png':
        form.image_url.data = ''

def replace_default_image_url(form, user):
        if form.image_url.data == '':
            user.image_url = '/static/images/noun-weights-49996.png'