from numpy import full, where, max as numpy_max, unique

from openfisca_core.model_api import Variable, min_, YEAR
from openfisca_france_dotations_locales.entities import *


class strate_demographique(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Strate ou groupe démographique de la commune d'après son nombre d'habitants"
    reference = [
        'Code général des collectivités territoriales - Article L2334-3',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878299&cidTexte=LEGITEXT000006070633'
        ]

    def formula(commune, period, parameters):
        pop = commune('population_dgf', period)
        bareme_strates_demographiques = parameters(period).population.groupes_demographiques
        return bareme_strates_demographiques.calc(pop)


class population_insee(Variable):
    value_type = int
    entity = Commune
    label = "Population de la commune au sens de l'INSEE"
    definition_period = YEAR
    default_value = -9999
    reference = "https://www.insee.fr/fr/metadonnees/definition/c1751"


class population_insee_initiale(Variable):
    value_type = int
    entity = Commune
    label = "Population au sens de l'INSEE à la création de la commune"
    definition_period = YEAR
    default_value = -9999
    # Article R2113-24 du Code général des collectivités locales
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049484404/2024-04-29/"
    documentation = '''
    En 2024, la population initiale est la population INSEE l'année suivant la création de la commune.
    C'est par exemple la population de référence pour évaluer l'éligibilité à la part amorçage
    de la dotation en faveur des communes nouvelles.
    '''

    def formula(commune, period):
        NB_HABITANT_NEUTRALISE = -9999
        date_creation_commune = commune("date_creation_commune", period)
        annee_suivante_creation_commune = date_creation_commune.astype('datetime64[Y]') + 1

        # la population est accessible année par année
        # les communes ont des dates de création très variables
        # on identifie donc les dates de création des communes (de toute la France) sans doublon
        # pour récupérer la population connue pour chaque commune l'année suivant sa création
        bilan_annees_suivant_creation_communes = unique(annee_suivante_creation_commune)

        # on crée un array/matrice avec :
        # - nb de lignes : nb d'années de création (sans doublon)
        # - nb de colonnes : nb de communes
        # - valeur par défaut : NB_HABITANT_NEUTRALISE
        nombre_communes = date_creation_commune.size
        matrice_population_insee_initiale = full((bilan_annees_suivant_creation_communes.size, nombre_communes), NB_HABITANT_NEUTRALISE)

        # boucle : pour chaque année de création, on recherche :
        # - la population de chaque commune (population_insee_annee)
        # - si l'année correspond à la date de création d'une ou plusieurs communes (filtre_annee_initiale)
        # on remplit la matrice population_insee_initiale grâce à l'information obtenue avec ces deux arrays
        for index, annee in enumerate(bilan_annees_suivant_creation_communes):
            # pour une 'annee' donnée = une année suivant la création d'une commune ou plus
            population_insee_annee = commune("population_insee", str(annee))

            # on constitue une colonne où pour chaque commune
            # si 'annee' est l'année suivant sa création, on a la population insee officielle
            filtre_annee_initiale = annee_suivante_creation_commune == annee

            # on ajoute les informations à la matrice avec un np.where :
            # - si l'année correspond à l'année initiale, on ajoute la population de l'année initiale
            # - sinon, valeur par défaut -9999
            matrice_population_insee_initiale[index] = where(filtre_annee_initiale, population_insee_annee, NB_HABITANT_NEUTRALISE)

        population_insee_initiale = numpy_max(matrice_population_insee_initiale, axis=0)
        return population_insee_initiale


class population_dgf(Variable):
    value_type = int
    entity = Commune
    label = "Population au sens DGF de la commune"
    reference = [
        'Code général des collectivités territoriales - Article L2334-2',
        'https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051220677'
        ]
    definition_period = YEAR

#     def formula(commune, period, parameters):
#         insee = commune('population_insee', period)
#         nb_resid_second = commune('nb_residences_secondaires', period)
#         nb_caravanes = commune('nb_caravanes', period)
#         dsu_nm1 = commune('dotation_solidarite_urbaine', period.last_year)
#         pfrac_dsu_nm1 = commune('premiere_fraction_dotation_solidarite_rurale', period.last_year)
#
#         return (
#             + insee
#             + 1 * nb_resid_second
#             + 1 * nb_caravanes
#             + 1 * nb_caravanes * ((dsu_nm1 > 0) + (pfrac_dsu_nm1 > 0))
#             )


class population_dgf_plafonnee(Variable):
    value_type = int
    entity = Commune
    label = "Population au sens DGF de la commune, plafonnée en fonction de la population INSEE"
    reference = [
        'https://www.legifrance.gouv.fr/affichCodeArticle.do;jsessionid=849B2A0736FF63D09762D4F7CE98FC9C.tplgfr31s_2?idArticle=LEGIARTI000036433099&cidTexte=LEGITEXT000006070633',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    definition_period = YEAR
    documentation = '''
    La population prise en compte est celle définie à l'article L. 2334-21 :
    – plafonnée à 500 habitants pour les communes dont la population issue du dernier recensement est inférieure à 100 habitants ;
    – plafonnée à 1 000 habitants pour les communes dont la population issue du dernier recensement est comprise entre 100 et 499 habitants ;
    – plafonnée à 2 250 habitants pour les communes dont la population issue du dernier recensement est comprise entre 500 et 1 499 habitants.
    Ce plafond s'applique uniquement à la population de la commune concernée et n'intervient pas dans le calcul du potentiel financier par habitant.
    '''

    def formula(commune, period, parameters):
        population_dgf = commune('population_dgf', period)
        population_insee = commune('population_insee', period)
        bareme_plafond_dgf = parameters(period).population.plafond_dgf

        # pour les communes  à la population insee < à la clef, la population dgf est plafonnée à value
        return min_(bareme_plafond_dgf.calc(population_insee), population_dgf)


class population_dgf_majoree(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Population DGF majorée:\
        Population DGF majorée pour le calcul de la dotation forfaitaire"
    reference = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006192290?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF#LEGISCTA000006192290"
    documentation = '''
        La population de la commune prise en compte au titre de 2019 est celle définie à l'article L. 2334-2
        du présent code majorée de 0,5 habitant supplémentaire par résidence secondaire pour les communes
        dont la population est inférieure à 3 500 habitants, dont le potentiel fiscal par habitant
        est inférieur au potentiel fiscal moyen par habitant des communes appartenant à la même
        strate démographique et dont la part de la majoration au titre des résidences secondaires
        dans la population avant application de la présente disposition est supérieure à 30 %.
        '''


class population_enfants(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombre d'habitants de 3 à 16 ans (selon le dernier recensement)"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"


class population_qpv(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Population QPV:\
        Population des quartiers prioritaires de politique de la ville"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"


class population_zfu(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Population ZFU:\
        Population des zones franches urbaines de la commune"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"
