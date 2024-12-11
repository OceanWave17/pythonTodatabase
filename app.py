from flask import Flask, render_template, jsonify, request
import psycopg2

app = Flask(__name__)

# PostgreSQL connection settings
DB_SETTINGS = {
    'host': 'localhost',
    'database': 'sensor_data',
    'user': 'postgres',
    'password': 'aquarium',  # Use environment variables in production!
}

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET'])
def fetch_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, value, timestamp FROM sensor_values ORDER BY timestamp DESC LIMIT 10")
        data = cursor.fetchall()
        conn.close()
        # Format the data as JSON
        return jsonify([
            {'id': row[0], 'value': row[1], 'timestamp': row[2].isoformat()} for row in data
        ])
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/add', methods=['POST'])
def add_data():
    try:
        data = request.json
        value = data.get('value')
        if value is None:
            return jsonify({'message': 'Value is required'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500

        cursor = conn.cursor()
        cursor.execute("INSERT INTO sensor_values (value) VALUES (%s)", (value,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Data added successfully!'}), 200
    except Exception as e:
        print(f"Error adding data: {e}")
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
