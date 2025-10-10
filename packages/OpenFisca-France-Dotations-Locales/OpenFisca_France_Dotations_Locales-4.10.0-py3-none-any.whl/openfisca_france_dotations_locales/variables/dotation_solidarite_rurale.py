from numpy import round

from openfisca_core.model_api import Variable, YEAR
from openfisca_france_dotations_locales.entities import Commune, Etat


class dsr_montant_outre_mer(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Montant de la quote-part de dotation de solidarité rurale (DSR) allouée aux communes ultra-marines"

    def formula(etat, period, parameters):
        # info : Tant que les calculs sont réalisés en float32, dgf_montant_perequation_verticale_communale
        # doit être calculé dans cette formule pour éviter des erreurs de précisions
        # à l'association de ce nombre en Md€ à des nombres à décimales.
        enveloppe_dnp = parameters(period).dotation_nationale_perequation.montant.total
        enveloppe_dsr = parameters(period).dotation_solidarite_rurale.montant.total
        enveloppe_dsu = parameters(period).dotation_solidarite_urbaine.montant.total
        dgf_montant_perequation_verticale_communale = enveloppe_dnp + enveloppe_dsr + enveloppe_dsu

        # info : calcul dsr_montant_outre_mer déduit des montants effectifs 2024 et 2025
        # logique = la DSR outre-mer est à l'échelle de la part de contribution
        # de la DSR nationale à l'assiette de la DACOM (enveloppe de péréquation verticale)
        portion_dsr_enveloppe_perequation = enveloppe_dsr / dgf_montant_perequation_verticale_communale
        dacom_montant_total = etat('dacom_montant_total', period)
        dsr_montant_outre_mer = round(portion_dsr_enveloppe_perequation * dacom_montant_total)
        return dsr_montant_outre_mer


class dsr_montant_metropole(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Montant de l'enveloppe métropole de la dotation de solidarité rurale (DSR)"

    def formula(etat, period, parameters):
        '''
        Déduit le montant d'enveloppe DSR des communes de métropole suite
        au calcul de sa quote-part outre-mer.
        Equivaut au calcul du paramètre dotation_solidarite_rurale.montant.metropole
        en cas d'évolution de l'enveloppe totale DSR.
        '''
        dsr_montant_total = parameters(period).dotation_solidarite_rurale.montant.total
        dsr_montant_outre_mer = etat('dsr_montant_outre_mer', period)

        dsr_montant_metropole = dsr_montant_total - dsr_montant_outre_mer
        return dsr_montant_metropole


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

    def formula(commune, period):
        dsr_fraction_cible = commune("dsr_fraction_cible", period)
        dsr_fraction_bourg_centre = commune("dsr_fraction_bourg_centre", period)
        dsr_fraction_perequation = commune("dsr_fraction_perequation", period)
        return dsr_fraction_cible + dsr_fraction_bourg_centre + dsr_fraction_perequation
