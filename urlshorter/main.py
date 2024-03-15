from flask import Flask, request, render_template, redirect, url_for, request
import json
import os
import string
import random

app = Flask(__name__)

DATABASE_FILE = "urls.json"

def load_urls():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump({}, f)

    with open(DATABASE_FILE, 'r') as f:
        return json.load(f)

def save_urls(urls):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(urls, f, indent=4)

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    return short_url

def shorten_url(long_url, custom_short_url=None):
    urls = load_urls()

    if custom_short_url:
        if custom_short_url in urls:
            return "This link is used"

        urls[custom_short_url] = {'long_url': long_url, 'visits': 0}
        save_urls(urls)
        return custom_short_url

    else:
        short_url = generate_short_url()
        while short_url in urls:
            short_url = generate_short_url()

        urls[short_url] = {'long_url': long_url, 'visits': 0}
        save_urls(urls)
        return short_url


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        custom_short_url = request.form.get('custom_short_url', None)
        short_url_or_message = shorten_url(long_url, custom_short_url)
        if short_url_or_message == "This link is used":
            return render_template('index.html', message=short_url_or_message)
        return redirect(url_for('shortened', short_url=short_url_or_message))
    return render_template('index.html')

@app.route('/shorter/<short_url>')
def shortened(short_url):
    urls = load_urls()
    long_url_info = urls.get(short_url)
    if long_url_info:
        long_url = long_url_info['long_url']
        visits = long_url_info.get('visits', 0)
        full_shortened_url = request.url_root + short_url
        return render_template('shortened.html', short_url=full_shortened_url, visits=visits)
    return "URL not found"

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    urls = load_urls()
    long_url_info = urls.get(short_url)
    if long_url_info:
        long_url = long_url_info['long_url']
        visits = long_url_info.get('visits', 0)
        urls[short_url]['visits'] = visits + 1
        save_urls(urls)
        
        return redirect(long_url)
    return "URL not found"


if __name__ == '__main__':
    app.run(debug=True)
