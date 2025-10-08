# Changelog

## 4.8.0 [!47](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/47)

* Évolution du système socio-fiscal.
* Périodes concernées : à partir du 01/01/1996
* Zones impactées :
  - `parameters/dotation_solidarite_urbaine/`
* Détails :
  - Ajoute la valeur 2025 des enveloppes DSU `dotation_solidarite_urbaine.montant.*` et `dotation_solidarite_urbaine.augmentation_montant`
  - Corrige le format de tous les paramètres DSU 
    - Toutes les URL légifrance désignent un article unique avec date d'entrée en application
    - Corrige les dates d'entrée en application de tous les paramètres DSU
    - Rassemble les métadonnées dans `metadata` avec `last_value_still_valid_on` et `unit`

## 4.7.0 [!46](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/46)

* Évolution du système socio-fiscal.
* Périodes concernées : à partir du 01/01/2024
* Zones impactées :
  - `parameters/dotation_communes_nouvelles/`
* Détails :
  - Ajoute en paramètres les montants totaux notifiés de DCN 2024 et 2025
    * Crée `dotation_communes_nouvelles.montant`, `dotation_communes_nouvelles.amorcage.montant` et `dotation_communes_nouvelles.garantie.montant`
  - Ajoute `last_value_still_valid_on` à tous les autres paramètres de DCN
  - Introduit l'unité `inhabitant`

## 4.6.0 [!43](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/43)

* Évolution du système socio-fiscal.
* Périodes concernées : à partir du 01/01/1996
* Zones impactées :
  - `parameters/dotation_solidarite_rurale/*`
* Détails :
  - Revalorise l'ensemble des paramètre `DSR` pour 2025
  - Corrige les `reférence` législatives de tous les paramètres
    - Déplace la référence dans `metadata` lorsqu'elle n'y est pas déjà
    - Corrige les liens légifrance afin qu'ils soient à la date d'entrée en vigueur concernée
    - Met à jour la date d'entrée en vigueur lorsque la référence est antérieure à ce qui précédait (1996 au lieu de 2019 en particulier)
    - Pour les paramètres non revalorisés annuellement, ajoute `last_value_still_valid_on`

## 4.5.0 [!42](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/42)

* Évolution du système socio-fiscal.
* Périodes concernées : à partir du 01/01/2022
* Zones impactées :
  - `parameters/montant_dotation_globale_fonctionnement.yaml`
  - `parameters/dotation_intercommunalite/augmentation_montant.yaml`
  - `parameters/dotation_forfaitaire/montant.yaml`
  - `parameters/dotation_forfaitaire/ecretement/plafond_pourcentage_recettes_max.yaml`
  - `parameters/dotation_forfaitaire/montant_minimum_par_habitant.yaml`
  - `parameters/dotation_forfaitaire/montant_maximum_par_habitant.yaml`
  - `variables/dotation_forfaitaire.py`
  - `variables/potentiel_fiscal.py`
  - `variables/population.py`
* Détails :
  - Ajoute la valeur 2025 de l'enveloppe `DGF` `montant_dotation_globale_fonctionnement`
  - Met à jour la `DF` pour 2025
    - Ajoute la valeur 2025 de `dotation_forfaitaire.montant.total`
    - Ajoute la valeur 2024+ de `dotation_intercommunalite.augmentation_montant` intervenant dans le calcul d'écrêtement `DF`
    - Ajoute les valeurs 2025, 2024 et 2022 de `potentiel_fiscal_moyen_national` intervenant dans le calcul d'écrêtement `DF`
  - Améliore la modélisation de la `DF`
    - Ajoute la variable `df_montant_ecretement_spontane` par extraction du calcul de `df_montant_ecretement`
    - Ajoute la variable `df_valeur_point_ecretement` par extraction du calcul de `df_montant_ecretement_spontane`
    - Extrait en paramètre `dgf_part_ecretement_attribue_df` le taux employé par `df_montant_total_ecretement`
    - Corrige les références de paramètres de `dotation_forfaitaire` `montant_minimum_par_habitant`, `montant_maximum_par_habitant` et `ecretement.plafond_pourcentage_recettes_max`
    - Documente `montant_total_ecretement` et `df_montant_total_ecretement`

### 4.4.2 [!45](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/45)

* Correction d'un crash technique.
* Périodes concernées : non applicable.
* Zones impactées : `.gitlab-ci.yml`
* Détails :
  * Corrige l'erreur `twine: command not found` sur le job de CI `deploy-wheel` exécuté sur la branche principale
    * Erreur introduite par la version `4.4.1` 

### 4.4.1 [!44](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/44)

* Correction d'un crash technique.
* Périodes concernées : non applicable.
* Zones impactées : `.gitlab-ci.yml`
* Détails :
  * Lie le job de CI `deploy-wheel` à la bonne exécution de `release-and-tag` en remplacement de `build`
    * Evite une ré-exécution de `has-functional-changes.sh` pouvant échouer
    * Corrige la non publication de wheel sur PyPi suite à `No functional changes detected.`

## 4.4.0 [!41](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/41)

* Évolution du système socio-fiscal.
* Périodes concernées : à partir du 01/01/2020
* Zones impactées :
  - `parameters/dotation_solidarite_rurale/`
  - `parameters/dotation_solidarite_urbaine/`
  - `parameters/dotation_amenagement_communes_outre_mer/`
  - `parameters/dotation_nationale_perequation/`
  - `variables/dotation_forfaitaire.py`
* Détails :
  - Pour chacune de la `DSR` et de la `DSU`, distingue la majoration décidée par le Comité des finances locales de l'augmentation d'enveloppe de l'article L.2334-13 du CGCT
    - Crée un paramètre `dotation_solidarite_rurale/majoration_montant` et `dotation_solidarite_urbaine/majoration_montant`
    - À partir de 2020, soustrait la majoration de `dotation_solidarite_rurale/augmentation_montant` et `dotation_solidarite_urbaine/augmentation_montant`
    - Met à jour `montant_total_ecretement` de la `DF` en cohérence
  - Ajoute le premier paramètre de la `DACOM` : `dotation_amenagement_communes_outre_mer.montant`
  - Ajoute les premiers paramètres de la `DNP` : `dotation_nationale_perequation.montant.total`, `metropole` et `outre_mer`
  - Ajoute les notes DGCL 2025 à `REFERENCES.md`
  - Corrige le job de CI `check-version` en l'associant aux runners GitLab ayant le tag `leximpact-shared-cache`

### 4.3.0 [!40](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/40)

* Correction d'un crash technique.
* Périodes concernées : A partir du 01/01/2020
* Zones impactées :
  - `variables/dotation_solidarite_rurale_fractions/bourg_centre.py`
* Détails :
  - Corrige le calcul de `dsr_montant_total_fraction_bourg_centre` à partir du montant de l'année précédente. 
  - Applique la même logique que le calcul des autres fractions de la DSR.

## 4.2.0 [!39](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/39)

* Évolution du système socio-fiscal.
* Périodes concernées : 01/01/2017
* Zones impactées :
  - `parameters/population/groupes_demographiques.yaml`
  - `variables/population.py`
* Détails :
  - Extrait de `strate_demographique` les seuils de strates en un paramètre `population.groupes_demographiques`
  - Définit en CI que les runners GitLab doivent avoir pour tag `leximpact-shared-cache`

### 4.1.1 [!38](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/38)

* Évolution du système socio-fiscal.
* Périodes concernées : toutes.
* Zones impactées :
  - `variables/population.py`
* Détails :
  - Corrige le calcul de date dans `population_insee_initiale`
    * Produisait la `ValueError: Expected a period (eg. '2017', '2017-01', '2017-01-01', ...); got: '2'`
  - Déplace le test `test_base_communes_nouvelles.yaml` dans un répertoire dédié à la DCN `tests/dotation_communes_nouvelles/`
  - Ajoute un sommaire au `README.md` et liste les dépôts réutilisateurs du modèle identifiés à ce jour

## 4.1.0 [!36](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/36)

* Évolution du système socio-fiscal.
* Périodes concernées : toutes.
* Zones impactées :
  - `/parameters/dotation_communes_nouvelles/amorcage/montant_attribution.yaml`
  - `/parameters/dotation_communes_nouvelles/amorcage/plafond_age_commune.yaml`
  - `/parameters/dotation_communes_nouvelles/amorcage/seuil_age_commune.yaml`
  - `/parameters/dotation_communes_nouvelles/eligibilite/plafond_nombre_habitants.yaml`
  - `/parameters/dotation_globale_fonctionnement/communes/taux_evolution.yaml`
  - `/variables/base.py`
  - `/variables/dotation_communes_nouvelles.py`
  - `/variables/dotation_globale_fonctionnement.py`
  - `/variables/dotation_nationale_perequation.py`
  - `/variables/dotation_solidarite_rurale.py`
  - `/variables/dotation_solidarite_urbaine.py`
  - `/variables/population.py`
  - `/variables/zone_de_montagne.py`
* Détails :
  - Pour 2024, ajoute le calcul `dotation_communes_nouvelles` par le calcul de ses deux parts
    * Ajoute `dotation_communes_nouvelles_eligible_part_amorcage` et `dotation_communes_nouvelles_part_amorcage`
    * Ajoute `dotation_communes_nouvelles_eligible_part_garantie` et `dotation_communes_nouvelles_part_garantie`
  - Ajoute `date_creation_commune`, `commune_nouvelle`, `age_commune` et calcule `population_insee_initiale`
  - Ajoute des éléments de la DGF pour calculer la part garantie de la dotation en faveur des communes nouvelles (DCN)
    * Initie le calcul de `dotation_globale_fonctionnement_communes`
    * Ajoute `dotation_nationale_perequation`, `dgf_reference_communes_spontanee` et `dotation_globale_fonctionnement_reference_communes` sans formule
  - Ajoute `taux_proratisation_population_commune_nouvelle` et `taux_evolution_dgf` afin de couvrir tous les concepts de la note DGCL DCN 2024

# 4.0.0 [!37](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/37)

* Évolution du système socio-fiscal non rétro-compatible.
* Périodes concernées : à partir du 01/01/2020.
* Zones impactées :
  - `parameters/dotation_solidarite_rurale/bourg_centre/montant.yaml`
  - `parameters/dotation_solidarite_rurale/cible/montant.yaml`
  - `parameters/dotation_solidarite_rurale/perequation/montant.yaml`
  - `variables/dotation_solidarite_rurale_fractions/bourg_centre.py`
  - `variables/dotation_solidarite_rurale_fractions/cible.py`
  - `variables/dotation_solidarite_rurale_fractions/perequation.py`
  - `variables/dotation_solidarite_urbaine.py`
* Détails :
  - Renomme `dsr_pourcentage_accroissement_bourg_centre` en `dsr_bourg_centre_accroissement_metropole` par cohérence d'ensemble
  - Modifie le calcul du pourcentage d'augmentation d'enveloppe en DSR et DSU : `dsr_bourg_centre_accroissement_metropole`, `dsr_perequation_accroissement_metropole`, `dsr_cible_accroissement_metropole` et `dsu_accroissement_metropole`
    * Évolue d'un % au rapport de l'augmentation d'enveloppe de l'année en cours à un rapport à l'enveloppe totale de l'année passée
  - Ajoute les montants alloués en 2024 au titre de chacune des trois fractions de DSR

### 3.0.2 [!35](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/35)

* Correction d'un crash technique.
* Périodes concernées : non applicable.
* Zones impactées : `.gitlab-ci.yml`
* Détails :
  * Corrige le déploiement sur PyPi assuré par le job `deploy` en CI
  * En CI, renomme le job `deploy` en `deploy-wheel` et le précède d'un nouveau `release-and-tag` ne nécessitant plus de token annuel
  * Déplace les scripts de CI de `.ci/` à `.gitlab/ci/`

### 3.0.1 [!34](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/34)

* Évolution du système socio-fiscal.
* Périodes concernées : à partir du 01/01/2024.
* Zones impactées :
  - `parameters/dotation_forfaitaire/montant.yaml`
  - `parameters/dotation_solidarite_rurale/augmentation_montant.yaml`
  - `parameters/dotation_solidarite_rurale/montant.yaml`
  - `parameters/dotation_solidarite_urbaine/augmentation_montant.yaml`
  - `parameters/dotation_solidarite_urbaine/montant.yaml`
* Détails :
  - Met à jour la répartition d'enveloppe DF, DSR et DSU 2024 suite à la décision du Comité des finances locales
  - Ajoute les notes DGCL 2024 à `REFERENCES.md`

# 3.0.0 [!31](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/31)

* Évolution du système socio-fiscal non rétro-compatible.
* Périodes concernées : à partir du 01/01/2020.
* Zones impactées :
  - `parameters/dotation_forfaitaire/montant.yaml`
  - `parameters/dotation_solidarite_rurale/augmentation_montant.yaml`
  - `parameters/dotation_solidarite_rurale/bourg_centre/montant.yaml`
  - `parameters/dotation_solidarite_rurale/cible/montant.yaml`
  - `parameters/dotation_solidarite_rurale/montant.yaml`
  - `parameters/dotation_solidarite_rurale/perequation/montant.yaml`
  - `parameters/dotation_solidarite_urbaine/attribution/augmentation_max.yaml`
  - `parameters/dotation_solidarite_urbaine/augmentation_montant.yaml`
  - `parameters/dotation_solidarite_urbaine/eligibilite/seuil_haut_nombre_habitants.yaml`
  - `parameters/dotation_solidarite_urbaine/montant.yaml`
  - `parameters/montant_dotation_globale_fonctionnement.yaml`
* Détails :
  - Renomme le paramètre `montant_dotation_globale_fonctionnament` en `montant_dotation_globale_fonctionnement` (typo) et corrige son montant 2019
  - Met à jour l'enveloppe globale de DGF tout échelon de 2020 à 2024
  - Met à jour les enveloppes communales publiées dans la loi pour la DF, DSR et DSU de 2023 et 2024

### 2.0.2 [!32](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/32)

* Changement mineur.
* Périodes concernées : toutes.
* Zones impactées : `README`.
* Détails :
  - Initie une documentation sur l'exemple d'[openfisca-france](https://github.com/openfisca/openfisca-france/blob/b23b17ec12e74a0766b10eef1523b8153c14ad04/README.md).
  - Intègre l'évolution de version de Python vers Python 3.11.

### 2.0.1 [!30](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/30)

* Correction d'un crash.
* Périodes concernées : non applicable.
* Zones impactées :
  - `parameters/dotation_solidarite_urbaine/eligibilite/*`.
  - `parameters/dotation_solidarite_urbaine/attribution/*`.
* Détails :
  - Corrige le job `deploy` de l'intégration continue 
    * Emploie un token pour l'identification sur PyPi suite à l'obligation de passer par la double authentification 
  - Corrige le format des liens legifrance des paramètres de la DSU
  - Référence les derniers documents officiels pour la DGF 2023 des communes

# 2.0.0 [!29](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/29)

* Amélioration technique.
* Périodes concernées : toutes.
* Zones impactées : `setup.py`
* Détails :
  - Met à jour la version Python de référence de la v`3.7` à la v`3.11`
  - Met à jour OpenFisca-Core de la v`38` à la v`41`
  - Migre les templates de déclaration de problèmes et propositions de modification de GitHub à GitLab

# 1.0.0 [!28](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/merge_requests/28)

* Amélioration technique.
* Périodes concernées : toutes.
* Zones impactées : `setup.py`.
* Détails :
  - Met à jour `OpenFisca-Core` à la dernière version compatible Python 3.7 ([v.38.0.4](https://github.com/openfisca/openfisca-core/tree/38.0.4))
  - Met à jour les dépendances de `dev` en gérant les incompatibilités
  - Corrige un `DtypeWarning` pour `test_data.py` 

## 0.9.0 [!26](https://git.leximpact.dev/leximpact/openfisca-france-dotations-locales/-/merge_requests/26)

* Évolution du système socio-fiscal.
* Périodes concernées : toutes.
* Zones impactées : `variables/base.py`
* Détails :
  - Ajoute les variables communales `nom` et `code_insee`
  - Facilite la réidentification des communes dans la simulation

### 0.8.1 [!24](https://git.leximpact.dev/leximpact/openfisca-france-dotations-locales/-/merge_requests/24)

* Évolution du système socio-fiscal.
* Périodes concernées : à partir du 01/01/2022.
* Zones impactées :
  - `parameters/dotation_forfaitaire/montant.yaml`
  - `parameters/dotation_forfaitaire/ecretement/seuil_rapport_potentiel_fiscal.yaml`
* Détails :
  - Met à jour la DF pour 2022
    * Enveloppe totale
    * Pour l'écrêtement, le plafond de potentiel fiscal par habitant de la commune au regard du potentiel fiscal par habitant moyen de la strate

## 0.8.0 [!22](https://git.leximpact.dev/leximpact/openfisca-france-dotations-locales/-/merge_requests/22)

* Évolution du système socio-fiscal.
* Périodes concernées : toutes.
* Zones impactées :
  - `parameters/dotation_forfaitaire/montant.yaml`
  - `parameters/dotation_solidarite_rurale/bourg_centre/montant.yaml`
  - `parameters/dotation_solidarite_rurale/cible/montant.yaml`
  - `parameters/dotation_solidarite_rurale/perequation/montant.yaml`
  - `parameters/dotation_solidarite_rurale/augmentation_montant.yaml`
  - `parameters/dotation_solidarite_rurale/montant.yaml`
  - `parameters/dotation_solidarite_urbaine/augmentation_montant.yaml`
  - `parameters/dotation_solidarite_urbaine/montant.yaml`
  - `variables/dotation_solidarite_rurale_fractions/*`
  - `variables/dotation_solidarite_urbaine.py`
* Détails :
  - DF : ajoute depuis 2019 `dotation_forfaitaire.montant.total`
  - DSR : ajoute depuis 2019 `dotation_solidarite_rurale.montant.[total/metropole/outre_mer]` et le montant total de chacune des fractions en métropole
  - DSU : ajoute depuis 2019 `dotation_solidarite_urbaine.montant.[total/metropole/outre_mer]`
  - Pour 2022, intègre les revalorisations de DSR et DSU.

### 0.7.7 [!23](https://git.leximpact.dev/leximpact/openfisca-france-dotations-locales/-/merge_requests/23)

* Amélioration technique.
* Périodes concernées : toutes.
* Zones impactées : non applicable
* Détails :
  - Ajoute le git tag automatique en GitLab CI.

### 0.7.6 [!21](https://git.leximpact.dev/openfisca/openfisca-france-dotations-locales/-/merge_requests/21)

* Amélioration technique.
* Périodes concernées : toutes.
* Zones impactées : `/parameters` (indirectement).
* Détails :
  - Ajoute la validation des YAML des paramètres en GitLab CI.

### 0.7.5 [!18](https://git.leximpact.dev/openfisca/openfisca-france-dotations-locales/-/merge_requests/18)

* Évolution du système socio-fiscal.
* Périodes concernées: 2021
* Zones impactées :
  - DSU
  - DSR toutes fractions
* Détails :
  - Revalorise l'ensemble pour 2021 suite à l'augmentation de l'enveloppe globale et à la publication des notes DGCL. 
  - Ajoute un notebook. 

### 0.7.4 [!17] (https://git.leximpact.dev/leximpact/openfisca-france-dotations-locales/-/merge_requests/17)

* Changement mineur.
* Périodes concernées : toutes.
* Zones impactées :
  - `.circleci/*` → `.ci/*`
  - `.gitlab-ci.yml`
  - `openfisca_france_dotations_locales/entities.py`.
* Détails :
  - Migre l'intégration continue CircleCI vers la CI GitLab
  - Met à jour la documentation de l'entité `Commune` pour tester la nouvelle CI

### 0.7.3 [#15] (https://github.com/leximpact/openfisca-france-dotations-locales/pull/15)

* Changement mineur.
* Périodes concernées : toutes.
* Zones impactées : `openfisca_france_dotations_locales/variables/base.py`.
* Détails :
  - Suppression des warnings 'divide by zero' dans la fonction custom de division que nous avons écrite (et qui fait bien attention à ne pas diviser par zéro)

### 0.7.2 [#14](https://github.com/leximpact/openfisca-france-dotations-locales/pull/14)

* Amélioration technique.
* Périodes concernées : toutes. 
* Zones impactées : `openfisca-france-dotations-locales/openfisca_france_dotations_locales/variables/dotation_solidarite_urbaine.py`.
* Détails :
  - Création d'une fonction custom de division, safe_divide, qui effectue une division mais renvoie une valeur par défaut si on essaye de diviser par zéro.
  
  ### 0.7.1 [#13](https://github.com/leximpact/openfisca-france-dotations-locales/pull/13)

* Amélioration technique.
* Périodes concernées : toutes.
* Zones impactées : toutes.
* Détails :
  - Met à jour la dépendance à OpenFisca-Core.
  - Permet l'emploi de `numpy` v1.18 apporté par [OpenFisca-Core v35](https://github.com/openfisca/openfisca-core/blob/a8d91949b522b5a214a5b44c88ce85b19277ec8b/CHANGELOG.md#3500-954) et influe sur les syntaxes autorisées des formulas.

## 0.7.0 [#12](https://github.com/leximpact/openfisca-france-dotations-locales/pull/12)

* Évolution du système socio-fiscal.
* Détails :
  - Ajoute le calcul des montants de la Dotation forfaitaire

## 0.6.0 [#11](https://github.com/leximpact/openfisca-france-dotations-locales/pull/11)

* Évolution du système socio-fiscal.
* Détails :
  - Définit des paramètres par défaut pour 2021 (à 0) sur l'augmentation des montants DSR/DSU

## 0.5.0 [#10](https://github.com/leximpact/openfisca-france-dotations-locales/pull/10)

* Évolution du système socio-fiscal.
* Détails :
  - Précise le calcul de la DSR : garanties
  - Ajoute le calcul des augmentations de montant de la DSU et de la DSR
  - Ajoute l'entité État

## 0.4.0 [#9](https://github.com/leximpact/openfisca-france-dotations-locales/pull/9)

* Évolution du système socio-fiscal.
* Détails :
  - Ajoute le calcul des montants de la DSU

## 0.3.1 [#8](https://github.com/leximpact/openfisca-france-dotations-locales/pull/8)

* Évolution du système socio-fiscal.
* Détails :
  - Ajoute un paramètre : le ratio maximum de potentiel financier. 

## 0.3.0 [#7](https://github.com/leximpact/openfisca-france-dotations-locales/pull/7)

* Évolution du système socio-fiscal.
* Détails :
  - Ajoute le calcul des montants hors garantie de la DSR pour les trois fractions de la DSR.

### 0.2.1 [#5](https://github.com/leximpact/openfisca-france-dotations-locales/pull/5)

* Changement mineur et correction d'un crash en CI.
* Détails :
  - Changement de la gestion des ratios : ils sont maintenant égaux à 0 quand le dénominateur est égal à 0
  - En CI, teste désormais le code source (et non plus la wheel) afin de résoudre un manque de mise à jour du cache `v1-py37-deps-{{ .Branch }}-{{ checksum "setup.py" }}`

## 0.2.0 [#4](https://github.com/leximpact/openfisca-france-dotations-locales/pull/4)

* Évolution du système socio-fiscal.
* Détails :
  - Ajoute, pour la DSR, l'éligibilité à la fraction cible.

## 0.1.0 [#3](https://github.com/leximpact/openfisca-france-dotations-locales/pull/3)

* Premier versionnement d'OpenFisca-France-Dotations-Locales.
* Amélioration technique.

## Hérité du country-tempate openfisca

> Pour plus d'information, consulter le [dépôt du country-tempate](https://github.com/openfisca/country-template).

### 3.9.10 - [#86](https://github.com/openfisca/country-template/pull/86)

* Technical change.
* Details:
  - Fix installation and building operations by fixing the bootstrap script.

### 3.9.9 - [#85](https://github.com/openfisca/country-template/pull/85)

* Minor change.
* Details:
  - Add `make serve-local` command to Makefile.

### 3.9.8 - [#83](https://github.com/openfisca/country-template/pull/83)

* Minor change.
* Details:
  - Add additional example JSON file; add to README.

### 3.9.7 - [#80](https://github.com/openfisca/country-template/pull/80)

* Minor change.
* Details:
  - Upgrade `autopep8`

### 3.9.6 - [#78](https://github.com/openfisca/country-template/pull/78)

* Minor change.
* Details:
  - Declare package compatible with Core v34

### 3.9.5 - [#76](https://github.com/openfisca/country-template/pull/76)

* Minor change.
* Details:
  - Declare package compatible with Core v32

### 3.9.4 - [#75](https://github.com/openfisca/country-template/pull/75)

* Minor change.
* Details:
  - Upgrade `autopep8`

### 3.9.3 - [#73](https://github.com/openfisca/country-template/pull/73)

* Minor change.
* Details:
  - Upgrade `autopep8`

### 3.9.2 - [#71](https://github.com/openfisca/country-template/pull/71)

* Minor change.
* Details:
  - Upgrade `flake8` and `pycodestyle`

### 3.9.1 - [#74](https://github.com/openfisca/country-template/pull/74)

* Minor change.
* Details:
  - Explicit expected test output

## 3.9.0 - [#72](https://github.com/openfisca/country-template/pull/72)

* Technical change
* Details:
  - Declare package compatible with Core v31

## 3.8.0 - [#69](https://github.com/openfisca/country-template/pull/69)

* Technical change
* Details:
  - Declare package compatible with Core v27

## 3.7.0 - [#68](https://github.com/openfisca/country-template/pull/68)

* Technical change
* Details:
  - Declare package compatible with Core v26
  - Remove Python 2 checks from continuous integration

## 3.6.O - [#66](https://github.com/openfisca/country-template/pull/66)

* Minor change
* Details:
  - Adapt to OpenFisca Core v25
  - Change the syntax of OpenFisca YAML tests

For instance, a test that was using the `input_variables` and the `output_variables` keywords like:

```yaml
- name: Basic income
  period: 2016-12
  input_variables:
    salary: 1200
  output_variables:
    basic_income: 600
```

becomes:

```yaml
- name: Basic income
  period: 2016-12
  input:
    salary: 1200
  output:
    basic_income: 600
```

A test that was fully specifying its entities like:

```yaml
name: Housing tax
  period: 2017-01
  households:
    - parents: [ Alicia ]
      children: [ Michael ]
  persons:
    - id: Alicia
        birth: 1961-01-15
    - id: Michael
        birth: 2002-01-15
  output_variables:
    housing_tax:
      2017: 1000
```

becomes:

```yaml
name: Housing tax
  period: 2017-01
  input:
    household:
      parents: [ Alicia ]
      children: [ Michael ]
    persons:
      Alicia:
        birth: 1961-01-15
      Michael:
        birth: 2002-01-15
  output:
    housing_tax:
      2017: 1000
```

### 3.5.4 - [#65](https://github.com/openfisca/country-template/pull/65)

* Minor change
* Details:
  - Update links to the doc

### 3.5.3 - [#64](https://github.com/openfisca/country-template/pull/64)

* Minor change
* Details:
  - Document housing tax

### 3.5.2 - [#59](https://github.com/openfisca/country-template/pull/59) [#62](https://github.com/openfisca/country-template/pull/62) [#63](https://github.com/openfisca/country-template/pull/63)

* Technical change
* Details:
  - Tests library against its packaged version
  - By doing so, we prevent some hideous bugs

> Note: Version `3.5.1` has been unpublished as it accidentally introduced a bug. Please use version `3.5.2` or more recent.

## 3.5.0 - [#58](https://github.com/openfisca/country-template/pull/58)

* Technical change
  - In the `/spec` Web API route, use examples that apply to this country package

## 3.4.0

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `housing`
* Details:
  - Introduce `code_postal` variable

### 3.3.2

* Minor change
* Details:
  - Update entities labels

### 3.3.1 - [#53](https://github.com/openfisca/country-template/pull/53)

* Minor change
* Details:
  - Add `documentation` to parameters: `benefits` node and `benefits/housing_allowance`
  - Add documentation to `housing_allowance` variable and formula

### 3.3.0 - [#51](https://github.com/openfisca/country-template/pull/51)

* Technical change
  - Make package compatible with OpenFisca Core v24
  - Rename development dependencies from `test` to `dev`:

### 3.2.3 - [#50](https://github.com/openfisca/country-template/pull/50)

* Minor change
* Details:
  - Fix repository URL in package metadata

### 3.2.2 - [#49](https://github.com/openfisca/country-template/pull/49)

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `taxes`
* Details:
  - Implement housing tax minimal amount

<!-- -->

* Minor change
* Details:
  - Add metadata to parameters

### 3.2.1 - [#47](https://github.com/openfisca/country-template/pull/47)

* Minor change.
* Details:
  - Make boostrap script portable.

## 3.2.0 - [#43](https://github.com/openfisca/country-template/pull/43)

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `demographics`
* Details:
  - Improve reliability and accuracy of `age` formula
  - Improve variables comments

### 3.1.3 - [#37](https://github.com/openfisca/country-template/pull/37)

* Minor change.
* Details:
  - Upgrade openfisca.org references to HTTPS.

### 3.1.2 - [#38](https://github.com/openfisca/country-template/pull/38)

* Minor change.
* Details:
  - Add situation example using YAML

### 3.1.1 - [#44](https://github.com/openfisca/country-template/pull/44)

* Technical improvement.
* Details:
  - Continuously deploy Python3 package.

## 3.1.0 - [#41](https://github.com/openfisca/country-template/pull/41)

* Technical improvement.
* Details:
  - Make package compatible with Python 3

### 3.0.2 - [#37](https://github.com/openfisca/country-template/pull/37)

* Technical change.
* Declare package compatible with OpenFisca Core v23

### 3.0.1 - [#39](https://github.com/openfisca/country-template/pull/39)

* Technical change.
* Declare package compatible with OpenFisca Core v22

# 3.0.0 - [#34](https://github.com/openfisca/country-template/pull/34)

#### Breaking change

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `housing`
* Details:
  - Fix spelling by renaming `accomodation_size` variable to `accommodation_size`

#### Other changes

* Minor change.
* Impacted areas: no functional impact.
* Details:
  - Improve spelling

## 2.1.0 - [#29](https://github.com/openfisca/country-template/pull/29) [#30](https://github.com/openfisca/country-template/pull/30)

* Tax and benefit system evolution
* Impacted areas:
  - Parameters `general`
  - Variables `benefits`
* Details:
  - Add a parameter and a variable with non ascii characters
    - Introduce `age_of_retirement` parameter
    - Introduce `pension` variable

## 2.0.1 - [#24](https://github.com/openfisca/country-template/pull/24) [#27](https://github.com/openfisca/country-template/pull/27)

_Note: the 2.0.0 version has been unpublished due to performance issues_

#### Breaking change

* Details:
  - Upgrade to Core v21
  - Introduce the use of a string identifier to reference Enum items.
  - When setting an Enum (e.g. housing_occupancy_status), set the relevant string identifier (e.g. `free_lodger`). Indexes (e.g.`2`) and phrases (e.g. `Free Lodgers`) cannot be used anymore.
  - The default value is indicated for each Enum variable instead of being implicitly the first item of the enum.

#### Web API request/response

Before:

```
"persons": {
    "Bill": {}
},
"households": {
    "_": {
        "parent": ["Bill"]
        "housing_occupancy_status": "Free Lodger"
    }
}
```
Now:

```
"persons": {
    "Bill": {}
},
"households": {
    "_": {
        "parent": ["Bill"]
        "housing_occupancy_status": "free_lodger"
    }
}
```

#### YAML testing
Before:

```
name: Household living in a 40 sq. metres accommodation while being free lodgers
  period: 2017
  input_variables:
    accommodation_size:
      2017-01: 40
    housing_occupancy_status:
      2017-01: 2
  output_variables:
    housing_tax: 0
```
Now:

```
name: Household living in a 40 sq. metres accommodation while being free lodgers
  period: 2017
  input_variables:
    accommodation_size:
      2017-01: 40
    housing_occupancy_status:
      2017-01: free_lodger
  output_variables:
    housing_tax: 0
```

#### Python API

When calculating an enum variable in Python, the output will be an [EnumArray](https://openfisca.org/doc/openfisca-python-api/enum_array.html).

See more on the OpenFisca-Core [changelog](https://github.com/openfisca/openfisca-core/blob/enums-perfs/CHANGELOG.md#2102-589-600-605).

## 1.4.0 - [#26](https://github.com/openfisca/country-template/pull/26)

* Technical improvement
* Details:
  - Upgrade to Core v20

### 1.3.2 - [#25](https://github.com/openfisca/country-template/pull/25)

* Declare package compatible with OpenFisca Core v19

### 1.3.1 - [#23](https://github.com/openfisca/country-template/pull/23)

* Technical improvement
* Details:
  - Declare package compatible with OpenFisca Core v18

## 1.3.0 - [#22](https://github.com/openfisca/country-template/pull/22)

* Tax and benefit system evolution
* Impacted periods: all
* Impacted areas: `stats`
* Details:
  - Introduce `total_benefits`
  - Introduce `total_taxes`

<!-- -->

* Minor change
* Details:
  - Introduce situation examples
    - These examples can be imported with: `from openfisca_country_template.situation_examples import single, couple`

## 1.2.7 - [#21](https://github.com/openfisca/country-template/pull/21)

* Minor change
  - Use the technical documentation new address

## 1.2.6 - [#20](https://github.com/openfisca/country-template/pull/20)

* Minor change
  - Document entities

## 1.2.5 - [#17](https://github.com/openfisca/country-template/pull/17)

* Technical improvement
* Details:
  - Adapt to version `17.0.0` of Openfisca-Core
  - Transform XML parameter files to YAML parameter files.

## 1.2.4 - [#16](https://github.com/openfisca/country-template/pull/16)

* Tax and benefit system evolution
* Details
  - Introduce `housing_occupancy_status`
  - Take the housing occupancy status into account in the housing tax

## 1.2.3 - [#9](https://github.com/openfisca/country-template/pull/9)

* Technical improvement: adapt to version `15.0.0` of Openfisca-Core
* Details:
  - Rename Variable attribute `url` to `reference`

## 1.2.2 - [#12](https://github.com/openfisca/country-template/pull/12)

* Tax and benefit system evolution
* Details
  - Allow to declare a yearly amount for `salary`.
  - The yearly amount will be spread over the months contained in the year

## 1.2.1 - [#11](https://github.com/openfisca/country-template/pull/11)

* Technical improvement
* Details:
  - Make `make test` command not ignore failing tests.

## 1.2.0 - [#10](https://github.com/openfisca/country-template/pull/10)

* Technical improvement
* Details:
  - Upgrade OpenFisca-Core
    - Update the way we define formulas start dates and variables stop dates.
    - Update the naming conventions for variable formulas.
    - See the [OpenFisca-Core Changelog](https://github.com/openfisca/openfisca-core/blob/master/CHANGELOG.md#1400---522).

## 1.1.0 - [#7](https://github.com/openfisca/country-template/pull/7)

* Tax and benefit system evolution
* Impacted periods: from 2013-01-01
* Impacted areas:
   - Reform: `modify_social_security_taxation`
* Details:
  - Add a reform modifying the brackets of a scale
      - Show how to add, modify and remove a bracket.
      - Add corresponding tests.

# 1.0.0 - [#4](https://github.com/openfisca/country-template/pull/4)

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas:
  - `benefits`
  - `demographics`
  - `housing`
  - `income`
  - `taxes`
* Details:
  - Build the skeleton of the tax and benefit system
