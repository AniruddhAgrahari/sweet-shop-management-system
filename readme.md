# Sweet Shop Management System 🍬

A full-stack web application for managing a sweet shop inventory, sales, and user authentication. Built with **FastAPI** (Backend) and **React + Vite** (Frontend).

## 🚀 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (via SQLModel)
- **Authentication**: OAuth2 with Password Flow (JWT)
- **Testing**: Pytest
- **Security**: PassLib (pbkdf2_sha256 hashing)

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Custom CSS (Responsive, Modern UI)
- **HTTP Client**: Axios
- **Routing**: React Router DOM

## ✨ Features

- **User Authentication**: Secure Register and Login functionality using JWT.
- **Dashboard**: Interactive dashboard to view available sweets.
- **Inventory Management**:
  - View all sweets with details (Name, Category, Price, Stock).
  - **Admin Feature**: Add new sweets to the inventory.
- **Purchase System**:
  - Buy sweets directly from the dashboard.
  - Real-time stock updates.
  - "Out of Stock" handling (disables purchase button).
- **Responsive Design**: Works seamlessly on desktop and mobile devices.

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js & npm

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the server:
```bash
uvicorn main:app --reload --port 8000
```
The API will be available at `http://127.0.0.1:8000`.
Swagger UI documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

Navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Run the development server:
```bash
npm run dev
```
The application will typically run at `http://localhost:5173` (or similar).

## 📖 Usage

1.  **Register**: Create a new account via the API or (future) UI.
    *   *Note: Currently, you can register via Swagger UI at `/auth/register`.*
2.  **Login**: Use the Login page on the frontend to authenticate.
3.  **Dashboard**:
    *   View the grid of sweets.
    *   Click **"Buy Now"** to purchase an item (decreases stock).
    *   Click **"Add New Sweet"** (Admin) to open the form and add new inventory.
4.  **Logout**: Click the Logout button in the navbar to end the session.

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user | No |
| `POST` | `/auth/login` | Login and get JWT token | No |
| `GET` | `/sweets/` | Get all sweets | Yes |
| `POST` | `/sweets/` | Create a new sweet | Yes |
| `GET` | `/sweets/{id}` | Get sweet details | Yes |
| `PUT` | `/sweets/{id}` | Update a sweet | Yes |
| `DELETE` | `/sweets/{id}` | Delete a sweet | Yes |
| `POST` | `/sweets/{id}/purchase` | Purchase a sweet (decrement stock) | Yes |

## 🧪 Testing

The backend includes a comprehensive test suite using `pytest`.

Run tests:
```bash
cd backend
pytest
```

Generate HTML Report:
```bash
pytest --html=report.html --self-contained-html
```

## 📂 Project Structure

```
Sweet shop management system/
├── backend/
│   ├── main.py           # API entry point & endpoints
│   ├── models.py         # Database models (Sweet, User)
│   ├── database.py       # DB connection & session
│   ├── security.py       # Auth utilities (Hash, JWT)
│   ├── test_main.py      # Integration tests
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components (Dashboard, Login)
│   │   ├── App.jsx       # Main App component & Routing
│   │   └── dashboard.css # Styles
│   └── package.json      # Node dependencies
└── readme.md             # Project documentation
```
