from openfisca_core import periods
from openfisca_core.reforms import Reform


class change_enveloppe_dsr(Reform):
    name = "Change le montant d'augmentation de l'enveloppe DSR"

    def __init__(self, tax_benefit_system, dsr_augmentation_montant=250_000_000):
        '''
        La réforme augmente le paramètre DSR dotation_solidarite_rurale.augmentation_montant
        de 100_000_000 € relativement à sa valeur initiale 2025 s'élevant à 150_000_000€.
        '''
        self.dsr_augmentation_montant = dsr_augmentation_montant
        super(change_enveloppe_dsr, self).__init__(tax_benefit_system)

    def modify_dsr_augmentation_montant(self, parameters):
        reform_year = 2025
        reform_period = periods.period(reform_year)

        parameters.dotation_solidarite_rurale.augmentation_montant.update(period = reform_period, value = self.dsr_augmentation_montant)

        # Mise en cohérence l'enveloppe totale de l'année de la réforme :
        # Choix notable : pour répercuter correctement les effets de vases communiquants entre enveloppes,
        # on choisit de faire porter à la réforme la mise en cohérence des autres paramètres
        # et non pas au modèle. Ceci afin de ne pas contraindre les contributions au modèle
        # (dans le cas contraire, les formules ne devraient jamais faire appel aux paramètres d'enveloppes totales
        # afin de répercuter des changements de certaines de leurs composantes par une réforme paramétrique
        # mais cela semble être une règle de contribution trop contraignante à maintenir dans le temps).
        dsr_montant_total_annee_precedente = parameters(reform_year - 1).dotation_solidarite_rurale.montant.total
        dsr_montant_total_annee_reforme = dsr_montant_total_annee_precedente + self.dsr_augmentation_montant
        parameters.dotation_solidarite_rurale.montant.total.update(period = reform_period, value = dsr_montant_total_annee_reforme)

        return parameters

    def apply(self):
        self.modify_parameters(modifier_function = self.modify_dsr_augmentation_montant)
