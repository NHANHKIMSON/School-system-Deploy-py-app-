import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Use environment variable for database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://crud_py_user:BThsvgJOW8m46DdUslTzu4kEuvvnfWEp@dpg-ctaoo823esus739c1jo0-a.oregon-postgres.render.com/crud_py'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)





# Define Contact Model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    score_i = db.Column(db.Float, nullable=False)
    score_ii = db.Column(db.Float, nullable=False)
    score_iii = db.Column(db.Float, nullable=False)
    
    # Separate sections for psychical and chemistry
    psychical_score = db.Column(db.Float, nullable=False)  # Psychical score
    chemistry_score = db.Column(db.Float, nullable=False)  # Chemistry score
    
    total_score = db.Column(db.Float, nullable=False)
    avg = db.Column(db.Float, nullable=True)
    grade = db.Column(db.String(1), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True)

# # Initialize Database
# with app.app_context():
#     db.create_all()


with app.app_context():
    try:
        db.create_all()  # This will create tables if they don't exist
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")

@app.route('/')
def index():
    added = request.args.get('added', False)  # Check if 'added' flag is in the URL
    
    # Query all students, ordered by total_score descending
    contacts = Contact.query.order_by(Contact.total_score.desc()).all()
    
    # Assign rankings dynamically
    ranked_contacts = [(index + 1, contact) for index, contact in enumerate(contacts)]
    
    return render_template('index.html', ranked_contacts=ranked_contacts, added=added)



# Add Contact
@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        sex = request.form['sex']
        score_i = float(request.form['score_i'])
        score_ii = float(request.form['score_ii'])
        score_iii = float(request.form['score_iii'])
        
        # Capture psychical and chemistry scores
        psychical_score = float(request.form['psychical_score'])
        chemistry_score = float(request.form['chemistry_score'])

        total_score = score_i + score_ii + score_iii + psychical_score + chemistry_score  # Update total score calculation
        avg = round(total_score / 5)  # Update average calculation (since you have 5 scores)

        # Determine grade and status
        if avg > 90:
            grade = "A"
            status = "Perfect 🤩!"
        elif avg > 80:
            grade = "B"
            status = "Very Good!"
        elif avg > 70:
            grade = "C"
            status = "Good!"
        elif avg > 60:
            grade = "D"
            status = "Needs Improvement"
        elif avg > 50:
            grade = "E"
            status = "Poor"
        else:
            grade = "F"
            status = "Fail 😢"

        # Create the new contact
        new_contact = Contact(
            name=name,
            sex=sex,
            score_i=score_i,
            score_ii=score_ii,
            score_iii=score_iii,
            psychical_score=psychical_score,
            chemistry_score=chemistry_score,
            total_score=total_score,
            avg=avg,
            grade=grade,
            status=status,
            phone=request.form['phone'],
            email=request.form['email']
        )
        db.session.add(new_contact)
        db.session.commit()
        return redirect(url_for('index', added=True))
    return render_template('add_contact.html')



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return redirect(url_for('index'))

    if request.method == 'POST':
        contact.name = request.form['name']
        contact.sex = request.form['sex']
        contact.score_i = float(request.form['score_i'])
        contact.score_ii = float(request.form['score_ii'])
        contact.score_iii = float(request.form['score_iii'])
        
        # Update psychical and chemistry scores
        contact.psychical_score = float(request.form['psychical_score'])
        contact.chemistry_score = float(request.form['chemistry_score'])
        
        contact.phone = request.form['phone']
        contact.email = request.form['email']

        # Recalculate total score and average
        contact.total_score = contact.score_i + contact.score_ii + contact.score_iii + contact.psychical_score + contact.chemistry_score
        contact.avg = round(contact.total_score / 5)

        # Recalculate grade and status
        if contact.avg > 90:
            contact.grade = "A"
            contact.status = "Perfect 🤩!"
        elif contact.avg > 80:
            contact.grade = "B"
            contact.status = "Very Good!"
        elif contact.avg > 70:
            contact.grade = "C"
            contact.status = "Good!"
        elif contact.avg > 60:
            contact.grade = "D"
            contact.status = "Needs Improvement"
        elif contact.avg > 50:
            contact.grade = "E"
            contact.status = "Poor"
        else:
            contact.grade = "F"
            contact.status = "Fail 😢"

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_contact.html', contact=contact)


# Delete Contact
@app.route('/delete/<int:id>')
def delete_contact(id):
    contact = Contact.query.get(id)
    if contact:
        db.session.delete(contact)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
