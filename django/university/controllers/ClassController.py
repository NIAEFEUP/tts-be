from university.models import Class, Professor, Slot, SlotProfessor, SlotClass, CourseUnit
from django.db import transaction
from university.controllers.SigarraController import SigarraController
from university.controllers.ScheduleController import ScheduleController
from django.forms.models import model_to_dict
from django.core.cache import cache

import hashlib

from django.utils import timezone

from django.db.models import Prefetch

class ClassController:
    @staticmethod
    def delete_cached_classes(course_unit_id: int):
        for class_obj in Class.objects.filter(course_unit=course_unit_id):
            for slot_class_obj in SlotClass.objects.filter(class_field__id=class_obj.id):
                for slot_obj in slot_class_obj.slot.all():
                    for slot_professor_obj in SlotProfessor.objects.filter(slot=slot_obj):
                        slot_professor_obj.slot.professor.delete()
                        slot_professor_obj.delete()

                    slot_obj.delete()

                slot_class_obj.delete()

            class_obj.delete()

    @staticmethod
    def parse_classes_from_response(response_data: list):
        fetched_classes = set()

        for entry in response_data:
            course_unit_id = int(entry.get('ocorrencia_id'))
            start_time = float(entry.get('hora_inicio', 0)) / 3600.0
            duration = float(entry.get('aula_duracao', 0))
            location = entry.get('sala_sigla')
            lesson_type = entry.get('tipo')
            day = ScheduleController.from_sigarra_day(entry.get('dia'))

            hash = hashlib.sha256(f"{course_unit_id}{day}{start_time}{duration}{location}{lesson_type}".encode('utf-8')).hexdigest()

            if hash in fetched_classes:
                continue

            fetched_classes.add(hash)

            slot = Slot(
                id=entry.get('aula_id'),
                lesson_type=entry.get('tipo'),
                day=ScheduleController.from_sigarra_day(entry.get('dia')),
                start_time=float(entry.get('hora_inicio', 0)) / 3600.0,
                duration=float(entry.get('aula_duracao', 0)),
                location=entry.get('sala_sigla'),
                is_composed=len(entry.get('turmas', [])) > 1,
                last_updated=timezone.now()
            )
            slot.save()

            for turma in entry.get('turmas', []):
                new_class, created = Class.objects.get_or_create(
                    name=turma.get('turma_sigla'),
                    course_unit_id=course_unit_id,

                    defaults={
                        'vacancies': 0,
                        'last_updated': timezone.now()
                    }
                )

                slot_class, created = SlotClass.objects.get_or_create(
                    slot=slot,
                    class_field=new_class,
                )

            for docente in entry.get('docentes', []):
                professor, created = Professor.objects.get_or_create(
                    id=docente.get('doc_codigo'),
                    defaults={
                        'professor_acronym': entry.get('doc_sigla'),
                        'professor_name': docente.get('doc_nome')
                    }
                )

                slot_professor = SlotProfessor(
                    slot=slot,
                    professor=professor
                ) 
                slot_professor.save()

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
    def get_classes(course_unit_id: int, fetch_professors: bool = True):
        sigarra_controller = SigarraController(login = False)
        (semana_ini, semana_fim) = sigarra_controller.semester_weeks()

        if not cache.get(f"schedule-{course_unit_id}"):
            with transaction.atomic():
                ClassController.delete_cached_classes(course_unit_id)
                schedule = SigarraController().get_course_schedule(course_unit_id).data

                ClassController.parse_classes_from_response(schedule)

                cache.set(f"schedule-{course_unit_id}", True, 60 * 60 * 24)
        
        classes = Class.objects.filter(
            course_unit=course_unit_id
        ).select_related(
            'course_unit'
        ).prefetch_related(
            Prefetch('slotclass_set', queryset=SlotClass.objects.select_related('slot'))
        ).order_by("name")

        result = []

        for class_obj in classes:
            slot_list = []

            if fetch_professors:
                slot_list = [ClassController.get_professors(sc.slot) for sc in class_obj.slotclass_set.all()]
            else: 
                slot_list = [
                    {
                        'id': sc.slot.id,
                        'lesson_type': sc.slot.lesson_type,
                        'day': sc.slot.day,
                        'start_time': float(sc.slot.start_time),
                        'duration': float(sc.slot.duration),
                        'location': sc.slot.location,
                        'is_composed': sc.slot.is_composed,
                        'professors': []
                    } for sc in class_obj.slotclass_set.all()
                ]

            result.append({
                "id": class_obj.id,
                "name": class_obj.name,
                "vacancies": class_obj.vacancies,
                "slots": slot_list
            })

        return result

