import numpy as np
from matplotlib.colors import hsv_to_rgb

# =========================================================
# 🔧 Constantes et utilitaires
# =========================================================
eps = 1e-12

def nan2num(z):
    """
    Remplace NaN et inf dans un tableau complexe par des valeurs finies.
    """
    return (
        np.nan_to_num(z.real, nan=0, posinf=1e12, neginf=-1e12) +
        1j * np.nan_to_num(z.imag, nan=0, posinf=1e12, neginf=-1e12)
    )

def clip(x):
    """Clippe x entre eps et 1/eps pour éviter les valeurs extrêmes"""
    return np.clip(x, eps, 1/eps)

def ln(x):
    """Logarithme naturel avec décalage pour éviter log(0)"""
    return np.log(x + 1e-12)

def hm_ln(x):
    """Homeomorphisme basé sur le log pour normaliser l'échelle"""
    x = ln(x)
    return x / (1 + np.abs(x))

def hm_sqrt(x):
    """Homeomorphisme basé sur la racine carrée"""
    x = np.sqrt(x) - 1 / np.sqrt(x)
    return x / (1 + np.abs(x))


# =========================================================
# 🧩 Homeomorphismes R
# =========================================================
homeomorphismes_R = [
    ln,
    hm_ln,
    hm_sqrt
]


# =========================================================
# 🟢 Marqueurs / masques sur les nombres complexes
# =========================================================

def marqueIsomod(z):
    """
    Masque booléen pour les isomodes classiques : |z| = 1/i ou |z| = i pour i = 1..20
    """
    r = np.abs(z)
    result = np.zeros_like(z, dtype=bool)
    for i in range(1, 21):
        result |= np.isclose(r, 1/i, 1e-2)
        result |= np.isclose(r, i, 1e-2)
    return result

def marqueIsomodLog(z):
    """
    Masque booléen pour les isomodes sur une échelle logarithmique :
    |z| proche de sqrt(2) * 2**i pour i de -20 à 19.5 par pas de 0.5
    """
    r = np.abs(z)
    result = np.zeros_like(z, dtype=bool)
    for i in np.arange(-20, 20, 0.5):
        result |= np.isclose(r, np.sqrt(2) * 2**i, 1e-2)
    return result

def marqueD(z):
    """Masque pour le disque unité : |z| < 1"""
    return np.abs(z) < 1

def marqueH(z):
    """Masque pour la demi-plan supérieur : Im(z) > 0"""
    return np.imag(z) > 0

def marqueA(z):
    """Masque pour la moitié gauche : Re(z) < 0"""
    return np.real(z) < 0


fonctions_marques = [
    marqueIsomod,
    marqueIsomodLog,
    marqueH,
    marqueD,
    marqueA
]


# =========================================================
# 🎨 Conversion HSL → RGB
# =========================================================
def hsl2rgb(HSL):
    """
    Conversion HSL → RGB
    (H, S, L) ∈ [0,1]^3 (arrays ou scalaires)
    Retourne RGB ∈ [0,1] (même shape + dernière dimension=3)
    """
    H, S, L = HSL
    V = L + S * np.minimum(L, 1 - L)
    Sv = np.zeros_like(S)
    mask = V > 0
    Sv[mask] = 2 * (1 - L[mask] / V[mask])
    
    HSV = np.stack([H, Sv, V], axis=-1)
    return hsv_to_rgb(HSV)

# =========================================================
# Fonction finale identité
# =========================================================
def foncFinaleId(H, S, L, Z, f):
    return H, S, L

def permuteHL(H, S, L, Z, f):
    return L, S, H

def traceSurD(H, S, L, Z, f):
    L = np.where((np.abs(Z) <= 1), L*(1-L), 0)**0.5
    return H, S, L