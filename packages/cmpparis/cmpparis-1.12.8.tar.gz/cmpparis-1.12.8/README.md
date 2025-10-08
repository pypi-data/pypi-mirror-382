# cmpparis

`cmpparis` est une bibliothèque Python interne pour CMP Paris qui centralise les fonctions communes afin d'éviter la duplication de code et d'accélérer le développement.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/pypi/v/cmpparis.svg)](https://pypi.org/project/cmpparis/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com)

## 📚 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Structure du Projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Documentation](#documentation)
- [Comment Contribuer](#comment-contribuer)
- [Gestion des Versions](#gestion-des-versions)
- [Déploiement](#déploiement)
- [FAQ](#faq)
- [Licence](#licence)

## ✨ Fonctionnalités

### BOD Parser

- 🔄 Parsing XML BOD (Infor M3) vers CSV
- ⚙️ Configurations externalisées (YAML/JSON)
- 🔧 40+ transformers prêts à l'emploi
- ☁️ Chargement depuis S3

### AWS Integration

- 📦 **S3** : Upload, download, gestion de fichiers
- 📧 **SES** : Envoi d'emails
- 🔐 **Secrets Manager** : Gestion des secrets
- ⚙️ **Parameter Store** : Gestion des paramètres

### Autres modules

- 🌐 **FTP/SFTP** : Transfert de fichiers
- 🗄️ **DocumentDB** : Client MongoDB
- 📁 **File Utils** : Utilitaires de manipulation de fichiers
- 🔌 **Quable API** : Client API Quable
- 🛠️ **Utils** : Fonctions utilitaires diverses

## 📂 Structure du Projet

```
cmpparis/
├── cmpparis/                    # Code source de la bibliothèque
│   ├── __init__.py
│   ├── bod_parser.py           # Parser BOD XML → CSV
│   ├── bod_config.py           # Configuration BOD
│   ├── bod_config_loader.py    # Chargeur de configs
│   ├── bod_transformers.py     # Transformers
│   ├── s3.py                   # Client S3
│   ├── ftp.py                  # Client FTP/SFTP
│   ├── ses_utils.py            # Utilitaires SES
│   ├── sm_utils.py             # Secrets Manager
│   ├── parameters_utils.py     # Parameter Store
│   └── ...
├── tests/                       # Tests unitaires
├── docs/                        # Documentation MkDocs
│   ├── index.md
│   ├── getting-started/
│   ├── modules/
│   ├── api/
│   └── guides/
├── configs/                     # Configurations BOD exemples
├── .gitignore
├── LICENSE
├── README.md                    # Ce fichier
├── README_PYPI.md              # Documentation PyPI
├── CHANGELOG.md                # Historique des versions
├── setup.py                    # Configuration packaging
├── mkdocs.yml                  # Configuration documentation
└── deploy_docs.sh              # Script de déploiement doc
```

## 🔧 Prérequis

- **Python** 3.7 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **Accès AWS** configuré (pour certains modules)
- `virtualenv` (optionnel mais recommandé)

## 📥 Installation

### Installation depuis PyPI (Production)

```bash
pip install cmpparis
```

### Installation en mode développement

1. **Clonez le dépôt** :

   ```bash
   git clone https://codecatalyst.aws/spaces/CMP/projects/Coding-Tools/source-repositories/python-cmpparis-lib
   cd python-cmpparis-lib
   ```

2. **Créez un environnement virtuel** :

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

3. **Installez en mode éditable** :

   ```bash
   pip install -e .
   ```

4. **Installez les dépendances de développement** :
   ```bash
   pip install -e ".[dev]"
   ```

## 🚀 Utilisation

### Exemple 1 : Parser un BOD XML

```python
from cmpparis import BODParser, BODConfigLoader

# Charger la configuration
config = BODConfigLoader.from_yaml("configs/purchase_order.yaml")

# Parser le XML
parser = BODParser()
csv_output = parser.parse_and_convert(xml_content, config)

# Sauvegarder
with open("output.csv", "w") as f:
    f.write(csv_output)
```

### Exemple 2 : Upload vers S3

```python
from cmpparis import S3

s3 = S3()
s3.upload_file("local_file.csv", "my-bucket", "remote/path/file.csv")
```

### Exemple 3 : Envoyer un email

```python
from cmpparis import send_email

send_email(
    to="user@example.com",
    subject="Notification",
    body="Message content"
)
```

### Exemple 4 : Récupérer un secret

```python
from cmpparis import get_secret

db_password = get_secret("production/database/password")
```

## 📖 Documentation

La documentation complète est disponible en ligne et auto-générée depuis le code source.

### 🌐 Accéder à la documentation

**URL :** [http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com](http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com)

### 📚 Contenu de la documentation

- **Guide de démarrage** : Installation, configuration, premiers pas
- **Modules** : Documentation détaillée de chaque module
- **API Reference** : Référence complète auto-générée
- **Guides pratiques** : Tutoriels et cas d'usage

### 🛠️ Générer la documentation localement

1. **Installer les dépendances** :

   ```bash
   pip install mkdocs mkdocs-material mkdocstrings-python
   ```

2. **Servir la documentation en local** :

   ```bash
   mkdocs serve
   ```

   Puis ouvrez http://127.0.0.1:8000

3. **Build la documentation** :

   ```bash
   mkdocs build
   ```

   Les fichiers HTML statiques seront dans le dossier `site/`

### 🚀 Déployer la documentation sur S3

La documentation est hébergée sur AWS S3 et accessible via une URL publique.

#### Déploiement manuel

```bash
# 1. Build la documentation
mkdocs build

# 2. Upload vers S3
aws s3 sync site/ s3://cmp-docs-internal --delete

# 3. Vérifier le déploiement
echo "Documentation disponible sur :"
echo "http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com"
```

#### Déploiement automatique (recommandé)

Utilisez le script fourni :

```bash
# Rendre le script exécutable (première fois seulement)
chmod +x deploy_docs.sh

# Déployer
./deploy_docs.sh
```

**Contenu de `deploy_docs.sh`** :

```bash
#!/bin/bash
echo "🏗️  Building documentation..."
mkdocs build

echo "📤 Uploading to S3..."
aws s3 sync site/ s3://cmp-docs-internal --delete

echo "✅ Documentation déployée !"
echo ""
echo "🌐 URL: http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com"
```

#### Configuration S3 (déjà fait, pour référence)

Si vous devez recréer le bucket :

```bash
# Créer le bucket
aws s3 mb s3://cmp-docs-internal

# Configurer en tant que site web
aws s3 website s3://cmp-docs-internal --index-document index.html

# Désactiver le blocage public
aws s3api put-public-access-block \
  --bucket cmp-docs-internal \
  --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Ajouter une policy publique
aws s3api put-bucket-policy --bucket cmp-docs-internal --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::cmp-docs-internal/*"
  }]
}'
```

### 📝 Ajouter de la documentation

Pour documenter votre code, utilisez des docstrings **Google-style** :

````python
def ma_fonction(param1: str, param2: int = 10) -> bool:
    """
    Description courte de la fonction.

    Description longue avec plus de détails.

    Args:
        param1: Description du paramètre 1
        param2: Description du paramètre 2 (défaut: 10)

    Returns:
        Description de la valeur retournée

    Raises:
        ValueError: Quand param1 est vide

    Examples:
        ```python
        result = ma_fonction("test", 5)
        print(result)  # True
        ```
    """
    # votre code
````

La documentation sera automatiquement générée depuis ces docstrings !

## 🤝 Comment Contribuer

### Workflow de contribution

1. **Créez une branche pour votre modification** :

   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   # ou
   git checkout -b fix/nom-du-bug
   ```

2. **Faites vos modifications**

   - Ajoutez votre code
   - Ajoutez des docstrings sur chaque fonctions/class
   - Ajoutez des tests si nécessaire

3. **Assurez-vous que tous les tests passent** :

   ```bash
   pytest
   ```

4. **Vérifiez la documentation** :

   ```bash
   mkdocs serve
   ```

5. **Ajoutez vos changements et commitez** :

   ```bash
   git add .
   git commit -m "feat: Description de la modification"
   ```

   Utilisez les [Conventional Commits](https://www.conventionalcommits.org/) :

   - `feat:` : Nouvelle fonctionnalité
   - `fix:` : Correction de bug
   - `docs:` : Documentation
   - `refactor:` : Refactoring
   - `test:` : Tests

6. **Poussez vos modifications** :

   ```bash
   git push origin feature/nom-de-la-fonctionnalite
   ```

7. **Ouvrez une Pull Request sur CodeCatalyst**

### Checklist avant PR

- [ ] Tests passent (`pytest`)
- [ ] Code documenté (docstrings)
- [ ] Documentation mise à jour si nécessaire
- [ ] CHANGELOG.md mis à jour
- [ ] Version incrémentée dans `setup.py` si nécessaire

## 📦 Gestion des Versions

Nous suivons le [versionnement sémantique](https://semver.org/lang/fr/) : `MAJOR.MINOR.PATCH`

- **MAJOR** : Changements incompatibles de l'API
- **MINOR** : Ajout de fonctionnalités compatibles
- **PATCH** : Corrections de bugs

### Mise à jour de la version

Dans `setup.py`, modifiez la ligne :

```python
version="1.12.7",  # Incrémenter selon le type de changement
```

Et dans `CHANGELOG.md` :

```markdown
## [1.12.8] - 2025-10-08

### Ajouté

- Nouvelle fonctionnalité X

### Corrigé

- Bug Y
```

## 🚀 Déploiement

### Déploiement sur PyPI

#### 1. Tester localement

```bash
# Installer en mode éditable
pip install -e .

# Lancer les tests
pytest
```

#### 2. Construire le package

```bash
# Installer les outils nécessaires
pip install wheel twine

# Construire
python setup.py sdist bdist_wheel
```

Cela génère un répertoire `dist/` contenant :

- `cmpparis-X.X.X.tar.gz` (source)
- `cmpparis-X.X.X-py3-none-any.whl` (wheel)

#### 3. Tester sur Test PyPI (optionnel mais recommandé)

```bash
# Upload sur Test PyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Installer depuis Test PyPI pour tester
pip install --index-url https://test.pypi.org/simple/ cmpparis
```

#### 4. Déployer sur PyPI (Production)

```bash
# Upload sur PyPI
twine upload dist/*

# Vérifier l'installation
pip install cmpparis --upgrade
```

### Déploiement de la documentation

Après chaque release :

```bash
./deploy_docs.sh
```

## ❓ FAQ

### Comment mettre à jour la bibliothèque ?

```bash
pip install cmpparis --upgrade
```

### Comment voir la version installée ?

```bash
pip show cmpparis
```

Ou dans Python :

```python
import cmpparis
print(cmpparis.__version__)
```

### Où trouver des exemples d'utilisation ?

- Documentation en ligne : [http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com](http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com)
- Dossier `tests/` pour des exemples de tests

### Comment signaler un bug ?

Ouvrez une issue sur CodeCatalyst avec :

- Description du bug
- Code pour reproduire
- Comportement attendu vs observé
- Version de cmpparis (`pip show cmpparis`)

### La documentation n'est pas à jour ?

1. Vérifiez que vous avez la dernière version : `pip install cmpparis --upgrade`
2. La documentation est déployée automatiquement, vérifiez la date de dernière mise à jour
3. Si le problème persiste, signalez-le via une issue

## 🔗 Liens utiles

- **Documentation** : [http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com](http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com)
- **PyPI** : [https://pypi.org/project/cmpparis/](https://pypi.org/project/cmpparis/)
- **CodeCatalyst** : [Repository interne](https://codecatalyst.aws/spaces/CMP/projects/Coding-Tools/source-repositories/python-cmpparis-lib)

---

## 📄 Licence

Usage interne CMP Paris uniquement.

Copyright © 2025 CMP Paris - Tous droits réservés.

**Maintenu par** : Sofiane Charrad | Hakim Lahiani

**Contact** : s.charrad@cmp-paris.com | h.lahiani@cmp-paris.com
