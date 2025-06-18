from flask import Flask, request, jsonify
from lib.validators import is_valid_email_syntax, has_mx_record, verify_email_smtp

app = Flask(__name__)

@app.route('/validate_email', methods=['POST'])
def validate_email_endpoint():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"error": "Email not provided"}), 400

    email = data['email']
    results = {
        "email": email,
        "is_valid_syntax": is_valid_email_syntax(email),
        "has_mx_record": has_mx_record(email),
        "can_smtp_verify": verify_email_smtp(email)
    }
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
