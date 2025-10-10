from openfisca_core.model_api import Variable, YEAR
from openfisca_france_dotations_locales.entities import Commune


class zone_de_montagne(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Commune de montagne: Commune située en zone de montagne"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"
