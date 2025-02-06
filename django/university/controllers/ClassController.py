from university.models import Class, Professor, Slot, SlotProfessor


class ClassController:
    @staticmethod
    def get_professors(slot):
        slot_professors = SlotProfessor.objects.filter(slot_id=slot.id).values()
        
        professors = []
        
        for slot_professor in slot_professors:
            professor = Professor.objects.get(id=slot_professor['professor_id'])
            professors.append({
                'id': professor.id,
                'acronym': professor.professor_acronym,
                'name': professor.professor_name
            })

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
    def get_schedule_from_class(class_):
        slot_ids = [sc.slot_id for sc in class_.slotclass_set.all()]
        slots = Slot.objects.filter(id__in=slot_ids)

        slot_list = list(map(ClassController.get_professors, slots))

        return {
            'id': class_.id,
            'name': class_.name,
            'slots': slot_list
        }

    @staticmethod
    def get_classes(course_unit_id: int):
        classes = Class.objects.filter(course_unit=course_unit_id).select_related(
            'course_unit').prefetch_related('slotclass_set__slot').order_by("name")

        result = []
        for class_obj in classes:
            slot_ids = [sc.slot_id for sc in class_obj.slotclass_set.all()]
            slots = Slot.objects.filter(id__in=slot_ids)

            slot_list = list(map(ClassController.get_professors, slots))

            result.append({
                'id': class_obj.id,
                'name': class_obj.name,
                'slots': slot_list
            })

        return result
