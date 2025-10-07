class Fonction:
    """
    Classe principale pour gérer des fonctions mathématiques complezes.
    """

    def __init__(self, expression):
        """
        Initialise la fonction à partir d'une expression lambda ou fonction Python.
        Par ezemple : f = Fonction(lambda z: z**2 + np.sin(z))
        """
        if not callable(expression):
            raise ValueError("L'expression doit être une fonction callable")
        self.expression = expression

    def eval(self, z):
        """
        Évalue la fonction en un point ou sur un tableau.
        z peut être un float ou un np.array
        """
        return self.expression(z)

    def __call__(self, z):
        """
        Permet d'appeler l'objet comme une fonction
        """
        return self.eval(z)
    
    # --- Opérateurs mathématiques ---
    def __add__(self, other):
        if isinstance(other, Fonction):
            return Fonction(lambda z: self(z) + other(z))
        else:  # supporte aussi les nombres
            return Fonction(lambda z: self(z) + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Fonction):
            return Fonction(lambda z: self(z) - other(z))
        else:
            return Fonction(lambda z: self(z) - other)

    def __rsub__(self, other):
        if isinstance(other, Fonction):
            return Fonction(lambda z: other(z) - self(z))
        else:
            return Fonction(lambda z: other - self(z))

    def __mul__(self, other):
        if isinstance(other, Fonction):
            return Fonction(lambda z: self(z) * other(z))
        else:
            return Fonction(lambda z: self(z) * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Fonction):
            return Fonction(lambda x: self(x) / other(x))
        else:
            return Fonction(lambda x: self(x) / other)

    def __rtruediv__(self, other):
        if isinstance(other, Fonction):
            return Fonction(lambda x: other(x) / self(x))
        else:
            return Fonction(lambda x: other / self(x))

    def __pow__(self, power):
        if isinstance(power, Fonction):
            return Fonction(lambda x: self(x) ** power(x))
        else:
            return Fonction(lambda x: self(x) ** power)

    def __rpow__(self, other):
        if isinstance(other, Fonction):
            return Fonction(lambda x: other(x) ** self(x))
        else:
            return Fonction(lambda x: other ** self(x))
    
    # --- Composition de fonctions ---
    def __matmul__(self, other):
        """
        Retourne la composition self(other(x)), équivalent à f(g(x))
        """
        if not isinstance(other, Fonction):
            raise ValueError("L'argument doit être une instance de Fonction")
        return Fonction(lambda x: self(other(x)))
    
    def composéePuissance(self, n):
        if n <= 1:
            return self
        else:
            return self.composéePuissance(n-1) @ self