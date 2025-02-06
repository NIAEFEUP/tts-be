from university.models import DirectExchange, DirectExchangeParticipants

class DirectExchangeController:
    def get_exchange_participant_map(self, exchange: DirectExchange):
        result = dict()

        participant_entries = DirectExchangeParticipants.objects.filter(direct_exchange=exchange)
        for participant_entry in participant_entries:
            if result.get(participant_entry.participant_nmec):
                result[participant_entry.participant_nmec]["goes_to"].append(participant_entry.class_participant_goes_to)
                result[participant_entry.participant_nmec]["goes_from"].append(participant_entry.class_participant_goes_from)
            else:
                result[participant_entry.participant_nmec]["goes_to"] = [participant_entry.class_participant_goes_to]
                result[participant_entry.participant_nmec]["goes_from"] = [participant_entry.class_participant_goes_from]

        return result