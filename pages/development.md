## 🤝 Dev/Contribution

> Le repo se base sur le fichier `src/export-obtainium.json` comme source de vérité, il s'agit de mon export puis le fichier `src/applications.yaml` via appliquer des ajouts/modifications si nécessaires.
> La compilation se fait via ([mise](https://github.com/jdx/mise)/[uv](https://github.com/astral-sh/uv)): `mise exec uv -- uv run make_table.py` ou `mise r generate`

Vous pouvez fork ou pull-request, pour ajouter une application :

1. Éditez le fichier `src/applications.yml`
2. Ajoutez votre configuration suivant par exemple le format :
```yaml
apps:
  - id: "package.name"
    url: "https://source.url"
    name: "App Name"
    categories: ["Catégorie"]
    meta:
      about: "Description"
```
3. Créez une Pull Request

## 📜 License  
MIT License  
