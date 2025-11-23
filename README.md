# Rezo: Campus Asset Management System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34C26?style=for-the-badge&logo=html5&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

Rezo is a campus asset management system designed to track university-owned equipment, including borrowing, repairs, and disposal.

## Roles

The system has the following user roles:

*   **Admin:** Manages the entire system, including users and assets.
*   **Staff:** Manages assets, including checking them in and out.
*   **End-user:** Can view and borrow assets.

## Features

*   **Asset Registration:** Register new assets in the system.
*   **Requisition:** Users can request to borrow assets.
*   **Repairs Log:** Track the repair history of assets.
*   **Disposal Tracking:** Track the disposal of assets.
*   **Reports:** Generate reports on asset usage and history.

## Getting Started

To get started with Rezo, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/rezo.git
    cd rezo
    ```

2.  **Create and activate virtual environment:**

    ```bash
    python -m venv myenv
    source myenv/bin/activate  # On Windows: myenv\Scripts\activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

   The app will be available at `http://127.0.0.1:8000/`

## Demo Credentials

**Admin Account:**
*   **Username:** `admin`
*   **Password:** `kulafu31`

**User Account:**
*   **Username:** `user@user.user`
*   **Password:** `Passw0rd123`

**User Account:**
*   **Username:** `staff`
*   **Password:** `staff`
## Tech Stack

*   **Backend:** Django 5.2.8
*   **Frontend:** HTML5, Tailwind CSS, JavaScript
*   **Database:** SQLite
*   **UI Components:** DaisyUI

## Templates and Libraries Used

*   **Forms Template:** [Uiverse.io](https://uiverse.io/)
     [micaelgomestavares](https://uiverse.io/micaelgomestavares).
     <!-- From Uiverse.io by themrsami -->  
*   **UI Library:** [DaisyUI](https://daisyui.com/) - Tailwind CSS component library.
*   **CSS Framework:** [Tailwind CSS](https://tailwindcss.com/)
*   **Icons:** [RemixIcon](https://remixicon.com/) Icon Library.

## Project Structure

```
rezo/
├── manage.py
├── rezo/                 # Main project settings
├── inventory/            # Asset inventory app
├── accounts/             # User authentication app
├── templates/            # HTML templates
│   ├── base.html
│   ├── auth_base.html
│   └── accounts/
└── static/               # CSS, JS, images
    ├── css/
    │   └── output.css    # Tailwind compiled CSS
    └── js/
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.

<div align='center'>
  
![Jsut a gif](https://media.giphy.com/media/VncQh8IPag1v1cgcCv/giphy.gif)

</div>