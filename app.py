from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
import sqlite3
import qrcode
import io
import base64
from datetime import datetime, date
import csv
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'aws-workshop-secret-key-2025'

# Database initialization
def init_db():
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    
    # Create workshops table
    c.execute('''CREATE TABLE IF NOT EXISTS workshops
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 date TEXT NOT NULL,
                 topic TEXT NOT NULL,
                 instructor TEXT NOT NULL,
                 time TEXT NOT NULL,
                 price REAL NOT NULL,
                 max_participants INTEGER DEFAULT 50,
                 is_active INTEGER DEFAULT 1,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create registrations table
    c.execute('''CREATE TABLE IF NOT EXISTS registrations
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 workshop_id INTEGER,
                 name TEXT NOT NULL,
                 email TEXT NOT NULL,
                 phone TEXT,
                 company TEXT,
                 experience_level TEXT,
                 registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (workshop_id) REFERENCES workshops (id))''')
    
    conn.commit()
    conn.close()

# Get current active workshop
def get_active_workshop():
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM workshops WHERE is_active = 1 ORDER BY date DESC LIMIT 1')
    workshop = c.fetchone()
    conn.close()
    return workshop

# Enhanced QR code generation
def generate_qr_code():
    try:
        # Get the registration URL (always the same)
        registration_url = url_for('register', _external=True)
        
        # Create QR code with AWS-themed styling
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction
            box_size=10,
            border=4,
        )
        qr.add_data(registration_url)
        qr.make(fit=True)
        
        # Use AWS orange (#FF9900) for the QR code
        img = qr.make_image(fill_color="#0A0A09", back_color="white")
        
        # Convert to base64 for HTML embedding
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", quality=100)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'qr_code': img_str,
            'url': registration_url,
            'domain': urlparse(registration_url).netloc
        }
    except Exception as e:
        app.logger.error(f"QR Generation Error: {str(e)}")
        return None

# New API endpoint for QR code
@app.route('/api/qr_code')
def get_qr_code():
    qr_data = generate_qr_code()
    if qr_data:
        return jsonify(qr_data)
    return jsonify({'error': 'Failed to generate QR code'}), 500

@app.route('/')
def index():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin')
def admin_dashboard():
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM workshops ORDER BY date DESC')
    workshops = c.fetchall()
    
    c.execute('''SELECT COUNT(*) FROM registrations r 
                 JOIN workshops w ON r.workshop_id = w.id 
                 WHERE w.is_active = 1''')
    current_registrations = c.fetchone()[0]
    conn.close()
    
    qr_data = generate_qr_code()
    
    return render_template('admin.html', 
                         workshops=workshops, 
                         current_registrations=current_registrations,
                         qr_code=qr_data['qr_code'] if qr_data else None,
                         qr_url=qr_data['url'] if qr_data else '#')

@app.route('/admin/add_workshop', methods=['POST'])
def add_workshop():
    date = request.form['date']
    topic = request.form['topic']
    instructor = request.form['instructor']
    time = request.form['time']
    price = float(request.form['price'])
    max_participants = int(request.form['max_participants'])
    
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    
    # Deactivate all previous workshops
    c.execute('UPDATE workshops SET is_active = 0')
    
    # Add new workshop
    c.execute('''INSERT INTO workshops (date, topic, instructor, time, price, max_participants, is_active)
                 VALUES (?, ?, ?, ?, ?, ?, 1)''', 
              (date, topic, instructor, time, price, max_participants))
    
    conn.commit()
    conn.close()
    
    flash('Workshop added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/activate_workshop/<int:workshop_id>')
def activate_workshop(workshop_id):
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    
    # Deactivate all workshops
    c.execute('UPDATE workshops SET is_active = 0')
    
    # Activate selected workshop
    c.execute('UPDATE workshops SET is_active = 1 WHERE id = ?', (workshop_id,))
    
    conn.commit()
    conn.close()
    
    flash('Workshop activated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/register')
def register():
    workshop = get_active_workshop()
    if not workshop:
        return render_template('no_workshop.html')
    
    # Convert workshop tuple to dict for easier access
    workshop_dict = {
        'id': workshop[0],
        'date': workshop[1],
        'topic': workshop[2],
        'instructor': workshop[3],
        'time': workshop[4],
        'price': workshop[5],
        'max_participants': workshop[6]
    }
    
    # Get current registration count
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM registrations WHERE workshop_id = ?', (workshop[0],))
    current_count = c.fetchone()[0]
    conn.close()
    
    return render_template('register.html', 
                         workshop=workshop_dict, 
                         current_count=current_count)

@app.route('/register', methods=['POST'])
def handle_registration():
    workshop = get_active_workshop()
    if not workshop:
        flash('No active workshop available', 'error')
        return redirect(url_for('register'))
    
    # Check if workshop is full
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM registrations WHERE workshop_id = ?', (workshop[0],))
    current_count = c.fetchone()[0]
    
    if current_count >= workshop[6]:  # max_participants
        flash('Sorry, this workshop is fully booked!', 'error')
        return redirect(url_for('register'))
    
    # Register participant
    name = request.form['name']
    email = request.form['email']
    phone = request.form.get('phone', '')
    company = request.form.get('company', '')
    experience = request.form['experience']
    
    c.execute('''INSERT INTO registrations (workshop_id, name, email, phone, company, experience_level)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (workshop[0], name, email, phone, company, experience))
    
    conn.commit()
    conn.close()
    
    return render_template('success.html', name=name, workshop=workshop)

@app.route('/admin/registrations')
def view_registrations():
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute('''SELECT r.*, w.topic, w.date 
                 FROM registrations r 
                 JOIN workshops w ON r.workshop_id = w.id 
                 ORDER BY r.registration_date DESC''')
    registrations = c.fetchall()
    conn.close()
    
    return render_template('registrations.html', registrations=registrations)

@app.route('/admin/export_csv')
def export_csv():
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute('''SELECT r.name, r.email, r.phone, r.company, r.experience_level, 
                        w.topic, w.date, w.time, r.registration_date
                 FROM registrations r 
                 JOIN workshops w ON r.workshop_id = w.id 
                 ORDER BY r.registration_date DESC''')
    
    registrations = c.fetchall()
    conn.close()
    
    # Create CSV response
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Email', 'Phone', 'Company', 'Experience Level', 
                    'Workshop Topic', 'Workshop Date', 'Workshop Time', 'Registration Date'])
    
    # Write data
    for reg in registrations:
        writer.writerow(reg)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=aws_workshop_registrations_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

@app.route('/api/workshop_status')
def workshop_status():
    workshop = get_active_workshop()
    if not workshop:
        return jsonify({'status': 'no_workshop'})
    
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM registrations WHERE workshop_id = ?', (workshop[0],))
    current_count = c.fetchone()[0]
    conn.close()
    
    return jsonify({
        'status': 'active',
        'current_count': current_count,
        'max_participants': workshop[6],
        'spots_remaining': workshop[6] - current_count
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)