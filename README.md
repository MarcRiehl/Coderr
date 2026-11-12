# Coderr – Offers and Orders API

![Coderr Logo](assets/logo/logo_coderr.svg)

## About the Project

Coderr is a RESTful backend application developed with **Python and Django REST Framework (DRF)**.

The platform connects customers with business users who offer services. Customers can browse offers, compare different packages, place orders and leave reviews. Business users can manage their offers and process incoming orders.

The API provides user authentication, profile management, offer management, order processing, reviews and platform statistics.

### Technologies

- Python
- Django
- Django REST Framework
- Token Authentication
- SQLite
- Git

---

## Requirements

Before installing the project, make sure you have the following installed:

- **Python 3:** [Download Python](https://www.python.org/downloads/)
- **Git:** [Download Git](https://git-scm.com/downloads)
- A terminal, such as Windows PowerShell or the integrated terminal in VS Code
- A code editor, such as [Visual Studio Code](https://code.visualstudio.com/)

---

## Installation

Follow the instructions for your operating system.

### 1. Install Python

**Windows**

1. Download Python from [python.org](https://www.python.org/downloads/).
2. Run the installer.
3. Enable **Add Python to PATH** during installation.
4. Complete the installation.

Verify the installation in PowerShell:

```powershell
python --version
pip --version
```

If `python` is not recognized, try:

```powershell
py --version
```

**macOS**

1. Download Python from [python.org](https://www.python.org/downloads/macos/).
2. Open the downloaded installer and follow the instructions.
3. Open the Terminal application.

Verify the installation:

```bash
python3 --version
python3 -m pip --version
```

### 2. Install Git

**Windows**

1. Download Git from [git-scm.com](https://git-scm.com/downloads).
2. Run the installer and follow the recommended default settings.
3. Open PowerShell or the VS Code terminal.

Verify the installation:

```powershell
git --version
```

**macOS**

Git can be installed using Apple's Command Line Tools.

Open Terminal and run:

```bash
git --version
```

If Git is not installed, macOS may prompt you to install the Command Line Tools. Follow the instructions.

Alternatively, download Git from [git-scm.com](https://git-scm.com/downloads/mac).

## Project Setup

### 3. Clone the repository

Open your terminal or PowerShell and navigate to the directory where you want to store the project.

Clone the repository:

```bash
git clone https://github.com/MarcRiehl/Coderr.git
```

Navigate into the project directory:

```bash
cd coderr
```

### 4. Create a virtual environment

A virtual environment keeps the project's dependencies separate from other Python projects.

**Windows:**

```bash
python -m venv env
```

Activate the environment:

```bash
env\Scripts\activate
```

**macOS:**

```bash
python3 -m venv env
```

Activate the environment:

```bash
source env/bin/activate
```

### 5. Install Dependencies

Make sure the virtual environment is activated.

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

The `requirements.txt` file must be present in the project root and contain all required Python packages.

### 6. Configure Environment Variables

Before starting the server, create a `.env` file in the project root directory, at the same level as `manage.py`.

The application uses environment variables to configure Django. A valid `SECRET_KEY` must be provided, otherwise the server will raise a `ValueError`.

Create a file named `.env` and add the following variable:

```dotenv
SECRET_KEY='your-secret-key'
```

Replace `your-secret-key` with a secure, randomly generated secret key.

You can generate a new Django secret key using the following command:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated key into your `.env` file:

```dotenv
SECRET_KEY='your-generated-secret-key'
```

Make sure the `.env` file is loaded by your Django settings using `load_dotenv()`.

**Important:** Never commit your `.env` file or secret keys to GitHub. Add the following entries to your `.gitignore` file:

```gitignore
.env
venv/
__pycache__/
*.py[cod]
db.sqlite3
```

Each developer must create their own local `.env` file before starting the application.

### 7. Apply database migrations

Run the following commands to prepare the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Start the development server

Start the Django development server:

```bash
python manage.py runserver
```

The API is now available at:

```text
http://127.0.0.1:8000/
```

You can access the API endpoints using Postman or your preferred API client.

To stop the server, press `CTRL + C` in your terminal.

---

### 9. Additional Information

- Activate the virtual environment whenever you open a new terminal to work on the project.
- On macOS, use `python3` to create the virtual environment if `python` is not available.
- On Windows, use `python` or `py` to create the virtual environment.
- Make sure `requirements.txt` is up to date before sharing the project.
- Never commit virtual environments, secret keys or sensitive credentials to GitHub.

## API Routes

The following table provides an overview of the available API endpoints.

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/api/registration/` | Register a new user | No |
| POST | `/api/login/` | Authenticate a user and obtain a token | No |
| GET | `/api/profile/{pk}/` | Retrieve a user profile | Yes |
| PATCH | `/api/profile/{pk}/` | Update a user profile | Yes |
| GET | `/api/profiles/business/` | Retrieve business profiles | Yes |
| GET | `/api/profiles/customer/` | Retrieve customer profiles | Yes |
| GET | `/api/offers/` | Retrieve all offers | No |
| POST | `/api/offers/` | Create a new offer | Yes |
| GET | `/api/offers/{id}/` | Retrieve a specific offer | Yes |
| PATCH | `/api/offers/{id}/` | Update an offer | Yes |
| DELETE | `/api/offers/{id}/` | Delete an offer | Yes |
| GET | `/api/offers/{id}/` | Delete an offer | Yes |
| GET | `/api/offerdetails/{id}/` | Retrieve a specific offerdetail | Yes |
| GET | `/api/orders/` | Retrieve all offers | Yes |
| POST | `/api/orders/` | Create a new order | Yes |
| PATCH | `/api/orders/{id}/` | Update an order status | Yes |
| GET | `/api/order-count/{business_user_id}/` | Retrieve the number of in-progress orders | Yes |
| GET | `/api/completed-order-count/{business_user_id}/` | Retrieve the number of completed orders | Yes |
| GET | `/api/reviews/` | Retrieve reviews | Yes |
| POST | `/api/reviews/` | Create a review | Yes |
| PATCH | `/api/reviews/{id}/` | Update a review | Yes |
| DELETE | `/api/reviews/{id}/` | Delete a review | Yes |
| GET | `/api/base-info/` | Retrieve general platform statistics | No |

**Notes:**

- `{pk}` represents the unique user profile ID.
- `{id}` represents the unique resource ID.
- `{business_user_id}` represents the ID of a business user.
- Authenticated endpoints require a valid authentication token.
- Offers can only be created and managed by their respective business owners.
- Orders cannot be deleted, including by administrators.
- Reviews can only be modified or deleted according to the implemented ownership permissions.

---

## Authentication

Coderr uses Django REST Framework Token Authentication.

After successfully logging in, the API returns an authentication token.

For protected endpoints, include the token in the request headers:

```http
Authorization: Token YOUR_AUTH_TOKEN
```

Replace `YOUR_AUTH_TOKEN` with the token returned by the login endpoint.

---

## License

This project was created exclusively as part of the Developer Akademie training program. It is intended for educational and demonstration purposes only and is not licensed for free use, distribution, modification, or redistribution without prior permission from the author.
