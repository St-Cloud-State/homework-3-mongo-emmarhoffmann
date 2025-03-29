from flask import Flask, jsonify, render_template, request
import random # use for creating application numbers
import sqlite3
import pymongo
import os

app = Flask(__name__)

# SQLite db for basic application info
DATABASE = os.path.join(os.getcwd(), 'Homework3/db/applications.db')

#  Ensure the database directory exists
if not os.path.exists(os.path.dirname(DATABASE)):
    os.makedirs(os.path.dirname(DATABASE))

#  Initialize SQLite Database
def init_sqlite_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Applications (
        application_number INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        zipcode TEXT NOT NULL,
        status TEXT DEFAULT 'received'
    )''')
    conn.commit()
    conn.close()

# Call this function before using the database
init_sqlite_db()

#  MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['acme_loans']
notes_collection = db['application_notes']

@app.route('/api/submit-application', methods=['POST'])
def submit_application():
    print("application submitting...")
    data = request.get_json()
    name = data.get('name')
    zipcode = data.get('zipcode')

    # generate a random 5 digit application number
    application_number = random.randint(10000, 99999)

    # store in SQLite
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Applications (application_number, name, zipcode) VALUES (?, ?, ?)", (application_number, name, zipcode))
    conn.commit()
    conn.close()

    # add initial note in MongoDB
    initial_note = {
        'application_number': application_number,
        'phase': 'submission',
        'phase_order': 1,
        'message': 'Application received'
    }
    notes_collection.insert_one(initial_note)

    return jsonify({
        'message': 'Application successfully submitted',
        'application_number': application_number
        })


# Route to check status of application
@app.route('/api/check-status', methods=['GET'])
def check_status():
    print("checking status...")
    application_number = int(request.args.get('number'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM Applications WHERE application_number = ?", (application_number,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({'status': result[0]})
    return jsonify({'status': 'not found'})

# Route to update the application status
@app.route('/api/update-status', methods=['POST'])
def update_status():
    print("updating status...")
    data = request.get_json()
    application_number = int(data.get('number'))
    new_status = data.get('status')
    reason = data.get('reason', '')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Applications SET status = ? WHERE application_number = ?", (new_status, application_number))
    conn.commit()
    conn.close()

    # add a status change note to MongoDB
    status_note = {
        'application_number': application_number,
        'phase': new_status,
        'phase_order': get_phase_order(new_status),
        'message': f"Status changed to {new_status}" + (f": {reason}" if reason else "")
    }
    notes_collection.insert_one(status_note)

    return jsonify({'message': 'Status updated successfully'})

# Add a note to an application
@app.route('/api/add-note', methods=['POST'])
def add_note():
    data = request.get_json()
    application_number = int(data.get('number'))
    phase = data.get('phase')
    subphase = data.get('subphase', None)
    task = data.get('task', None)
    message = data.get('message')

    note = {
        'application_number': application_number,
        'phase': phase,
        'phase_order': get_phase_order(phase, subphase),
        'message': message
    }

    if subphase:
        note['subphase'] = subphase
    if task:
        note['task'] = task

    notes_collection.insert_one(note)

    return jsonify({'message': 'Note added successfully'})

# Get all note for an application
@app.route('/api/get-notes', methods=['GET'])
def get_notes():
    application_number = int(request.args.get('number'))

    # Get application details from SQLite
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT application_number, name, zipcode, status FROM Applications WHERE application_number = ?", (application_number,))
    app_data = cursor.fetchone()
    conn.close()

    if not app_data:
        return jsonify({'error': 'Application not found'})

    #Get notes from MongoDB
    notes = list(notes_collection.find({'application_number': application_number}, {'_id': 0}))

    application = {
        'application_number': app_data[0],
        'name': app_data[1],
        'zipcode': app_data[2],
        'status': app_data[3],
        'notes': notes
    }

    return jsonify(application)

def get_phase_order(phase, subphase=None):
    # Returns numeric val for phase ordering
    phase_orders = {
        'submission': 1,
        'processing': 2,
        'personal_details': 2.1,
        'credit_check': 2.2,
        'certificate_check': 2.3,
        'accepted': 3,
        'rejected': 4,                                
    }

    if phase in phase_orders:
        return phase_orders[phase]
    elif subphase in phase_orders:
        return phase_orders[subphase]
    # phase 5 is other unknown phase        
    return 5 

# Route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
