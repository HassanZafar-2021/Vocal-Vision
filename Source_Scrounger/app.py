from flask import Flask, render_template, request
from openperplex import Openperplex
import urllib.parse

app = Flask(__name__)

api_key = API_KEY

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']

        client = Openperplex(api_key)

        result = client.search(
            query=query,
            date_context="",  # Use current date of the API server
            location="us",
            pro_mode=False,
            response_language="en",
            answer_type="text",
            search_type="general",
            verbose_mode=False
        )

        sources = result.get("sources", [])

        # Process each source to extract the domain for favicon
        for source in sources:
            parsed_uri = urllib.parse.urlparse(source['link'])
            domain = parsed_uri.netloc
            source['domain'] = domain

        return render_template('results.html', query=query, sources=sources)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5051)
