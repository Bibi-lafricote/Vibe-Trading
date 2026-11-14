# btc-lab : Vibe-Trading comme base

## Architecture

Vibe-Trading reste l'application de base. Le lanceur choisit son fournisseur natif DeepSeek et le modele deepseek-flash ; il ne remplace pas le moteur ni le registre d'outils. La skill deepseek-api est un complement distinct. Aucun registre limite a deux outils n'est installe.

## Installation locale depuis ce fork

Prerequis : Python 3.11 ou plus et environnement virtuel dedie. Depuis la racine du depot, sur la branche btc-lab/deepseek-readonly :

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -e '.[deepseek]'
    python -m pip install -r agent/src/skills/anonymize-before-remote-llm/requirements.txt
    python btc-lab/start.py --check

Ces commandes ne sont pas executees par l'ajout de cette notice. Elles telechargent et installent des dependances lorsqu'elles sont lancees localement. Ne pas utiliser une installation PyPI seule a la place du fork personnalise.

## Cle et demarrage

La cle est lue depuis DEEPSEEK_API_KEY ou ~/.openclaw/deepseek.key, jamais fournie en argument. Le fichier de cle doit etre prive, non symbolique et inaccessible au groupe/autres. Ne jamais coller la cle dans un terminal avec une commande qui la conserve dans l'historique, ni dans GitHub ou la conversation. Le controle --check ne lit pas la cle et ne contacte pas DeepSeek.

    python btc-lab/start.py --start

Le demarrage importe la commande native et peut lancer ses procedures normales, dont l'assistant de configuration et des appels payants selon l'utilisation. Les sous-commandes natives peuvent etre transmises apres --start -- ; leurs effets doivent etre verifies avant utilisation. Ne pas modifier le fournisseur dans l'assistant si l'objectif est de rester sur DeepSeek.

## Limites et securite

Ce lanceur est preparatoire : lancement reel et appels de modele non encore verifies. Il ne force pas le modele d'eventuels agents secondaires disposant d'une configuration propre. Il ne cree pas de workspace isole. Ne pas reutiliser sans examen un environnement contenant deja des identifiants de courtier ou une configuration de trading.

Le registre natif et ses fonctions restent disponibles selon la configuration de Vibe-Trading. Aucune garantie de blocage global des ordres n'est ajoutee par ce lanceur. Ne connecter aucun compte autorise a trader pendant la mise au point. Aucun ordre n'est autorise par l'ajout de ces fichiers.

Le masquage des scripts ne couvre pas automatiquement les messages de l'interface native ni tous les resultats d'outils. Ne pas saisir de donnees privees avant l'integration d'un controle d'envoi global. Les deux skills sont presentes, mais leurs scripts ne sont pas encore raccordes comme outils executables natifs ; la lecture d'une fiche SKILL.md n'y suffit pas.
