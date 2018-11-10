from apps.naming.models import PersonNamePrefix, PersonNamePostfix


class PersonNameService(object):

    @staticmethod
    def create_name():
        prefix = PersonNamePrefix.objects.order_by('?').first()
        postfix = PersonNamePostfix.objects.order_by('?').first()
        return f'{prefix}{postfix}'
