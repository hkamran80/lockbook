"""
Lockbook Backend
Contributors:
	:: H. Kamran [@hkamran80] (author)
Version: 1.0.0
Last Updated: 2020-06-22, @hkamran80
"""

from flask import Flask
import flask_cors
import os

app = Flask(__name__, static_folder="../dist", static_url_path="/")
app.secret_key = os.urandom(24)
flask_cors.CORS(app)

@app.route("/")
def index():
	return app.send_static_file("index.html")

if __name__ == "__main__":
	development = {
		"state": True,
		"host": "0.0.0.0",
		"port": 8081
	}
	app.run(host=development["host"], port=development["port"], debug=development["state"])
