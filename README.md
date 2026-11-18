
# Student Fee Management System

A web-based Student Fee Management System developed using Django and Python. This application helps manage student registration, fee payments, payment history, and receipt generation through a simple interface.

## Features

- Student Registration and Login
- Student Dashboard
- Admin Dashboard
- Student Fee Details
- Fee Payment Management
- Payment History
- PDF Receipt Generation
- Secure Student Authentication
- Django Admin Panel

## Technologies Used

- Python
- Django
- SQLite
- HTML
- CSS
- Bootstrap (if used in the project)
- ReportLab (PDF Receipt Generation)

## Project Structure

```text
StudentFeeManagement/
│
├── config/
├── students/
├── fees/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/isharawat-01/Student_Fee_Management.git
```

### 2. Open Project Folder

```bash
cd Student_Fee_Management
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

Windows:

```powershell
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
```

Replace the placeholder with your own Django secret key.

### 7. Run Database Migrations

```bash
python manage.py migrate
```

### 8. Start Development Server

```bash
python manage.py runserver
```

Open your browser:

http://127.0.0.1:8000/

## Application Modules

**Student Module**
- Register and log in.
- View fee details.
- Track paid and remaining fees.
- View payment history.
- Download payment receipts.

**Admin Module**
- View student records.
- Monitor fee collection.
- Add fee payments.
- Manage payment records.
- Generate PDF receipts.

## Author

**Isha Rawat**

MCA Student

GitHub: [isharawat-01](https://github.com/isharawat-01)

---

If you find this project useful, feel free to explore the repository.
