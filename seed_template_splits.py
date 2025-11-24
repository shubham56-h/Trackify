"""
Seed popular workout split templates
Run this once to add template splits to the database
"""
from app import create_app
from models import db, Split, SplitDay

app = create_app()

TEMPLATE_SPLITS = [
    {
        'name': 'Push Pull Legs (PPL)',
        'days': [
            {'name': 'Push Day', 'muscle_groups': 'Chest, Shoulders, Triceps'},
            {'name': 'Pull Day', 'muscle_groups': 'Back, Biceps'},
            {'name': 'Leg Day', 'muscle_groups': 'Legs, Core'},
        ]
    },
    {
        'name': 'Upper Lower Split',
        'days': [
            {'name': 'Upper Body', 'muscle_groups': 'Chest, Back, Shoulders, Arms'},
            {'name': 'Lower Body', 'muscle_groups': 'Legs, Core'},
        ]
    },
    {
        'name': 'Bro Split (5 Day)',
        'days': [
            {'name': 'Chest Day', 'muscle_groups': 'Chest'},
            {'name': 'Back Day', 'muscle_groups': 'Back'},
            {'name': 'Shoulder Day', 'muscle_groups': 'Shoulders'},
            {'name': 'Arm Day', 'muscle_groups': 'Biceps, Triceps, Forearms'},
            {'name': 'Leg Day', 'muscle_groups': 'Legs, Core'},
        ]
    },
    {
        'name': 'Full Body (3 Day)',
        'days': [
            {'name': 'Full Body A', 'muscle_groups': 'Chest, Back, Legs'},
            {'name': 'Full Body B', 'muscle_groups': 'Shoulders, Arms, Core'},
            {'name': 'Full Body C', 'muscle_groups': 'Chest, Back, Legs'},
        ]
    },
    {
        'name': 'Arnold Split',
        'days': [
            {'name': 'Chest & Back', 'muscle_groups': 'Chest, Back'},
            {'name': 'Shoulders & Arms', 'muscle_groups': 'Shoulders, Biceps, Triceps'},
            {'name': 'Legs', 'muscle_groups': 'Legs, Core'},
        ]
    },
    {
        'name': 'Enhanced Bro Split (6 Day)',
        'days': [
            {'name': 'Leg Day', 'muscle_groups': 'Quads, Hamstrings, Glutes, Calves'},
            {'name': 'Shoulder Day', 'muscle_groups': 'Shoulders'},
            {'name': 'Back Day', 'muscle_groups': 'Lats, Rhomboids, Lower Back, Traps'},
            {'name': 'Chest Day', 'muscle_groups': 'Upper Chest, Lower Chest, Middle Chest'},
            {'name': 'Arm Day', 'muscle_groups': 'Biceps, Triceps, Forearms'},
            {'name': 'Calisthenics Day', 'muscle_groups': 'Bodyweight, Core, Mobility'},
        ]
    },
]

def seed_templates():
    with app.app_context():
        print("🌱 Seeding template splits...")
        
        created_count = 0
        skipped_count = 0
        
        for template_data in TEMPLATE_SPLITS:
            # Check if this template already exists
            existing = Split.query.filter_by(
                name=template_data['name'],
                is_template=True
            ).first()
            
            if existing:
                print(f"⏭️  Skipped (already exists): {template_data['name']}")
                skipped_count += 1
                continue
            
            # Create split
            split = Split(
                owner_id=None,  # No owner for templates
                name=template_data['name'],
                is_template=True
            )
            db.session.add(split)
            db.session.flush()
            
            # Add days
            for idx, day_data in enumerate(template_data['days']):
                day = SplitDay(
                    split_id=split.id,
                    position=idx,
                    name=day_data['name'],
                    muscle_groups=day_data['muscle_groups']
                )
                db.session.add(day)
            
            print(f"✅ Created template: {template_data['name']}")
            created_count += 1
        
        db.session.commit()
        print(f"\n🎉 Done! Created: {created_count}, Skipped: {skipped_count}")

if __name__ == '__main__':
    seed_templates()
