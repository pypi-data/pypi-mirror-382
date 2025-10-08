from openfisca_core.model_api import Variable, YEAR
from openfisca_france_dotations_locales.entities import Commune


class dotation_nationale_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Dotation nationale de péréquation (DNP)"
    # Article L2334-14-1 du Code général des collectivités locales
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048849540/2023-12-31/"
