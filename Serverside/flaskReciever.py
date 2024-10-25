from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory data store (you can use a database for persistence)
pi_data_store = {}

@app.route('/receive_data', methods=['POST'])
def receive_data():
    # Get JSON data from the request
    data = request.get_json()
    print("Data received")
    # Validate the data
    if not data or 'pi_id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
    
    pi_id = data['pi_id']
    pi_data_store[pi_id] = {
        'data': data,
        'timestamp': datetime.utcnow()
    }

    # Respond to the Pi
    return jsonify({'status': 'success'}), 200

@app.route('/pi_data', methods=['GET'])
def get_pi_data():
    # Return the stored data for all Pis
    return jsonify(pi_data_store), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
