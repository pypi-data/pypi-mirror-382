# OpenFisca-France-Dotations-Locales

[![Twitter](https://img.shields.io/badge/twitter-follow%20us!-9cf.svg?style=flat)](https://twitter.com/intent/follow?screen_name=openfisca)
[![Slack](https://img.shields.io/badge/slack-join%20us!-blueviolet.svg?style=flat)](mailto:contact%40openfisca.org?subject=Join%20you%20on%20Slack%20%7C%20Nous%20rejoindre%20sur%20Slack&body=%5BEnglish%20version%20below%5D%0A%0ABonjour%2C%0A%0AVotre%C2%A0pr%C3%A9sence%C2%A0ici%C2%A0nous%C2%A0ravit%C2%A0!%20%F0%9F%98%83%0A%0ARacontez-nous%20un%20peu%20de%20vous%2C%20et%20du%20pourquoi%20de%20votre%20int%C3%A9r%C3%AAt%20de%20rejoindre%20la%20communaut%C3%A9%20OpenFisca%20sur%20Slack.%0A%0AAh%C2%A0!%20Et%20si%20vous%20pouviez%20remplir%20ce%20petit%20questionnaire%2C%20%C3%A7a%20serait%20encore%20mieux%C2%A0!%0Ahttps%3A%2F%2Fgoo.gl%2Fforms%2F45M0VR1TYKD1RGzX2%0A%0AN%E2%80%99oubliez%20pas%20de%20nous%20envoyer%20cet%20email%C2%A0!%20Sinon%2C%20on%20ne%20pourra%20pas%20vous%20contacter%20ni%20vous%20inviter%20sur%20Slack.%0A%0AAmiti%C3%A9%2C%0AL%E2%80%99%C3%A9quipe%20OpenFisca%0A%0A%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%20ENGLISH%20VERSION%20%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%3D%0A%0AHi%2C%20%0A%0AWe're%20glad%20to%20see%20you%20here!%20%F0%9F%98%83%0A%0APlease%20tell%20us%20a%20bit%20about%20you%20and%20why%20you%20want%20to%20join%20the%20OpenFisca%20community%20on%20Slack.%0A%0AAlso%2C%20if%20you%20can%20fill%20out%20this%20short%20survey%2C%20even%20better!%0Ahttps%3A%2F%2Fgoo.gl%2Fforms%2FsOg8K1abhhm441LG2.%0A%0ADon't%20forget%20to%20send%20us%20this%20email!%20Otherwise%20we%20won't%20be%20able%20to%20contact%20you%20back%2C%20nor%20invite%20you%20on%20Slack.%0A%0ACheers%2C%0AThe%20OpenFisca%20Team)
[![Python](https://img.shields.io/pypi/pyversions/openfisca-france-dotations-locales.svg)](https://pypi.org/project/OpenFisca-France-Dotations-Locales/)
[![PyPi](https://img.shields.io/pypi/v/openfisca-france-dotations-locales.svg?style=flat)](https://pypi.org/project/OpenFisca-France-Dotations-Locales/)


## [EN] Introduction

OpenFisca is a versatile microsimulation free software. This repository contains the OpenFisca model of the State endowments to local authorities in France. Therefore, the working language here is French. You can however check the [general OpenFisca documentation](https://openfisca.org/doc/) in English!

## [FR] Introduction

[OpenFisca](https://www.openfisca.fr/) est un logiciel libre de micro-simulation. Ce dépôt contient la modélisation des dotations de l'État aux collectivités territoriales. Pour plus d'information sur les fonctionnalités et la manière d'utiliser OpenFisca, vous pouvez consulter la [documentation générale](https://openfisca.org/doc/).

## Sommaire

- [Installation](#installation)
  - [Installez un environnement virtuel avec Pew](#installez-un-environnement-virtuel-avec-pew)
  - [A. Installation minimale (pip install)](#a-installation-minimale-pip-install)
    - [Installer OpenFisca-France-Dotations-Locales avec pip install](#installer-openfisca-france-dotations-locales-avec-pip-install)
    - [Prochaines étapes](#prochaines-étapes)
  - [B. Installation avancée (Git Clone)](#b-installation-avancée-git-clone)
    - [Cloner OpenFisca-France-Dotations-Locales avec Git](#cloner-openfisca-france-dotations-locales-avec-git)
    - [Prochaines étapes](#prochaines-étapes-1)
- [Tests](#tests)
- [Style](#style)
- [Servir OpenFisca-France-Dotations-Locales avec l'API Web OpenFisca](#servez-openfisca-france-dotations-locales-avec-lapi-web-openfisca)
- [Stratégie de versionnement](#stratégie-de-versionnement)
- [Contributeurs](#contributeurs)
- [Références](#références)


## Installation

Ce paquet requiert [Python 3.11](https://www.python.org/downloads/release/python-3110/) et [pip](https://pip.pypa.io/en/stable/installing/) (ou `pip` dans un [environnement conda](https://www.anaconda.com/products/individual)).

Plateformes supportées :
- Distributions GNU/Linux (en particulier Debian and Ubuntu) ;
- Mac OS X ;
- Windows : Nous recommandons d'utiliser [conda](https://www.anaconda.com/products/individual) en association avec [pip](https://pip.pypa.io/en/stable/installing/) pour la facilité d'installation et sachant que la librairie d'OpenFisca-France-Dotations-Locales est publiée sur [PyPi](https://pypi.org/project/OpenFisca-France-Dotations-Locales/) mais pas sur conda. OpenFisca fonctionne également dans le [sous-système Windows pour Linux (WSL)](https://docs.microsoft.com/fr-fr/windows/wsl/install). Dans ce dernier cas, il suffit de suivre la procédure pour Linux car vous êtes alors dans un environnement Linux.

Pour les autres OS : si vous pouvez exécuter Python et Numpy, l'installation d'OpenFisca devrait fonctionner.

### Installez un environnement virtuel avec Pew

Nous recommandons l'utilisation d'un [environnement virtuel](https://virtualenv.pypa.io/en/stable/) (_virtualenv_) avec un gestionnaire de _virtualenv_ tel que [Pew](https://github.com/berdario/pew). Vous pouvez aussi utiliser le gestionnaire d'environnemnt officiel de Python : [venv](https://docs.python.org/3/library/venv.html).

- Un _[virtualenv](https://virtualenv.pypa.io/en/stable/)_ crée un environnement pour les besoins spécifiques du projet sur lequel vous travaillez.
- Un gestionnaire de _virtualenv_, tel que [Pew](https://github.com/berdario/pew), vous permet de facilement créer, supprimer et naviguer entre différents environnements.

Pour installer Pew, lancez une fenêtre de terminal et suivez ces instructions :

```sh
python --version # Python 3.11.0 ou plus récent devrait être installé sur votre ordinateur.
# Si non, téléchargez-le sur http://www.python.org et téléchargez pip.
```

```sh
pip install --upgrade pip
pip install pew
```
Créez un nouveau _virtualenv_ nommé **openfisca** et configurez-le avec python 3.11 :

```sh
pew new openfisca --python=python3.11
# Si demandé, répondez "Y" à la question sur la modification du fichier de configuration de votre shell
```
Le  _virtualenv_  **openfisca** sera alors activé, c'est-à-dire que les commandes suivantes s'exécuteront directement dans l'environnement virtuel. Vous verrez dans votre terminal :

```sh
Installing setuptools, pip, wheel...done.
Launching subshell in virtual environment. Type 'exit' or 'Ctrl+D' to return.
```

Informations complémentaires :
- sortez du _virtualenv_ en tapant `exit` (or Ctrl-D) ;
- re-rentrez en tapant `pew workon openfisca` dans votre terminal.

Bravo :tada: Vous êtes prêt·e à installer OpenFisca-France-Dotations-Locales !

Nous proposons deux procédures d'installation. Choisissez l'installation A ou B ci-dessous en fonction de l'usage que vous souhaitez faire d'OpenFisca-France-Dotations-Locales.  

### A. Installation minimale (pip install)

Suivez cette installation si vous souhaitez :
- procéder à des calculs sur toutes les collectivités ;
- créer des simulations des dotations ;
- écrire [une extension](https://openfisca.org/doc/architecture.html#extensions-packages) au-dessus de la législation française ;
- servir OpenFisca-France-Dotations-Locales avec l'[API Web OpenFisca](https://openfisca.org/doc/openfisca-web-api/index.html).

Pour pouvoir modifier OpenFisca-France-Dotations-Locales, consultez l'[Installation avancée](#b-installation-avancée-git-clone).

#### Installer OpenFisca-France-Dotations-Locales avec pip install

Dans votre _virtualenv_, vérifiez les pré-requis :

```sh
python --version  # Devrait afficher "Python 3.11.xx".
# Si non, vérifiez que vous passez --python=python3.11 lors de la création de votre environnement virtuel.
```

```sh
pip --version  # Devrait afficher au moins 23.x
# Si non, exécutez "pip install --upgrade pip".
```
Installez OpenFisca-France-Dotations-Locales :

```sh
pip install openfisca-france-dotations-locales && pip install openfisca-core[web-api]
```
> _Note: Ou `pip install openfisca-france-dotations-locales && pip install openfisca-core[web-api]` pour installer l'API Web d'OpenFisca._

Félicitations :tada: OpenFisca-France-Dotations-Locales est prêt à être utilisé !

#### Prochaines étapes

- Apprenez à utiliser OpenFisca avec nos [tutoriels](https://openfisca.org/doc/) (en anglais).
- Simulez le calcul des dotations avec les [données officielles de la Direction générale des collectivités locales](http://www.dotations-dgcl.interieur.gouv.fr/consultation/criteres_repartition.php).
- Hébergez et servez votre instance d'OpenFisca-France-Dotations-Locales avec l'[API Web OpenFisca](#servez-openfisca-france-avec-lapi-web-openfisca).

En fonction de vos projets, vous pourriez bénéficier de l'installation des paquets suivants dans votre _virtualenv_ :
- pour installer une extension ou écrire une législation au-dessus d'OpenFisca-France-Dotations-Locales, consultez la [documentation sur les extensions](https://openfisca.org/doc/contribute/extensions.html) (en anglais) ;
- pour représenter graphiquement vos résultats, essayez la bibliothèque [matplotlib](http://matplotlib.org/) ;
- pour gérer vos données, découvrez la bibliothèque [pandas](http://pandas.pydata.org/).

### B. Installation avancée (Git Clone)

Suivez cette installation si vous souhaitez :
- enrichir ou modifier la législation d'OpenFisca-France-Dotations-Locales ;
- contribuer au code source d'OpenFisca-France-Dotations-Locales.  

#### Cloner OpenFisca-France-Dotations-Locales avec Git

Premièrement, assurez-vous que [Git](https://www.git-scm.com/) est bien installé sur votre machine.

Dans votre _virtualenv_, assurez-vous que vous êtes dans le répertoire où vous souhaitez cloner OpenFisca-France-Dotations-Locales.  

Vérifiez les pré-requis :

```sh
python --version  # Devrait afficher "Python 3.11.xx".
# Si non, vérifiez que vous passez --python=python3.11 lors de la création de votre environnement virtuel.
```

```sh
pip --version  # Devrait afficher au moins 23.x
# Si non, exécutez "pip install --upgrade pip".
```

Clonez OpenFisca-France-Dotations-Locales sur votre machine :

```sh
git clone git@git.leximpact.dev:leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales.git
cd openfisca-france-dotations-locales
pip install --editable .[dev]
```
> _Note: Ou `pip install --editable .[dev] && pip install openfisca-core[web-api]` pour installer l'API Web d'OpenFisca._

Vous pouvez vous assurer que votre installation s'est bien passée en exécutant :

```sh
pytest tests/test_base.py # Ces test peuvent prendre jusqu'à 60 secondes.
```
:tada: OpenFisca-France-Dotations-Locales est prêt à être utilisé !

#### Prochaines étapes

- Pour enrichir ou faire évoluer la législation d'OpenFisca-France-Dotations-Locales, lisez _[Coding the Legislation](https://openfisca.org/doc/coding-the-legislation/index.html)_ (en anglais).
- Pour contribuer au code, lisez le _[Contribution Guidebook](https://openfisca.org/doc/contribute/index.html)_ (en anglais) ainsi que le [fichier de contribution](./CONTRIBUTING.md) de ce dépôt.

## Tests

Pour faire tourner les tests d'OpenFisca-France-Dotations-Locales, exécutez la commande suivante qui provient du le fichier [Makefile](./Makefile) :

```sh
make test
```

## Style

Ce dépôt adhère à un style de code précis, et on vous invite à le suivre pour que vos contributions soient intégrées au plus vite. L'analyse de style est déjà exécutée avec `make test`. Pour le faire tourner de façon indépendante :

```sh
make check-style
```

Puis, pour corriger les erreurs de style de façon automatique :

```sh
make format-style
```

Pour corriger les erreurs de style de façon automatique à chaque fois que vous faites un _commit_ vous pouvez appliquer cette configuration :

```sh
touch .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

tee -a .git/hooks/pre-commit << END
#!/bin/sh
#
# Automatically format your code before committing.
exec make format-style
END
```

## Servir OpenFisca-France-Dotations-Locales avec l'API Web OpenFisca

Après avoir installé les dépendances additionnelles nécessaires à l'API Web, il est possible de servir OpenFisca-France-Dotations-Locales sur votre propre serveur avec :

```sh
openfisca serve --port 5000
```

Ou utilisez la commande pré-configurée :

```
make serve-local
```

Pour en savoir plus sur la commande `openfisca serve` et ses options, consultez la [documentation de référence](https://openfisca.org/doc/openfisca-python-api/openfisca_serve.html).

Testez votre installation en requêtant la commande suivante :

```sh
curl "http://localhost:5000/spec"
```

Ou tester un calcul sur un exemple déjà fourni avec :

```sh
curl -X POST -H "Content-Type: application/json" \
  -d @./openfisca_france_dotations_locales/situation_examples/communes_dsr.json \
  http://localhost:5000/calculate
```

:tada: Vous servez OpenFisca-France-Dotations-Locales via l'API Web OpenFisca !

Vous pouvez activer le suivi des visites sur votre instance via Matomo avec _[le Tracker API OpenFisca](https://github.com/openfisca/tracker)_ (en anglais).

## Stratégie de versionnement

Le code d'OpenFisca-France-Dotations-Locales  est déployé de manière continue et automatique. Ainsi, à chaque fois que le code de la législation évolue sur la branche principale `master`, une nouvelle version est publiée.

De nouvelles versions sont donc publiées très régulièrement. Cependant, la différence entre deux versions consécutives étant réduite, les efforts d'adaptation pour passer de l'une à l'autre sont en général très limités.

Par ailleurs, OpenFisca-France-Dotations-Locales respecte les règles du [versionnement sémantique](http://semver.org/). Tous les changements qui ne font pas l'objet d'une augmentation du numéro majeur de version sont donc garantis rétro-compatibles.

> Par exemple, si mon application utilise la version `13.1.1`, je sais qu'elle fonctionnera également avec la version `13.2.0`. En revanche, il est possible qu'une adaptation soit nécessaire sur mon client pour pouvoir utiliser la version `14.0.0`.

Enfin, les impacts et périmètres des évolutions sont tous documentés sur le [CHANGELOG](CHANGELOG.md) du package. Ce document permet aux contributeurs de suivre les évolutions et d'établir leur propre stratégie de mise à jour.

## Contributeurs

Voir la [liste des contributeurs](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/openfisca-france-dotations-locales/-/graphs/master?ref_type=heads).

## Références

Ce code a été initialisé grâce aux travaux réalisés dans ces différents dépôts :

* [travaux au hackathon #dataFin](https://github.com/leximpact/dataFin)
* [openfisca-collectivites-territoriales par @guillett](https://github.com/guillett/openfisca-collectivites-territoriales)
* [analyse de la DSR par @magemax](https://github.com/magemax/dsr)
* [template du moteur openfisca](https://github.com/openfisca/country-template)

Il a été ou est réutilisé par : 
* [leximpact-server (LexImpact, Assemblée nationale)](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/leximpact-server) (jusqu'aux dotations 2021 et Projet de loi de finances 2022)
* [dotations-locales-back (Incubateur des territoires, Agence nationale de la cohésion des territoires)](https://gitlab.com/incubateur-territoires/startups/dotations-locales/dotations-locales-back) (jusqu'aux dotations 2023)
* [leximpact-dotations-back (LexImpact, Assemblée nationale)](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/leximpact-dotations-back) (à partir des dotations 2024)

Par ailleurs, ce code peut être testé avec les [données ouvertes officielles](http://www.dotations-dgcl.interieur.gouv.fr/consultation/criteres_repartition.php) de la Direction générale des collectivités locales (DGCL). Ceci est par exemple réalisé dans le dépôt [data-exploration (LexImpact, Assemblée nationale)](https://git.leximpact.dev/leximpact/simulateur-dotations-communes/data-exploration) (succède à [data-exploration, Incubateur des territoires de l'Agence nationale de la cohésion des territoires](https://gitlab.com/incubateur-territoires/startups/dotations-locales/data-exploration)).
