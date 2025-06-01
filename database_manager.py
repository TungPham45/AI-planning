import pandas as pd
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self):
        try:
            self.subjects_df = pd.read_excel('subject.xlsx')
            self.grades_df = pd.read_excel('grade.xlsx')
            self.topics_df = pd.read_excel('topic.xlsx')
            self.theories_df = pd.read_excel('theory.xlsx')
            self.practices_df = pd.read_excel('practice.xlsx')
        except Exception as e:
            print(f"[ERROR] Lỗi khi đọc file Excel: {str(e)}")
            raise

    def get_subjects(self) -> List[Dict]:
        """Get all subjects"""
        return self.subjects_df.to_dict('records')

    def get_grades(self) -> List[Dict]:
        """Get all grades"""
        return self.grades_df.to_dict('records')

    def get_topics_by_subject_grade(self, subject_id: int, grade_id: int) -> List[Dict]:
        """Get topics for a specific subject and grade"""
        return self.topics_df[
            (self.topics_df['ID_subject'] == subject_id) & 
            (self.topics_df['ID_grade'] == grade_id)
        ].to_dict('records')

    def get_theories_by_topic(self, topic_id: int) -> List[Dict]:
        """Get theories for a specific topic"""
        return self.theories_df[
            self.theories_df['ID_topic'] == topic_id
        ].to_dict('records')

    def get_practices_by_theory(self, theory_id: int) -> List[Dict]:
        """Get practices for a specific theory"""
        return self.practices_df[
            self.practices_df['ID_theory'] == theory_id
        ].to_dict('records')

    def get_subject_by_id(self, subject_id: int) -> Optional[Dict]:
        """Get subject by ID"""
        result = self.subjects_df[self.subjects_df['ID_subject'] == subject_id]
        return result.to_dict('records')[0] if not result.empty else None

    def get_grade_by_id(self, grade_id: int) -> Optional[Dict]:
        """Get grade by ID"""
        result = self.grades_df[self.grades_df['ID_grade'] == grade_id]
        return result.to_dict('records')[0] if not result.empty else None

    def get_topic_by_id(self, topic_id: int) -> Optional[Dict]:
        """Get topic by ID"""
        result = self.topics_df[self.topics_df['ID_topic'] == topic_id]
        return result.to_dict('records')[0] if not result.empty else None

    def get_theory_by_id(self, theory_id: int) -> Optional[Dict]:
        """Get theory by ID"""
        result = self.theories_df[self.theories_df['ID_theory'] == theory_id]
        return result.to_dict('records')[0] if not result.empty else None

    def get_practice_by_id(self, practice_id: int) -> Optional[Dict]:
        """Get practice by ID"""
        result = self.practices_df[self.practices_df['ID_practice'] == practice_id]
        return result.to_dict('records')[0] if not result.empty else None

    def get_learning_path(self, subject_id: int, grade_id: int) -> Dict:
        """Get complete learning path for a subject and grade"""
        subject = self.get_subject_by_id(subject_id)
        grade = self.get_grade_by_id(grade_id)
        
        if not subject or not grade:
            return None

        topics = self.get_topics_by_subject_grade(subject_id, grade_id)
        
        learning_path = {
            'subject': subject,
            'grade': grade,
            'topics': []
        }

        for topic in topics:
            topic_data = {
                'topic': topic,
                'theories': []
            }
            
            theories = self.get_theories_by_topic(topic['ID_topic'])
            for theory in theories:
                theory_data = {
                    'theory': theory,
                    'practices': self.get_practices_by_theory(theory['ID_theory'])
                }
                topic_data['theories'].append(theory_data)
            
            learning_path['topics'].append(topic_data)

        return learning_path 