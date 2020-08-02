from apps.account.models import Savegame
from apps.dynasty.settings import GENDER_MALE, GENDER_FEMALE
from apps.location.models import County
from apps.naming.services import LocationNameService


class CreateCountyService(object):

    @staticmethod
    def create_random_county(savegame: Savegame):
        county = County.objects.create(
            name=LocationNameService.create_name(savegame),
            savegame=savegame
        )

        return county


class CountyRulerService:
    country = None
    savegame = None

    def __init__(self, savegame: Savegame, country: County):
        self.savegame = savegame
        self.country = country

    def get_succession_line(self):
        succession_line = []

        # todo make this dynamic with a recursion to find more people
        try:
            ruler = self.country.ruled_by.current_dynast
        except AttributeError:
            return succession_line
        else:
            if not ruler:
                return succession_line

        # Sons
        sons = ruler.children.get_alive(
            self.savegame).filter(gender=GENDER_MALE).order_by('birth_year')
        for person in sons:
            succession_line.append(person)

        # Brothers
        brothers = ruler.get_siblings_by_gender(
            GENDER_MALE).get_alive(self.savegame).order_by('birth_year')
        for person in brothers:
            succession_line.append(person)

        # Husband of daughters
        married_daughters = ruler.children.get_alive(
            self.savegame).filter(gender=GENDER_FEMALE).exclude(
            spouse__isnull=True).order_by('birth_year')
        for person in married_daughters:
            succession_line.append(person.spouse)

        # Husband of sisters
        married_sisters = ruler.get_siblings_by_gender(
            GENDER_FEMALE).get_alive(self.savegame).exclude(
            spouse__isnull=True).order_by('birth_year')
        for person in married_sisters:
            succession_line.append(person.spouse)

        return succession_line
