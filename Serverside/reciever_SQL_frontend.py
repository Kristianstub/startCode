from flask import Flask, request, jsonify, render_template, url_for
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from dateutil import parser
import pandas as pd

app = Flask(__name__)

# Configure the database URI (using SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pi_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Device model
class Device(db.Model):
    __tablename__ = 'devices'
    mac_address = db.Column(db.String(17), primary_key=True)
    pi_id = db.Column(db.String(50), nullable=False)

    readings = db.relationship('Reading', backref='device', lazy=True)

# Define the Reading model
class Reading(db.Model):
    __tablename__ = 'readings'
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), db.ForeignKey('devices.mac_address'), nullable=False)
    cpu_usage = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    # Extract the pi_id and data
    if len(data) != 1:
        return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400

    pi_id = next(iter(data))
    pi_data = data[pi_id]

    # Extract the data fields
    data_content = pi_data.get('data', {})
    timestamp_str = pi_data.get('timestamp', '')

    cpu_usage = data_content.get('cpu_usage')
    temperature = data_content.get('temperature')
    mac_address = data_content.get('pi_mac')

    if not all([cpu_usage is not None, temperature is not None, mac_address, timestamp_str]):
        return jsonify({'status': 'error', 'message': 'Missing data fields'}), 400

    # Parse the timestamp
    try:
        timestamp = parser.parse(timestamp_str)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Invalid timestamp format'}), 400

    # Check if the device exists in the database
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        # Device does not exist, create a new one
        device = Device(mac_address=mac_address, pi_id=pi_id)
        db.session.add(device)
        db.session.commit()
    
    # Add the new reading to the database
    reading = Reading(
        mac_address=mac_address,
        cpu_usage=cpu_usage,
        temperature=temperature,
        timestamp=timestamp
    )
    db.session.add(reading)
    db.session.commit()

    return jsonify({'status': 'success'}), 200

@app.route('/')
def index():
    # Fetch all devices and their last timestamp
    devices = Device.query.all()
    device_list = []
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

    for device in devices:
        last_reading = Reading.query.filter_by(mac_address=device.mac_address).order_by(Reading.timestamp.desc()).first()
        if last_reading:
            status = 'Online' if last_reading.timestamp >= ten_minutes_ago else 'Offline'
            device_list.append({
                'pi_id': device.pi_id,
                'mac_address': device.mac_address,
                'last_seen': last_reading.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'status': status
            })

    return render_template('index.html', devices=device_list)

@app.route('/device/<mac_address>')
def device_logs(mac_address):
    # Fetch the last 10 logs for the device
    readings = Reading.query.filter_by(mac_address=mac_address).order_by(Reading.timestamp.desc()).limit(10).all()
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return "Device not found", 404

    logs = []
    for r in readings:
        logs.append({
            'cpu_usage': r.cpu_usage,
            'temperature': r.temperature,
            'timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('device_logs.html', device=device, logs=logs)

@app.route('/api/online_devices')
def online_devices():
    # Return data for the online devices chart
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    devices = Device.query.all()
    online_status = []

    for device in devices:
        last_reading = Reading.query.filter_by(mac_address=device.mac_address).order_by(Reading.timestamp.desc()).first()
        if last_reading:
            status = 'Online' if last_reading.timestamp >= ten_minutes_ago else 'Offline'
            online_status.append({
                'mac_address': device.mac_address,
                'status': status
            })

    online_count = len([d for d in online_status if d['status'] == 'Online'])
    offline_count = len(online_status) - online_count

    data = {
        'labels': ['Online', 'Offline'],
        'counts': [online_count, offline_count]
    }
    return jsonify(data)

@app.route('/devices_over_time')
def devices_over_time():
    return render_template('devices_over_time.html')

@app.route('/api/devices_over_time')
def api_devices_over_time():
    # Generate data for the devices over time chart
    readings = Reading.query.order_by(Reading.timestamp).all()
    if not readings:
        return jsonify({'timestamps': [], 'device_counts': []})

    # Create a DataFrame for easier manipulation
    data = [{'timestamp': r.timestamp, 'mac_address': r.mac_address} for r in readings]
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)

    # Resample data by day (you can adjust the frequency)
    resampled = df.groupby('mac_address').resample('D').count()

    # Count unique devices over time
    device_counts = resampled.reset_index().groupby('timestamp')['mac_address'].nunique()

    # Prepare data for the chart
    timestamps = device_counts.index.strftime('%Y-%m-%d').tolist()
    counts = device_counts.values.tolist()

    return jsonify({'timestamps': timestamps, 'device_counts': counts})

if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5000, debug=True)
