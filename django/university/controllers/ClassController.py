from university.models import Class, SlotClass, Slot, SlotProfessor


class ClassController:
    @staticmethod
    def get_professors(slot_obj):
        try:
            professor = slot_obj.slotprofessor.professor
            professors = [
                {'id': professor.id, 'acronym': professor.professor_acronym, 'name': professor.professor_name}]
        except SlotProfessor.DoesNotExist:
            professors = []

        return {
            'id': slot_obj.id,
            'lesson_type': slot_obj.lesson_type,
            'day': slot_obj.day,
            'start_time': float(slot_obj.start_time),
            'duration': float(slot_obj.duration),
            'location': slot_obj.location,
            'is_composed': slot_obj.is_composed,
            'professors': professors
        }

    @staticmethod
    def get_classes(course_unit_id: int):
        classes = Class.objects.filter(course_unit=course_unit_id).select_related(
            'course_unit').prefetch_related('slotclass_set__slot').order_by("name")

        result = []
        for class_obj in classes:
            slot_ids = [sc.slot_id for sc in class_obj.slotclass_set.all()]
            slots = Slot.objects.filter(id__in=slot_ids).prefetch_related(
                'slotprofessor__professor')

            slot_list = list(map(ClassController.get_professors, slots))

            result.append({
                'id': class_obj.id,
                'name': class_obj.name,
                'slots': slot_list
            })

        return result
