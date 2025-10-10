from math import ceil

from openfisca_core.model_api import Variable, YEAR
from openfisca_france_dotations_locales.entities import Etat


class ratio_demographique_outre_mer(Variable):
    value_type = float
    entity = Etat
    definition_period = YEAR
    label = "Ratio démographique majoré de population INSEE communale ultramarine au rapport de l'ensemble des communes"
    reference = [
        "I de l'article L. 2334-23-1 du Code général des collectivités territoriales (CGCT)",
        "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000046873826/2023-01-01"
        ]

    def formula_2023(etat, period, parameters):
        populations_insee = etat.members('population_insee', period)
        outre_mer = etat.members('outre_mer', period)

        population_insee_outre_mer = etat.sum(populations_insee * outre_mer)
        population_insee_nationale = etat.sum(populations_insee)
        ratio_population_outre_mer = population_insee_outre_mer / population_insee_nationale

        taux_majoration_population = parameters(period).dotation_amenagement_communes_outre_mer.taux_majoration_population
        ratio_demographique_outre_mer = (1 + taux_majoration_population) * ratio_population_outre_mer

        return ratio_demographique_outre_mer


class dacom_montant_total(Variable):
    value_type = float
    entity = Etat
    definition_period = YEAR
    label = "Montant total de la quote-part de la dotation d'aménagement des communes d'outre-mer (DACOM)"
    reference = [
        "I de l'article L. 2334-23-1 du Code général des collectivités territoriales (CGCT)",
        "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000046873826/2023-01-01"
        ]
    documentation = '''
    [objet] Extrait de la note DGCL DACOM 2025, page 2 :
    Le mode de calcul de la dotation d'aménagement ultramarine traduit la solidarité nationale
    en faveur des communes d'outre-mer en leur affectant une quote-part plus favorable
    que celle résultant de leur strict poids démographique.

    [calcul] Extrait de l'article L. 2334-23-1 :
    I. - A compter de 2020, la quote-part de la dotation d'aménagement (...)
    destinée aux communes des départements d'outre-mer, de la Nouvelle-Calédonie,
    de la Polynésie française, de la collectivité territoriale de Saint-Pierre-et-Miquelon
    et aux circonscriptions territoriales de Wallis-et-Futuna comprend
    une dotation d'aménagement des communes d'outre-mer
    [et, s'agissant des communes des départements d'outre-mer, une dotation de péréquation].

    Cette quote-part est calculée en appliquant à la somme des montants
    de la dotation nationale de péréquation, de la dotation de solidarité rurale
    et de la dotation de solidarité urbaine et de cohésion sociale le rapport existant,
    d'après le dernier recensement de population, entre la population des communes d'outre-mer
    et la population de l'ensemble des communes. Ce rapport est majoré de 63 % en 2023.
    '''

    def formula(etat, period, parameters):
        # info : On choisit d'employer les paramètres d'enveloppe déductibles de la loi
        # et non les variables simulées plus sensibles aux marges d'erreur.
        enveloppe_dnp = parameters(period).dotation_nationale_perequation.montant.total
        enveloppe_dsr = parameters(period).dotation_solidarite_rurale.montant.total
        enveloppe_dsu = parameters(period).dotation_solidarite_urbaine.montant.total

        # info : Tant que les calculs sont réalisés en float32, dgf_montant_perequation_verticale_communale
        # doit être calculé dans cette formule pour éviter des erreurs de précisions
        # à l'association de ce nombre en Md€ au ratio_demographique_outre_mer à parfois 11 décimales.
        dgf_montant_perequation_verticale_communale = enveloppe_dnp + enveloppe_dsr + enveloppe_dsu

        ratio_demographique_outre_mer = etat('ratio_demographique_outre_mer', period)
        dacom_montant_total = ceil(ratio_demographique_outre_mer * dgf_montant_perequation_verticale_communale)
        # info : 'ceil' employé pour arrondir à l'entier surpérieur dès le premier cent
        # calcul déduit de la note DGCL DACOM 2024 (en 2024 : 388_891_981.12238264 arrondi à 388_891_982)
        return dacom_montant_total
