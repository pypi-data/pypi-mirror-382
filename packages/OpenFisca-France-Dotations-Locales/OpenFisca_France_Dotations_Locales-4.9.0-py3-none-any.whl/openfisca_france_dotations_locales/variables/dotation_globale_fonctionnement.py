from openfisca_core.model_api import Variable, YEAR
from openfisca_france_dotations_locales.entities import Commune


class dotation_globale_fonctionnement_communes(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total de la dotation globale de fonctionnement des communes (DGF des communes)"
    # Article L2334-1 du Code général des collectivités locales
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048850193/2023-12-31/"

    def formula(commune, period):
        # On ne s'intéresse ici qu'aux portions communales. Néanmoins, pour la vue d'ensemble :
        # DGF des communes et EPCI
        # = dotation forfaitaire
        # + dotation forfaitaire des groupements touristiques (TODO variable)
        # + dotation d'aménagement
        dotation_forfaitaire = commune("dotation_forfaitaire", period)

        # dotation d'aménagement
        # = dotations de péréquation des communes
        # + DGF des EPCI (TODO variable)

        # dotations de péréquation des communes
        # = DSU
        # + DSR
        # + DNP (TODO formule)
        dotation_solidarite_rurale = commune("dotation_solidarite_rurale", period)
        dsu_montant = commune("dsu_montant", period)
        dotation_nationale_perequation = commune("dotation_nationale_perequation", period)
        dotations_perequation_communes = dotation_solidarite_rurale + dsu_montant + dotation_nationale_perequation

        return dotation_forfaitaire + dotations_perequation_communes


class taux_proratisation_population_commune_nouvelle(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Taux de proratisation par population applicable à une commune nouvelle"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=262"
    documentation = '''
    Si la commune nouvelle est défusionnée, la DGF de référence de la commune nouvelle
    est proratisée en fonction de sa population telle qu'indiquée dans l‘arrêté préfectoral
    établissant la modification des limites territoriales de la commune.

    Taux de proratisation applicable à la CN :
    = population de la nouvelle commune conservant le statut de commune nouvelle
    / population de la commune nouvelle avant la modification de ses limites territoriales
    '''


class taux_evolution_dgf(Variable):
    value_type = float
    entity = Commune  # et groupements de communes ?!
    definition_period = YEAR
    label = "Taux d'évolution de la DGF"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=262"
    documentation = '''
    La DGF de référence finale de la commune nouvelle est calculée en multipliant
    chaque année la DGF de référence spontanée par le taux d’évolution de la DGF des communes
    et des groupements mentionnée au premier alinéa de l'article L. 2334-1 du CGCT.

    Taux d'évolution N =
    DGF des communes et des groupements N
    / DGF des communes et des groupements N — 1

    Où DGF des communes et des groupements = somme des montants attribués au titre
    de la DGF des communes et des groupements mentionnée au premier alinéa
    de l'article L. 2334-1 CGCT.
    '''


class dgf_reference_communes_spontanee(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant spontané de la dotation globale de fonctionnement de référence des communes (DGF de référence des communes)"
    # Article L2113-22-1, III du Code général des collectivités territoriales
    # dans le calcul de la part garantie de la dotation en faveur des communes nouvelles
    reference = [
        "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048850000/2023-12-31/",
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=262"
        ]
    documentation = '''
    Au regard de la part garantie de la dotation en faveur des communes nouvelles débutant en 2024,
    la DGF de référence varie en fonction de la date de création de la commune nouvelle.

    Pour les communes nouvelles créées avant le 2 janvier 2023, c'est le montant de la DGF
    perçu par la commune nouvelle lors de sa dernière année d‘éligibilité au pacte de stabilité :
    * DGF 2020 pour les communes nouvelles créées entre le 2 janvier 2017 et le 1er janvier 2018.
    * DGF 2021 pour les communes nouvelles créées entre le 2 janvier 2018 et le 1er janvier 2019.
    * DGF 2023 pour les autres communes.

    Pour les communes nouvelles créées à compter du 2 janvier 2023,
    c'est la somme des DGF perçues par les communes l’année précédant la fusion.

    Si la commune nouvelle est une commune nouvelle rurale au sens de l’article L. 2334-22-2 du CGCT,
    alors il sera soustrait à sa DGF de référence les éventuelles sommes perçues en 2023
    au titre d'une garantie de sortie de la dotation de solidarité rurale.

    Si la commune nouvelle est défusionnée, la DGF de référence de la commune nouvelle
    est proratisée en fonction de sa population telle qu'indiquée dans l‘arrêté préfectoral
    établissant la modification des limites territoriales de la commune.
    '''
    # formula ? :
    # https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/issues/16


class dotation_globale_fonctionnement_reference_communes(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant final de la dotation globale de fonctionnement de référence des communes (DGF de référence des communes)"
    # Article L2113-22-1, III du Code général des collectivités territoriales
    # dans le calcul de la part garantie de la dotation en faveur des communes nouvelles
    reference = [
        "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048850000/2023-12-31/",
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=262"
        ]
    documentation = '''
    La DGF de référence finale de la commune nouvelle est calculée en multipliant
    chaque année la DGF de référence spontanée par le taux d’évolution de la DGF
    des communes et des groupements mentionnée au premier alinéa de l'article L. 2334-1 du CGCT.
    '''
    # formula ? :
    # https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/issues/17
