### Matthew Baer - Capstone Project: "ROUTINE" Readme

<br>

**This project is deployed here:**

- https://routine.onrender.com/

<br>

**Purpose**

The _Routine_ web application is designed to simplify the process of planning a workout and empower users to visualize their progress towards their fitness goals through a very simple and straightforward user interface.

_Routine_ relies on the wger.de API to seed the database with exercise names and descriptions from which the user can choose and add to a workout.

<br>

**Functionality**

_Routine_ allows a user to:

- Sign up
- Browse other user's workouts
- Copy other user's workouts
- Create their own workouts
- Add goals to every workout that sets a target for:
    - Reps
    - Sets
    - Weight
    - Time
    - Distance

Every time a user performs a workout _Routine_ will present the user with a guided editor where they will enter in their performance against these goals.

After the user has finished the workout they will be presented with line-graph visualizations for each goal and their progress toward achieving that goal.

<br>

**Technology**

_Routine_ is a Python application which uses a Flask web framework that performs CRUD operations on a SQL database.

Additional libraries used are:

- PostgreSQL
- SQLAlchemy
- WTForms
- Jinja Templates
- Chart.js
- Bootstrap

Tests are run with Python Unittest.

<br>

**API Used To Seed Exercises: wger.de**

 - https://wger.de/en/software/api?ref=apilist.fun

<br>
<br>