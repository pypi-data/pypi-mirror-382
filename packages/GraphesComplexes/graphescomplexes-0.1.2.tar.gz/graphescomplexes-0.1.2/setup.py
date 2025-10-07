from setuptools import setup, find_packages

setup(
    name="GraphesComplexes",
    version="0.1.2",
    packages=find_packages(),
    install_requires=["numpy", "matplotlib"],  # liste les dépendances si nécessaire
    author="Emmanuel Lafont",
    description="Une bibliothèque simple pour visualiser les fonctions complexes",
    #url="https://github.com/toncompte/ma_biblio",  # optionnel
)
