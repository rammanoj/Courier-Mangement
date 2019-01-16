

**Amrita courier management system** :

A web application to efficiently manage the courier operations in the campus.

- This provides easy and fast access(search) of couriers to the courier office operator and deliver them easily.
- Provides the student timely notifications and secure delivery with pin verification.

**Motivation** :

The courier details are being written manually in a book which is making it difficult for the students to search for their name in the register and collect it.

**Details of the project :**

This applications has three types of users:

1. The administrator
2. Courier office operator
3. Student/faculty

The admin has access to all the couriers and also has the functionalities of courier  operator enables to him(deliver the couriers to students).

 The administrator should accept registration request of  the courier operator .

 The courier operator has powers to enter the details of a new parcel arrived and deliver the package after verification of the student/faculty .

A student has a dashboard which lists out all the couriers and its details of his packages.

A student has to set a pin for himself which he will be entering in the courier office for validation.

Student can reset/modify his pin if he wishes to.

Once a delivery entered into the database by the courier operator the student is notified about his parcel through email.

**Installation:**

The website is easy to install, follow these instructions to complete the installation:

1. Clone the code with the command
  1. git clone [https://github.com/rammanoj/Courier-Mangement](https://github.com/rammanoj/Courier-Mangement)
2. Rename the root directory, Courier-Management to parcelmanage.
3. Go to this [link](https://www.digitalocean.com/community/tutorials/how-to-install-django-and-set-up-a-development-environment-on-ubuntu-16-04), and follow the instructions to install the **pip** along with the virtual environment.
4. Then activate the virtual environment.
5. Install the requirements with the following command
  1. pip install -r requirements.txt
6. Then, run the migrations with the following migrations with the following commands in the root directory of the project.
  1. python manage.py makemigrations
  2. python manage.py migrate
7. Finally, run the command to start the server,
  1. python manage.py runserver
8. Go to the link [http://127.0.0.1/accounts/login](http://127.0.0.1/accounts/login)/

