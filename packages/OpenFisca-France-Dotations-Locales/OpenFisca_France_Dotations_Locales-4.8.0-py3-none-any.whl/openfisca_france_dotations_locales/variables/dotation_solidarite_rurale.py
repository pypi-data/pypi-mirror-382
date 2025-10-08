from openfisca_core.model_api import Variable, YEAR
from openfisca_france_dotations_locales.entities import Commune


class dotation_solidarite_rurale(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Dotation de solidarité rurale (DSR)"
    reference = [
        # Articles L2334-20 à L2334-23 du Code général des collectivités territoriales
        "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006197650/2020-01-01/",
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]

    def formula(commune, period, parameters):
        dsr_fraction_cible = commune("dsr_fraction_cible", period)
        dsr_fraction_bourg_centre = commune("dsr_fraction_bourg_centre", period)
        dsr_fraction_perequation = commune("dsr_fraction_perequation", period)
        return dsr_fraction_cible + dsr_fraction_bourg_centre + dsr_fraction_perequation
