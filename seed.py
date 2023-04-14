"""Seed database with sample data and data from API."""

# from csv import DictReader
from app import db
from models import Exercise, Metric, ExerciseMetric, User, Workout, WorkoutExercise, Goal, Performance


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
bob_bobson = User(email='bob@unoriginallastname.com', username='Bobbo', bio='I am here to do some workouts! I hope you are too!!!', password='bobson')
mike_mikeson = User(email='mike@gmail.com', username='Mikey', bio='I am here to do some workouts! I hope you are too!!!', password='mikeson')
bob_alfredson = User(email='bob@gmail.com', username='BobbyA', bio='I am here to do some workouts! I hope you are too!!!', password='alfredson')
jim_mikeson = User(email='jim@gmail.com', username='JimmyMike', bio='I am here to do some workouts! I hope you are too!!!', password='mikeson')
bob_bo = User(email='otherbob@otherbob.com', username='Bobbo2electricboo', bio='I am here to do some workouts! I hope you are too!!!', password='bobson')

db.session.add_all([bob_bobson, mike_mikeson, bob_alfredson, jim_mikeson, bob_bo])
db.session.commit()

# Add workouts
the_bobson_workout = Workout(description='Curls and Burpees Forever', owner_user_id='1')
the_mikeson_workout = Workout(description='Kettles and Abs All Day', owner_user_id='2')
the_bo_workout = Workout(description='I do very little', owner_user_id='5')
db.session.add_all([the_bobson_workout, the_mikeson_workout, the_bo_workout])
db.session.commit()

# Add exercises to the workouts
add_to_bobson_1 = WorkoutExercise(workout_id=1, exercise_id=2)
add_to_bobson_2 = WorkoutExercise(workout_id=1, exercise_id=5)
add_to_mikeson_1 = WorkoutExercise(workout_id=2, exercise_id=1)
add_to_mikeson_2 = WorkoutExercise(workout_id=2, exercise_id=3)

db.session.add_all([add_to_bobson_1, add_to_bobson_2, add_to_mikeson_1, add_to_mikeson_2])
db.session.commit()

# Add goals
# Add performance