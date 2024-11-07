from app import create_app
from app.views.patient import patient_bp

app = create_app()
app.register_blueprint(patient_bp, url_prefix='/patient')  # Register the patient blueprint

if __name__ == '__main__':
    app.run(debug=True)
