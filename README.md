# JobTrack – Job Application Tracker

JobTrack is a web-based job application tracking system developed using Python, Flask, HTML, CSS, JavaScript, and SQLite.

It helps job seekers organize their job applications, monitor application statuses, schedule interviews, and analyze their job search progress through a dashboard.

## Features

- Dashboard with application and interview statistics.
- Add, edit, and delete job applications.
- Search and filter applications.
- Track application statuses.
- Schedule and manage interviews.
- Search and filter interviews.
- Interview pagination and application pagination.
- Analytics dashboard with interactive charts.
- Export job applications to Excel.
- Form validation for reliable data entry.
- Responsive interface for desktop and mobile devices.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| SQLAlchemy | Database management |
| HTML | Page structure |
| CSS | Styling and responsive design |
| JavaScript | Frontend interactions |
| Chart.js | Analytics charts |
| OpenPyXL | Excel export |

## Project Structure

```text
JobTrack/
│
├── app.py
├── models.py
├── extensions.py
├── requirements.txt
├── check_db.py
├── check_data.py
├── check_interview.py
│
├── database/
│   └── jobtrack.db
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── add_application.html
│   ├── applications.html
│   ├── edit_application.html
│   ├── interviews.html
│   ├── add_interview.html
│   ├── edit_interview.html
│   └── analytics.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── screenshots/
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project folder

```bash
cd JobTrack
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## Future Enhancements

- User authentication.
- Email notifications for upcoming interviews.
- Advanced job search analytics.
- Cloud database integration.

## Author

Developed as a practical full-stack web development project using Python and web technologies.