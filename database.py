from app import app,db

#Create database
with app.app_context():
    db.create_all()