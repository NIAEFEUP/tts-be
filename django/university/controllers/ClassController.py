from university.models import Class, Professor, Slot, SlotProfessor, SlotClass
from django.forms.models import model_to_dict

from django.db.models import Prefetch

class ClassController:
    @staticmethod
    def get_professors(slot):
        slot_professors = SlotProfessor.objects.filter(slot_id=slot.id).select_related("professor")

        professors = [
            {
                'id': slot_professor.professor.id,
                'acronym': slot_professor.professor.professor_acronym,
                'name': slot_professor.professor.professor_name
            } for slot_professor in slot_professors
        ]

        return {
            'id': slot.id,
            'lesson_type': slot.lesson_type,
            'day': slot.day,
            'start_time': float(slot.start_time),
            'duration': float(slot.duration),
            'location': slot.location,
            'is_composed': slot.is_composed,
            'professors': professors
        }

    @staticmethod
    def get_classes(course_unit_id: int):
        classes = Class.objects.filter(
            course_unit=course_unit_id
        ).select_related(
            'course_unit'
        ).prefetch_related(
            Prefetch('slotclass_set', queryset=SlotClass.objects.select_related('slot'))
        ).order_by("name")

        result = []

        for class_obj in classes:
            slot_list = [ClassController.get_professors(sc.slot) for sc in class_obj.slotclass_set.all()]

            result.append({
                "id": class_obj.id,
                "name": class_obj.name,
                "vacancies": class_obj.vacancies,
                "slots": slot_list
            })

        return result
