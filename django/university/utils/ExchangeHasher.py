import hashlib
from typing import Any, Iterable

class ExchangeHasher:
    @staticmethod
    def hash(exchanges: Iterable[Any], username: str) -> str:
        serialized_request = '|'.join(map(
            lambda exchange: ExchangeHasher.serialize_exchange(exchange, username),
            sorted(exchanges)  # sorted to ensure order between requests
        ))

        return hashlib.sha256(serialized_request.encode('utf8')).hexdigest()

    @staticmethod
    def serialize_exchange(exchange: Any, username: str) -> str:
        # This function depends on the schema of the `CreateRequestData` type in the frontend
        return (
            username
            + '+' + str(exchange['courseUnitId'])
            + '+' + exchange['courseUnitName']
            + '+' + exchange['classNameRequesterGoesFrom']
            + '+' + exchange['classNameRequesterGoesTo']
            + '+' + (str(exchange['other_student']['mecNumber']) if exchange['other_student'] else '')
        )