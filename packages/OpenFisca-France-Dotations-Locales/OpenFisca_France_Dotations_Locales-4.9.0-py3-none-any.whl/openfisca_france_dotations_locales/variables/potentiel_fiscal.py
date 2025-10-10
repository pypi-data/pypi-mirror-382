from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class potentiel_fiscal(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Potentiel fiscal de la commune (4 taxes)"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000025076225"


class potentiel_fiscal_moyen_national(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Potentiel fiscal moyen national par habitant (PF/HAB)"
    reference = [
        "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037994287",
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=115",  # 2020
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=142",  # 2021
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=188",  # 2022
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=260",  # 2024
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=295"  # 2025
        ]
    documentation = '''
    Potentiel fiscal moyen constaté au niveau national rapporté à la population DGF totale logarithmée.
    Il contribue au calcul de la Dotation forfaitaire.
    '''

    def formula_2018(etat, period):
        return 624.197

    def formula_2019(etat, period):
        return 631.5677

    def formula_2020(etat, period):
        return 641.164387  # PF/HAB 2019 dans note DGCL DF 2020, page 14

    def formula_2021(etat, period):
        return 655.021595  # PF/HAB 2020 dans note DGCL DF 2021, page 14

    def formula_2022(etat, period):
        return 662.030926  # PF/HAB 2021 dans note DGCL DF 2022, page 16

    # TODO en 2023, l'écrêtement péréqué de la DF est suspendu
    # le PF/HAB habituellement publié dans la section dédiée
    # à cet écrêtement dans la note DGCL n'est pas indiqué.
    # Cf. http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=220
    # Identifier le montant 2023 ou le calculer.

    def formula_2024(etat, period):
        return 690.836979  # PF/HAB 2023 dans note DGCL DF 2024, page 13

    def formula_2025(etat, period):
        # TODO transformer en formule de calcul tout en conservant les valeurs officielles en paramètre ?
        return 744.504275  # PF/HAB 2024 dans note DGCL DF 2025, page 10
