# Courier Management System 
The Courier Management System is a scalable RESTful backend API built with Django & Django REST Framework (DRF).  
It allows users to place and track courier orders, delivery men to manage their assigned orders, and admins to manage the entire system.  
Integrated with Stripe for secure payments.

---
---

## Features
- JWT Authentication { Register, Login, Profile (view and  update) }
- Roles: Admin, Delivery Man, User
- Order Management

  - USER:
    - can create orders. 
    - can track orders.
    - can view only his all and single orders.
    - can update and delete order.

  - DELIVERY MAN:
    - can update status of assigned orders.
    - can track assigned orders orders.
    - can view assigned orders orders.

  - Admin
    - Admins has all the power.
    - Only Admin has permission to assign delivery man

- Payments
  - Secure payments using Stripe Checkout.
  - Payment success and cancel option
  - Payment during order creation or later.

- Tracking
  - Status updates with tracking history.

---



## Relationship Diagram
[View ERD Diagram](https://dbdiagram.io/d/Courier-Management-System-DB-Diagram-68ca3a0452b325f10768fec9)

---

## Live API (Remember DEBUG is TRUE)
Base URL: [https://courier-management-system-yqna.onrender.com](  https://courier-management-system-yqna.onrender.com)

---

## Github Link
Base URL : [https://github.com/AzizurRahamanGithub/Courier-Management-System.git]( https://github.com/AzizurRahamanGithub/Courier-Management-System.git)


---

## Postman Collection
[Postman Workspace Collection](https://drive.google.com/drive/folders/1-wq97OGBpMZR--V84AiXZDzTIVg8-RSo?usp=sharing)

---

## Login Credentials (Demo)

| Role         | username       | Password   |
|--------------|------------------------|------------|
| Super User        | admin      | 0000   |
| Admin        | admin2      | A016461a   |
| Delivery Man |   delivery2 | A123456a|
| User         | user1      | A123456a    |

---

## Setup Instructions

1. Clone the repository  
   ```bash
   git clone https://github.com/AzizurRahamanGithub/Courier-Management-System.git
   
   ##then 

   cd Courier-Management-System

---

2. Make Virtual Environment then activate
   ```bash
   python -m venv venv

   source venv/bin/activate
---

3. Install dependencies
   ```bash
   pip install -r requirements.txt 

---

4. Apply migrations
   ```bash
   python manage.py makemigrations

   python manage.py migrate   

---

5. Run Project
   ```bash
   python manage.py runserver   
