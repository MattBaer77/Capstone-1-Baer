"""Seed database with sample data and data from API."""

# from csv import DictReader
from app import db
from models import Exercise, User, Workout, Goal, Performance
from fetch_wger_exercises import *
from secrets import *


db.drop_all()
db.create_all()

# Add exercises - from API Call
data = wger_fetch("wger_fetch_from_seed_file", "A", 10000)

for each in data:
    exercise = Exercise(name=each["name"], description=each["description"])
    db.session.add(exercise)

db.session.commit()

# Add users
routine_user_1 = User.signup(email='routine_user1@routinefauxemail.com', username='Routine User 1', password=faux_password_1)
routine_user_2 = User.signup(email='routine_user2@routinefauxemail.com', username='Routine User 2', password=faux_password_2)
routine_user_3 = User.signup(email='routine_user3@routinefauxemail.com', username='Routine User 3', password=faux_password_3)
routine_user_4 = User.signup(email='routine_user4@routinefauxemail.com', username='Routine User 4', password=faux_password_4)
routine_user_5 = User.signup(email='routine_user5@routinefauxemail.com', username='Routine User 5', password=faux_password_5)

db.session.commit()

# Add workouts
user_1_workout = Workout.create(description='Sample Workout 1', owner_user_id='1')
user_2_workout = Workout.create(description='Sample Workout 2', owner_user_id='2')
user_3_workout = Workout.create(description='Sample Workout Empty', owner_user_id='5')

db.session.commit()

# Add goals
user_1_workout_goal_1 = Goal(workout_id=1, exercise_id=1, goal_reps=10, goal_sets=2, goal_weight_lbs=30, goal_time_sec=45)
user_1_workout_goal_2 = Goal(workout_id=1, exercise_id=2, goal_reps=20, goal_sets=2, goal_weight_lbs=20)
user_1_workout_goal_3 = Goal(workout_id=1, exercise_id=3, goal_reps=30, goal_sets=3, goal_distance_miles=30)
user_1_workout_goal_4 = Goal(workout_id=1, exercise_id=4, goal_reps=40, goal_sets=4)
user_1_workout_goal_5 = Goal(workout_id=1, exercise_id=5, goal_reps=50, goal_sets=5)

user_2_workout_goal_1 = Goal(workout_id=2, exercise_id=1, goal_reps=10, goal_sets=1, goal_time_sec=10)
user_2_workout_goal_2 = Goal(workout_id=2, exercise_id=2, goal_reps=20, goal_sets=2, goal_weight_lbs=20)

db.session.add_all([

    user_1_workout_goal_1,
    user_1_workout_goal_2,
    user_1_workout_goal_3,
    user_1_workout_goal_4,
    user_1_workout_goal_5,
    user_2_workout_goal_1,
    user_2_workout_goal_2

])
db.session.commit()

# Add performance
user_1_workout_goal_1_performance_1 = Performance(goal_id=1, performance_reps=10, performance_sets=1, performance_weight_lbs=20, performance_time_sec=80)
user_1_workout_goal_1_performance_2 = Performance(goal_id=1, performance_reps=10, performance_sets=1, performance_weight_lbs=20, performance_time_sec=70)
user_1_workout_goal_1_performance_3 = Performance(goal_id=1, performance_reps=10, performance_sets=1, performance_weight_lbs=20, performance_time_sec=60)
user_1_workout_goal_1_performance_4 = Performance(goal_id=1, performance_reps=10, performance_sets=1, performance_weight_lbs=30, performance_time_sec=50)

user_1_workout_goal_2_performance_1 = Performance(goal_id=2, performance_reps=10, performance_sets=1, performance_weight_lbs=10)
user_1_workout_goal_2_performance_2 = Performance(goal_id=2, performance_reps=11, performance_sets=2, performance_weight_lbs=20)
user_1_workout_goal_2_performance_3 = Performance(goal_id=2, performance_reps=12, performance_sets=3, performance_weight_lbs=30)

db.session.add_all([

    user_1_workout_goal_1_performance_1,
    user_1_workout_goal_1_performance_2,
    user_1_workout_goal_1_performance_3,
    user_1_workout_goal_1_performance_4,
    user_1_workout_goal_2_performance_1,
    user_1_workout_goal_2_performance_2,
    user_1_workout_goal_2_performance_3

])

db.session.commit()

# Copy a workout
workout_to_copy=Workout.query.get(1)

Workout.copy(workout_to_copy, 3)

