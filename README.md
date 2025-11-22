# Rezo: Campus Asset Management System

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
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4.  **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

5.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## Accounts

You can use the following credentials to log in to the admin account:

*   **Username:** `admin`
*   **Password:** `kulafu31`

## Templates and Libraries Used

*   **Login Design/Template:** The login form design is from [Uiverse.io](https://uiverse.io/) by [micaelgomestavares](https://uiverse.io/micaelgomestavares).
*   **UI Library:** [DaisyUI](https://daisyui.com/) is used for the user interface components.
*   **Remix icon:** [RemixIcon](https://remixicon.com/) Icon Library.
    