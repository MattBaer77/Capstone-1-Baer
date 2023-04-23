"""Seed database with sample data and data from API."""

# from csv import DictReader
from app import db
from models import Exercise, User, Workout, Goal, Performance


db.drop_all()
db.create_all()

# Make api call to populate exercises

# Manual entry of some data - no API Call

# Add exercises
two_hand_kettle_swing = Exercise(name='Two handed kettlebell swing', description='Two Handed Russian Style Kettlebell swing')
four_count_burpee = Exercise(name='Four-count burpees', description='Starting position: Stand straight, feet hip-width apart. Steps: Sqat low and support yourself on the floor with your hands between the knees and in front of your feet, your back straight. Keeping your hands on the floor, jump your legs backward into high plank position. Jump your feet forward to return to the squat position. Repeat.')
abdominal_stabilization = Exercise(name='Abdominal Stabilization', description='Do something')
alternate_back_lunges = Exercise(name='Alternate back lunges', description='The posterior muscles of the buttocks, hamstrings, soleus and gastrocnemius are trained more')
alternating_bicep_curl = Exercise(name='Alternating bicep curls', description='Starting position: Start standing up with dumbbells in each hand, your back straight and feet hip-width apart. Your arms should be relaxed, pointing down. Your knees should be slightly bent, your abs contracted, and your shoulders down. Steps: Bend one arm at the elbow, bringing the dumbbell up to your shoulder. Your upper arm should remain motionless during this movement. Bring the dumbbell back down until your arm is in its original relaxed position. Repeat, switching arms.')

# Commit exercises
db.session.add_all([two_hand_kettle_swing, four_count_burpee, abdominal_stabilization, alternate_back_lunges, alternating_bicep_curl])
db.session.commit()

# Add users
bob_bobson = User.signup(email='bob@unoriginallastname.com', username='Bobbo', bio='I am here to do some workouts! I hope you are too!!!', password='bobson')
mike_mikeson = User.signup(email='mike@gmail.com', username='Mikey', bio='I am here to do some workouts! I hope you are too!!!', password='mikeson')
bob_alfredson = User.signup(email='bob@gmail.com', username='BobbyA', bio='I am here to do some workouts! I hope you are too!!!', password='alfredson')
jim_mikeson = User.signup(email='jim@gmail.com', username='JimmyMike', bio='I am here to do some workouts! I hope you are too!!!', password='mikeson')
bob_bo = User.signup(email='otherbob@otherbob.com', username='Bobbo2electricboo', bio='I am here to do some workouts! I hope you are too!!!', password='bobson')

db.session.commit()

# Add workouts
the_bobson_workout = Workout.create(description='Curls and Burpees Forever', owner_user_id='1')
the_mikeson_workout = Workout.create(description='Kettles and Abs All Day', owner_user_id='2')
the_bo_workout = Workout.create(description='I do very little', owner_user_id='5')

db.session.commit()

# Add goals
add_to_bobson_workout_1 = Goal(workout_id=1, exercise_id=5, goal_reps=10, goal_sets=3, goal_weight_lbs=45)
add_to_bobson_workout_2 = Goal(workout_id=1, exercise_id=2, goal_reps=50, goal_sets=1)

add_to_mikeson_workout_1 = Goal(workout_id=2, exercise_id=1, goal_reps=30, goal_weight_lbs=80)
add_to_mikeson_workout_2 = Goal(workout_id=2, exercise_id=3, goal_sets=6, goal_time_sec=60)

db.session.add_all([
    add_to_bobson_workout_1,
    add_to_bobson_workout_2,
    add_to_mikeson_workout_1,
    add_to_mikeson_workout_2,
    ])
db.session.commit()

# Add performance
the_bobson_workout_1_performance_4 = Performance(goal_id =1, performance_reps=10, performance_sets=3, performance_weight_lbs=45)
the_bobson_workout_1_performance_1 = Performance(goal_id =1, performance_reps=10, performance_sets=3, performance_weight_lbs=30)
the_bobson_workout_1_performance_2 = Performance(goal_id =1, performance_reps=10, performance_sets=3, performance_weight_lbs=35)
the_bobson_workout_1_performance_3 = Performance(goal_id =1, performance_reps=10, performance_sets=3, performance_weight_lbs=40)

the_bobson_workout_2_performance_1 = Performance(goal_id =2, performance_reps=36)
the_bobson_workout_2_performance_2 = Performance(goal_id =2, performance_reps=39)
the_bobson_workout_2_performance_3 = Performance(goal_id =2, performance_reps=50)

db.session.add_all([
    the_bobson_workout_1_performance_1,
    the_bobson_workout_1_performance_2,
    the_bobson_workout_1_performance_3,
    the_bobson_workout_1_performance_4,
    the_bobson_workout_2_performance_1,
    the_bobson_workout_2_performance_2,
    the_bobson_workout_2_performance_3
])

db.session.commit()
