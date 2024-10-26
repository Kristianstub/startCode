from flask import Flask, request, jsonify
from datetime import datetime
import json 
from flask_sqlalchemy import SQLAlchemy





app = Flask(__name__)
db = SQLAlchemy(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pi_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy ORM
db = SQLAlchemy(app)

class PiData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pi_id = db.Column(db.String(100), nullable=False)
    cpu_usage = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


# In-memory data store (you can use a database for persistence)
pi_data_store = {}

@app.route('/receive_data', methods=['POST'])
def receive_data():
    # Get JSON data from the request
    data = request.get_json()
    
    # Validate the data
    if not data or 'pi_id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
    
    pi_id = data['pi_id']
    pi_data_store[pi_id] = {
        'data': data,
        'timestamp': datetime.utcnow()
    }
    try:
        with open('pi_data_log.jsonl', 'a') as f:
            # Create a log entry with timestamp
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'pi_id': pi_id,
                'data': data
            }
            # Write the JSON-serialized log entry to the file
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        # Handle exceptions (optional)
        print(f"Error writing to file: {e}")

    # Respond to the Pi
    return jsonify({'status': 'success'}), 200

@app.route('/pi_data', methods=['GET'])
def get_pi_data():
    # Return the stored data for all Pis
    return jsonify(pi_data_store), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
