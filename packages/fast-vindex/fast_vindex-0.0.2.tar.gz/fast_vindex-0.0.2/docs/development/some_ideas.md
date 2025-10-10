# Some ideas

Voici quelques idées pour améliorer les performances de vindex.

**1. Regrouper les tâches `vindex-slice` par chunk dans une tâche unique**

| Avantages                           | Inconvénients                          |
|-------------------------------------|----------------------------------------|
| ✅ diminuer drastiquement le nombre de tâche dans l'arbre des tâches.                       | ❌ Chaque méthode vindex-slice aura une liste d'indexation de taille différentes à mener, comment rendre celà rapide ?                     |


**2. Diminuer la taille de l'arbre des tâches**

Regarder pour remplacer un index array du style array([[1], [2], [3], [4]]), par un slice(1, 5) et un shape (4, 1).

/!\ Pas sur que pour les petits arrays, celà améliore la taille de l'arbre.

NB: Plus la taille de l'arbre est grand, plus l'objet a serialiser entre le client et le scheduler est grand, et donc prend du temps.
