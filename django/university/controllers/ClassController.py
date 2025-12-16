from university.models import Class, Professor, Slot, SlotProfessor, SlotClass, CourseUnit
from university.controllers.SigarraController import SigarraController
from university.controllers.ScheduleController import ScheduleController
from django.forms.models import model_to_dict
from django.core.cache import cache

from django.utils import timezone

from django.db.models import Prefetch

class ClassController:
    @staticmethod
    def parse_classes_from_response(response_data: list):
        for entry in response_data:
            course_unit_id = int(entry.get('ocorrencia_id'))

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

                slot_class = SlotClass(
                    slot=slot,
                    class_field=new_class
                )
                slot_class.save()

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
            print("Not in cache")
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

        print("CLASS: ", classes)

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

