from apps.naming.services import PersonNameService, LocationNameService
from apps.person.models import Person


class PersonService(object):

    @staticmethod
    def create_random_person(birth_year, gender):
        person = Person.objects.create(
            name=PersonNameService.get_name(gender),
            nobility=True,
            from_location=LocationNameService.create_name(),
            gender=gender,
            birth_year=birth_year
        )

        return person
