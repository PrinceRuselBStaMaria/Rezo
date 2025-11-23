# Rezo: Campus Asset Management System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34C26?style=for-the-badge&logo=html5&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

Rezo is a campus asset management system designed to track university-owned equipment, including borrowing, repairs, and disposal.

## 🎬 Demo Videos & GIFs

<div align="center">

### Sample Landing 
![Sample Landing ](./static/readme/sample.GIF)

### Sample List
![Sample List](./static/readme/sample2.GIF)

<div align="center">

<video width="700" height="500" controls>
  <source src="./static/readme/sample.webm" type="video/webm">
  Your browser does not support the video tag.
</video>


</div>
</div>

---


## 🎯 Roles

The system has the following user roles:

* **Admin:** Manages the entire system, including users and assets.
* **Staff:** Manages assets, including approval and returns.
* **End-user:** Can view and borrow assets.

## ✨ Features

* **Asset Registration:** Register new assets in the system.
* **Borrowing System:** Users can request to borrow assets with staff approval.
* **Maintenance Log:** Track the repair history of assets.
* **Disposal Tracking:** Track the disposal of assets.
* **Reports:** Generate reports on asset usage and history.
* **Guest Access:** Browse available equipment without login.

## 🚀 Getting Started

To get started with Rezo, follow these steps:

### 1. Clone the repository

```bash
git clone https://github.com/your-username/rezo.git
cd rezo
```

### 2. Create and activate virtual environment

```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`

---

## 👤 Demo Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `kulafu31`

### Staff Account
- **Username:** `staff`
- **Password:** `staff`

### User Account
- **Username:** `user@user.user`
- **Password:** `Passw0rd123`

---

## 🛠️ Tech Stack

* **Backend:** Django 5.2.8
* **Frontend:** HTML5, Tailwind CSS, JavaScript
* **Database:** SQLite
* **UI Components:** DaisyUI
* **Image Processing:** Pillow

---

## 📚 Templates and Libraries Used

* **UI Library:** [DaisyUI](https://daisyui.com/) - Tailwind CSS component library
* **CSS Framework:** [Tailwind CSS](https://tailwindcss.com/)
* **Icons:** [RemixIcon](https://remixicon.com/) - Icon Library
* **Forms Template:** [Uiverse.io](https://uiverse.io/) by [micaelgomestavares](https://uiverse.io/micaelgomestavares)
* **Images:** [Unsplash](https://unsplash.com/)
  - simone-hutsch-_wpce-AsLxk-unsplash
  - jakub-zerdzicki-gJ8bkUlUFkY-unsplash
  - nikita-kachanovsky-OVbeSXRk_9E-unsplash

---

## 🔄 System Architecture

### Two-App Design

**accounts/** - Authentication & User Management
- User login/registration
- Staff management
- Role-based access control

**inventory/** - Asset Management
- Equipment tracking
- Borrowing system
- Maintenance & disposal

---

## 📖 How to Use

### For Regular Users

1. **Browse Equipment** (no login required)
   - Visit homepage → Click "Browse Equipment as Guest"
   - Or login for additional features

2. **Request to Borrow**
   - Select equipment → Click "Borrow Now"
   - Submit quantity → Request sent to staff

3. **Track Borrowings**
   - Go to "My Borrowings"
   - View pending, active, and returned items

4. **Return Equipment**
   - Click "Return" on active borrowing
   - Equipment back in stock

### For Staff

1. **Manage Requests**
   - Dashboard → "Manage Requests"
   - Approve or reject pending requests

2. **Process Returns**
   - Dashboard → "Manage Returns"
   - Confirm items returned

3. **Create Maintenance**
   - Mark equipment for repair
   - Track maintenance history

4. **Dispose Assets**
   - Retire old equipment
   - Record disposal reason

### For Admin

- Full system access
- User management
- Generate reports
- Access Django admin panel

---

## 📞 Support

For issues or questions, please create an issue on GitHub.

---

<div align='center'>

![Just a gif](https://media.giphy.com/media/VncQh8IPag1v1cgcCv/giphy.gif)

**Made with ❤️ for Campus Equipment Management**

</div>