from apps.dynasty import settings as ps


def get_opposite_gender(gender):
    return ps.GENDER_FEMALE if gender == ps.GENDER_MALE else ps.GENDER_MALE
