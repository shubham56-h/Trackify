from models import db, UserSplitAssignment, WorkoutSession
from datetime import date


class WorkoutManager:
    @staticmethod
    def get_current_day(user_id):
        """Get the current day for a user's split"""
        assignment = UserSplitAssignment.query.filter_by(user_id=user_id).first()
        if not assignment:
            return None
        
        split = assignment.split
        if not split.days:
            return None
        
        for day in split.days:
            if day.position == assignment.current_position:
                return day
        
        return split.days[0]
    
    @staticmethod
    def move_to_next_day(user_id):
        """Move user to the next day in their split"""
        assignment = UserSplitAssignment.query.filter_by(user_id=user_id).first()
        if not assignment:
            return None
        
        split = assignment.split
        total_days = len(split.days)
        
        assignment.current_position = (assignment.current_position + 1) % total_days
        assignment.last_completed_at = date.today()
        db.session.commit()
        
        return WorkoutManager.get_current_day(user_id)
    
    @staticmethod
    def get_active_session(user_id):
        """Get active workout session for user"""
        return WorkoutSession.query.filter_by(
            user_id=user_id,
            completed=False
        ).first()
