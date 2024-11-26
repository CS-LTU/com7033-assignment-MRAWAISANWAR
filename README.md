# 🏥 StrokeWatch

A Flask-based healthcare application that combines machine learning with patient management for stroke risk assessment.

## ✨ Features

- User authentication with role-based access (Admin, Doctor, Staff)
- Patient data management and search
- Real-time stroke risk prediction using ML
- Secure data handling with dual database system
- Modern, responsive interface

## 🛠️ Tech Stack

- **Backend**: Flask 3.1.0, SQLAlchemy, MongoEngine
- **Databases**: SQLite, MongoDB
- **ML**: TensorFlow, Keras
- **Security**: Bcrypt, CSRF Protection
- **Frontend**: HTML, CSS, JavaScript

## 🚀 Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/CS-LTU/com7033-assignment-MRAWAISANWAR.git
   cd strokewatch
   ```

2. **Set up Python environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix
   venv\Scripts\activate     # Windows
   ```

3. **Install requirements**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment**

   ```bash
   # Create .env file with:
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   SQLITE_DATABASE_URI=sqlite:///stroke_prediction.db
   MONGO_URI=mongodb://localhost:27017/stroke_prediction
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.
