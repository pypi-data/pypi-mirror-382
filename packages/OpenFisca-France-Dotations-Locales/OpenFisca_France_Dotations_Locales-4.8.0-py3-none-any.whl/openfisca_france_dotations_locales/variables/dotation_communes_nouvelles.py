from openfisca_core.model_api import Variable, max_, YEAR
from openfisca_france_dotations_locales.entities import Commune


class dotation_communes_nouvelles(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total de la dotation en faveur des communes nouvelles"
    reference = [
        # Article 134 de la loi n° 2023-1322 du 29 décembre 2023 de finances pour 2024
        "https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000048769531/2023-12-31/",
        # Article L. 2113-22-1 du Code général des collectivités territoriales (CGCT)
        "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048850000/2023-12-31/",
        # Note DGCL 2024
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=262"
        ]

    documentation = '''
    La dotation en faveur des communes nouvelles est instituée par la LF pour 2024.
    Elle vient remplacer le pacte de stabilité pour les communes nouvelles
    dont le montant était financé sur l'enveloppe allouée à la dotation globale de fonctionnement (DGF).
    '''

    def formula_2024(commune, period):
        dotation_communes_nouvelles_part_amorcage = commune('dotation_communes_nouvelles_part_amorcage', period)
        dotation_communes_nouvelles_part_garantie = commune('dotation_communes_nouvelles_part_garantie', period)
        return dotation_communes_nouvelles_part_amorcage + dotation_communes_nouvelles_part_garantie


class dotation_communes_nouvelles_eligible_part_amorcage(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Éligibilité à la part amorçage de la dotation en faveur des communes nouvelles"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048850000/2023-12-31/"

    def formula_2024(commune, period, parameters):
        # condition communes dans les _3_ premières années suivant leurs créations
        age_commune = commune("age_commune", period)
        age_eligible = (
            (age_commune >= parameters(period).dotation_communes_nouvelles.amorcage.seuil_age_commune)
            * (age_commune <= parameters(period).dotation_communes_nouvelles.amorcage.plafond_age_commune)
            )

        # condition population insee initiale <= _150000_ habitants
        # où la population insee initiale est la population insee l'année suivant la création de chaque commune
        population_insee_initiale = commune("population_insee_initiale", period)
        population_insee_eligible = (
            (population_insee_initiale >= 0)  # plus précisément, différente de NB_HABITANT_NEUTRALISE = -9999
            * (population_insee_initiale <= parameters(period).dotation_communes_nouvelles.eligibilite.plafond_nombre_habitants)
            )

        return age_eligible * population_insee_eligible


class dotation_communes_nouvelles_part_amorcage(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total de la part amorçage de la dotation en faveur des communes nouvelles"
    # Article L. 2113-22-1 du Code général des collectivités territoriales (CGCT)
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048850000/2023-12-31/"
    documentation = '''
    La part amorçage est destinée à aides les communes nouvelles à faire face,
    dans les premières années suivant leur création, aux coûts inhérents à la fusion.
    En 2024, si l'éligibilité est évaluée au regard de la population INSEE,
    le montant considère la population DGF telle que définie au 2ème alinéa de l’article L. 2334-2 du CGCT.
    '''

    def formula_2024(commune, period, parameters):
        dotation_communes_nouvelles_eligible_part_amorcage = commune("dotation_communes_nouvelles_eligible_part_amorcage", period)

        population_dgf = commune("population_dgf", period)
        montant_attribution_par_habitant = parameters(period).dotation_communes_nouvelles.amorcage.montant_attribution
        montant_part_amorcage_commune = montant_attribution_par_habitant * population_dgf

        return dotation_communes_nouvelles_eligible_part_amorcage * montant_part_amorcage_commune


class dotation_communes_nouvelles_eligible_part_garantie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Éligibilité à la part garantie de la dotation en faveur des communes nouvelles"
    # Article L. 2113-22-1 du Code général des collectivités territoriales (CGCT)
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048850000/2023-12-31/"

    def formula_2024(commune, period, parameters):
        # condition population insee initiale <= _150000_ habitants
        # où la population insee initiale est la population insee l'année suivant la création de chaque commune
        population_insee_initiale = commune("population_insee_initiale", period)
        population_insee_eligible = (
            (population_insee_initiale >= 0)  # plus précisément, différente de NB_HABITANT_NEUTRALISE = -9999
            * (population_insee_initiale <= parameters(period).dotation_communes_nouvelles.eligibilite.plafond_nombre_habitants)
            )

        return population_insee_eligible


class dotation_communes_nouvelles_part_garantie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total de la part garantie de la dotation en faveur des communes nouvelles"
    # Article L. 2113-22-1 du Code général des collectivités territoriales (CGCT)
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048850000/2023-12-31/"
    documentation = '''
    La part garantie compense de manière pérenne toute perte de DGF
    de la commune nouvelle suite à sa fusion.

    Part de garantie année N = DGF de référence finale année N - DGF année N
    si la différence est positive.
    '''

    def formula_2024(commune, period):
        dotation_communes_nouvelles_eligible_part_garantie = commune("dotation_communes_nouvelles_eligible_part_garantie", period)

        dotation_globale_fonctionnement_reference_communes = commune("dotation_globale_fonctionnement_reference_communes", period)
        dotation_globale_fonctionnement_communes = commune("dotation_globale_fonctionnement_communes", period)
        return (
            dotation_communes_nouvelles_eligible_part_garantie
            * max_(
                0,
                (dotation_globale_fonctionnement_reference_communes - dotation_globale_fonctionnement_communes)
                )
            )
