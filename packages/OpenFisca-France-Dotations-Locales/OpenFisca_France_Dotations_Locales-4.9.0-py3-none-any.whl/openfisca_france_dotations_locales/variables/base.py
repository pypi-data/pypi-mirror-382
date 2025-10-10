from numpy import divide, errstate, where

from openfisca_core.model_api import ETERNITY, MONTH, YEAR, date, set_input_dispatch_by_period, Variable
from openfisca_france_dotations_locales.entities import Commune


# L'année où le temps commence :) Par exemple, utile aux conversions datetime / int.
ANNEE_DATETIME_EPOCH = 1970  # = time.gmtime(0).tm_year


class nom(Variable):
    value_type = str
    entity = Commune
    definition_period = MONTH
    label = "Nom de la commune"
    reference = "https://www.insee.fr/fr/information/6051727"
    set_input = set_input_dispatch_by_period


class code_insee(Variable):
    value_type = str
    entity = Commune
    definition_period = MONTH
    label = "Code INSEE de la commune"
    reference = "https://www.insee.fr/fr/information/6051727"
    set_input = set_input_dispatch_by_period


class date_creation_commune(Variable):
    value_type = date
    entity = Commune
    definition_period = ETERNITY
    default_value = date(1, 1, 1)
    label = "Date de création de la commune"
    # Référence à partir de 2024 et de l'apparition de la dotation communes nouvelles : Article R.2113-24 CGCT
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049484404/2024-04-29/"


class commune_nouvelle(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Est une commune nouvellement créée"
    # Référence à partir de 2024 et de l'apparition de la dotation communes nouvelles : Article R.2113-24 CGCT
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049484404/2024-04-29/"

    def formula(commune, period):
        date_creation_commune = commune("date_creation_commune", period)

        annee_precedente = period.last_year.start.year
        annee_creation_commune = date_creation_commune.astype('datetime64[Y]').astype(int) + ANNEE_DATETIME_EPOCH

        return annee_creation_commune == annee_precedente


class age_commune(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    default_value = -9999
    label = "Âge en années de la commune"
    documentation = '''
    Âge calculé relativement au premier jour de l'an.
    Le jour et le mois de création de la commune sont ignorés.
    '''

    def formula(commune, period):
        date_creation_commune = commune("date_creation_commune", period)
        annee_creation_commune = date_creation_commune.astype('datetime64[Y]').astype(int) + ANNEE_DATETIME_EPOCH
        return period.start.year - annee_creation_commune


def safe_divide(a, b, value_if_error=0):
    with errstate(divide='ignore', invalid='ignore'):
        return where(b != 0, divide(a, b), value_if_error)
