import string
import random
import re
from flask import Flask, request, jsonify, render_template, redirect
from database import init_db, insert_url, get_url_by_code, increment_clicks, get_all_urls

app = Flask(__name__)

# Initialize Database
init_db()

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def is_valid_url(url):
    # Basic URL regex check
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/shorten', methods=['POST'])
def shorten():
    data = request.get_json() or {}
    original_url = data.get('url', '').strip()
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
        
    if not (original_url.startswith('http://') or original_url.startswith('https://')):
        original_url = 'https://' + original_url

    if not is_valid_url(original_url):
        return jsonify({'error': 'Invalid URL format'}), 400

    # Try generating a unique short code
    max_attempts = 10
    for _ in range(max_attempts):
        short_code = generate_short_code()
        if insert_url(original_url, short_code):
            short_url = request.host_url + short_code
            return jsonify({
                'short_code': short_code,
                'short_url': short_url,
                'original_url': original_url
            }), 201
            
    return jsonify({'error': 'Failed to generate a unique short code. Please try again.'}), 500

@app.route('/api/analytics', methods=['GET'])
def analytics():
    urls = get_all_urls()
    # Add full short url mapping for convenience
    for url in urls:
        url['short_url'] = request.host_url + url['short_code']
    return jsonify(urls)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url_entry = get_url_by_code(short_code)
    if url_entry:
        increment_clicks(short_code)
        return redirect(url_entry['original_url'])
    return "<h1>URL Not Found</h1><p>The requested short link does not exist.</p>", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
