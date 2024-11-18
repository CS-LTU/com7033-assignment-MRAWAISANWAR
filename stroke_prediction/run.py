#run.py
from app import create_app
 
app = create_app()
 # Register the patient blueprint

if __name__ == '__main__':
    app.run(debug=True)
