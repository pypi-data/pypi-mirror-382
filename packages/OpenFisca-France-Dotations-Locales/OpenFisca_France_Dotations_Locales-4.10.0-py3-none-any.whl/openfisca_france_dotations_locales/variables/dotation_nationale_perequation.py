from numpy import round

from openfisca_core.model_api import Variable, YEAR
from openfisca_france_dotations_locales.entities import Commune, Etat


class dnp_montant_outre_mer(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Montant de la quote-part de dotation nationale de péréquation (DNP) allouée aux communes ultra-marines"

    def formula(etat, period, parameters):
        dacom_montant_total = etat('dacom_montant_total', period)

        # info : Tant que les calculs sont réalisés en float32, dgf_montant_perequation_verticale_communale
        # doit être calculé dans cette formule pour éviter des erreurs de précisions
        # à l'association de ce nombre en Md€ à des nombres à décimales.
        enveloppe_dnp = parameters(period).dotation_nationale_perequation.montant.total
        enveloppe_dsr = parameters(period).dotation_solidarite_rurale.montant.total
        enveloppe_dsu = parameters(period).dotation_solidarite_urbaine.montant.total
        dgf_montant_perequation_verticale_communale = enveloppe_dnp + enveloppe_dsr + enveloppe_dsu

        # info : calcul dnp_montant_outre_mer déduit des montants effectifs 2024 et 2025
        # logique = la DNP outre-mer est à l'échelle de la part de contribution
        # de la DNP nationale à l'assiette de la DACOM (enveloppe de péréquation verticale)
        portion_dnp_enveloppe_perequation = enveloppe_dnp / dgf_montant_perequation_verticale_communale
        dnp_montant_outre_mer = round(portion_dnp_enveloppe_perequation * dacom_montant_total)
        return dnp_montant_outre_mer


class dnp_montant_metropole(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Montant de l'enveloppe métropole de la dotation nationale de péréquation (DNP)"

    def formula(etat, period, parameters):
        '''
        Déduit le montant d'enveloppe DNP des communes de métropole suite
        au calcul de sa quote-part outre-mer.
        Equivaut au calcul du paramètre dotation_nationale_perequation.montant.metropole
        en cas d'évolution de l'enveloppe totale DNP.
        '''
        dnp_montant_total = parameters(period).dotation_nationale_perequation.montant.total
        dnp_montant_outre_mer = etat('dnp_montant_outre_mer', period)
        return dnp_montant_total - dnp_montant_outre_mer


class dotation_nationale_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Dotation nationale de péréquation (DNP)"
    # Article L2334-14-1 du Code général des collectivités locales
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048849540/2023-12-31/"
