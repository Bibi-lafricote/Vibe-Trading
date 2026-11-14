---
name: anonymize-before-remote-llm
description: Masquer localement certaines donnees personnelles avant un envoi distant, conserver la source et controler les faux positifs.
category: tool
---

# Masquage avant envoi distant

## Etat

Integration en cours. Cette fiche est une documentation, pas une autorisation d'execution. Aucun envoi distant n'est effectue par les scripts de cette skill. Les tests fonctionnels avec phonenumbers et ceux de l'anonymiseur complet restent a executer. Ne pas considerer le filtre comme valide avant ces tests.

## Utilisation locale

Depuis le dossier de cette skill :

    python3 scripts/anonymiser.py document.txt --region FR
    python3 -m unittest discover -s tests -p 'test_*.py'

Installer les dependances de requirements.txt dans un environnement isole avant utilisation. Le module anonymiser.py expose anonymiser(texte, region=None) depuis son dossier scripts ; il retourne le texte masque et le nombre de remplacements. Le pays de reference est configurable et ne doit pas etre deduit silencieusement.

## Conservation

Le script cree document.anonymise.txt et laisse l'original intact. Une copie existante n'est pas ecrasee. Ne transmettre que le texte controle de la copie, jamais automatiquement l'original. Ne pas publier ces fichiers personnels dans GitHub.

## Categories

EMAIL, CLE_API, URL_JETON, MOT_DE_PASSE, NAISSANCE, SECU, PLAQUE, IBAN, IP, CHEMIN, ADRESSE, TEL et CARTE. Les cartes ne sont retenues que pour 13 a 16 chiffres avec controle Luhn ; cela ne prouve pas leur nature. Les telephones utilisent phonenumbers et ses regles internationales ; sans region, les numeros nationaux ne sont pas couverts de maniere fiable. Les autres motifs sont heuristiques et notamment les adresses restent limitees aux formes francaises prevues.

## Controle obligatoire

Inspecter les categories et le contexte local des remplacements, particulierement TEL et CARTE dans les textes financiers. Conserver les prix, dates, entreprises, tickers et noms publics. Ne pas afficher les extraits sensibles dans un journal distant. Un compte de remplacements correct ne prouve pas que le texte est depourvu de donnees privees. Des noms prives, secrets inconnus et formats non reconnus peuvent rester visibles. Ne pas envoyer en cas de doute.

## Limites

Aucune anonymisation exhaustive, aucune analyse des images ou des PDF bruts, aucune identification fiable entre personne publique et personne privee. La dependance manquante doit bloquer le traitement, sans repli silencieux. Le filtre ne remplace ni la limitation des donnees envoyees ni la validation humaine. L'obligation de passer par ce filtre dans la skill DeepSeek reste a implementer.
