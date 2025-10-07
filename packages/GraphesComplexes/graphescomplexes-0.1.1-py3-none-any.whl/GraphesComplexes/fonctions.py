from .Fonction import Fonction
from .outils import eps, nan2num
import numpy as np

# =========================================================
# 🔧 Fonctions de base
# =========================================================

id = Fonction(lambda z: z)
inv = Fonction(lambda z: 1 / z)
sin = Fonction(lambda z: np.sin(z))
cos = Fonction(lambda z: np.cos(z))
exp = Fonction(lambda z: np.exp(z))
Log = Fonction(lambda z: np.log(np.abs(z) + eps) + 1j * np.angle(z))  # éviter log(0)

# Transformations disque/demi-plan de Pointcarré
D2H = Fonction(lambda z: 1j * (1 + z) / (1 - z))
H2D = D2H.composéePuissance(2)

# =========================================================
# 🧪 Fonctions de test
# =========================================================

fonctions_test = [
    Fonction(lambda z: np.sin(-np.pi * z) * np.sin(np.pi / z)),
    Fonction(lambda z: z**4 / (z**2 - 1j * np.pi)),
    Fonction(lambda z: (z - 1j / 2) * (z - 1)**2),
    Fonction(lambda z: (-z**3 + 1j * z + 1) / (z - 1 + 1j)**2),
    Fonction(lambda z: (z + 1)**3 * (z + 1j) / (z - 1 - 1j)**5),
]

# =========================================================
# ⚙️ Générateurs de fonctions
# =========================================================

def z_p(p: int) -> Fonction:
    """Retourne la fonction z ↦ z**p"""
    return Fonction(lambda z: z**p)


def bijD(a: complex, θ: float) -> Fonction:
    """Bijection du disque unité : z ↦ e^{iθ} * (z - a) / (1 - z * conj(a))"""
    return Fonction(lambda z: np.exp(1j * θ) * (z - a) / (1 - z * np.conj(a)))


def bijH(a: complex, b: complex, c: complex, d: complex) -> Fonction:
    """Transformation de Möbius : z ↦ (a*z + b) / (c*z + d)"""
    return Fonction(lambda z: (a * z + b) / (c * z + d))


def serieDirichlet(a, l, N: int) -> Fonction:
    """
    Série de Dirichlet généralisée :
        f(z) = Σ a(n) * exp(-z * l(n))  pour n = 0..N
    """
    def f(z):
        s = 0
        for n in range(N + 1):
            s += a(n) * np.exp(-z * l(n))
        return s
    return Fonction(f)


def serieDirichletn2(N: int) -> Fonction:
    """
    Série de Dirichlet basée sur n² :
        f(z) = Σ z^(n²)  pour n = 0..N
    """
    def f(z):
        s = 0
        for n in range(N + 1):
            s += nan2num(z**(n**2))
        return s
    return Fonction(f)