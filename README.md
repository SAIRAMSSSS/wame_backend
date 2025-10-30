# WAME Backend 🌐

This is the backend repository for the **WAME** application. It provides the API endpoints, business logic, and database management for the frontend client, built using **Django** and **Django REST Framework**.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* pip (Python package installer)
* Git

### Installation

Follow these steps to set up and run the server locally:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/SAIRAMSSSS/wame_backend.git](https://github.com/SAIRAMSSSS/wame_backend.git)
    cd wame_backend
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Database setup:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API should now be running at `http://127.0.0.1:8000/`.

---

## ⚙️ Configuration

The project uses environment variables for sensitive settings.

### Environment Variables

Create a file named **`.env`** in the root directory (outside of any app folders) and add the following:
