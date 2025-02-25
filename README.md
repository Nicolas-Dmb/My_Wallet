# My_Wallet

[![codecov](https://codecov.io/github/Nicolas-Dmb/My_Wallet/graph/badge.svg?token=CW1Z2CKRZS)](https://codecov.io/github/Nicolas-Dmb/My_Wallet)


## Comment lancer l'API 
### Télécharger le code et ses dependances
```bash
git clone git@github.com:Nicolas-Dmb/My_Wallet.git
cd cd My_Wallet
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```
### implémenter le fichier .env 
Le fichier .env_exemple regroupe l'ensemble des données à intégrer dans le fichier .env, il vous faudra : 
- une clé API de chatGPT 
- générer clé pour FIXER_KEY et SECRET_KEY
- configurer une Adresse SMTP, remplacer les informations nécessaires dans settings.py puis ajouter le mot de passe dans le fichier .env 
- configurer une base de données SQL comme postgres 
