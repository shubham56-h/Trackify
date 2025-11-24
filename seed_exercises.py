"""Seed default exercises into the database"""
from app import create_app
from models import db, Exercise

app = create_app()

# Default exercises organized by muscle group and specific muscle
DEFAULT_EXERCISES = {
    'chest': {
        'upper_chest': ['Incline Barbell Press', 'Incline Dumbbell Press', 'Cable Fly'],
        'middle_chest': ['Flat Barbell Bench Press', 'Flat Dumbbell Press', 'Pec-Dec Fly', 'Push-ups'],
        'lower_chest': ['Decline Barbell Press', 'Decline Dumbbell Press', 'Dips']
    },
    'back': {
        'lats': ['Pull-ups', 'Lat Pulldown', 'Dumbbell Row', 'One Arm Half-Kneeling Lat'],
        'upper_back': ['Face Pulls', 'Reverse Fly', 'Seated Cable Row'],
        'lower_back': ['Deadlift', 'Romanian Deadlift', 'Back Extensions', 'Good Mornings'],
        'traps': ['Barbell Shrugs', 'Dumbbell Shrugs', 'Farmer Walks', 'Rack Pulls'],
        'rhomboids': ['Bent Over Row', 'T-Bar Row', 'Chest Supported Row', 'Inverted Row']
    },
    'shoulders': {
        'front_delt': ['Overhead Press', 'Front Raise', 'Arnold Press'],
        'side_delt': ['Lateral Raise', 'Dumbbell Lateral Raise', 'Cable Lateral Raise', 'Upright Row'],
        'rear_delt': ['Reverse Fly', 'Face Pulls', 'Bent Over Lateral Raise', 'Rear Delt Row']
    },
    'arms': {
        'biceps': ['Barbell Curl', 'Dumbbell Curl', 'Hammer Curl', 'Preacher Curl', 'Cable Curl', 'Spider Curl'],
        'triceps': ['Close Grip Bench Press', 'Tricep Dips', 'Overhead Extension', 'Tricep Pushdown', 'Skull Crushers'],
        'forearms': ['Wrist Curl', 'Reverse Wrist Curl', 'Farmers Walk']
    },
    'legs': {
        'quads': ['Squat', 'Smith Machine Squat', 'Leg Press', 'Leg Extension', 'Lunges'],
        'hamstrings': ['Romanian Deadlift', 'Leg Curl', 'Good Mornings', 'Nordic Curls'],
        'glutes': ['Hip Thrust', 'Bulgarian Split Squat', 'Glute Bridge', 'Cable Kickbacks'],
        'calves': ['Standing Calf Raise', 'Seated Calf Raise', 'Calf Press']
    },
    'core': {
        'abs': ['Crunches', 'Leg Raise', 'Cable Crunch', 'Ab Wheel', 'Plank'],
        'obliques': ['Russian Twist', 'Side Plank', 'Woodchoppers', 'Bicycle Crunches']
    }
}

def seed_exercises():
    with app.app_context():
        # Check if exercises already exist
        existing_count = Exercise.query.filter_by(is_default=True).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} default exercises. Skipping seed.")
            return

        print("Seeding default exercises...")
        count = 0
        
        for muscle_group, specific_muscles in DEFAULT_EXERCISES.items():
            for specific_muscle, exercises in specific_muscles.items():
                for exercise_name in exercises:
                    exercise = Exercise(
                        name=exercise_name,
                        muscle_group=muscle_group,
                        specific_muscle=specific_muscle,
                        is_default=True,
                        created_by=None
                    )
                    db.session.add(exercise)
                    count += 1
        
        db.session.commit()
        print(f"✅ Successfully seeded {count} default exercises!")

if __name__ == '__main__':
    seed_exercises()
