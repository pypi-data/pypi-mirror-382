import numpy as np
import matplotlib.pyplot as plt

from .outils import hsl2rgb, clip

class Graphe:
    def __init__(self, x=1, y=1):
        self.x = x
        self.y = y
        self.graphes = []
        fig, axs = plt.subplots(x, y)
        if x == 1 and y == 1:
            self.graphes = np.array([[axs]])
        elif x == 1:
            self.graphes = np.array([axs])
        elif y == 1:
            for ax in axs:
                self.graphes.append([ax])
        else:
            self.graphes = axs

    def trace(self, f, grapheX=0, grapheY=0, tailleMult=1, taille=(-1, 1, -1, 1), res = 1000, lumZoom=1, homeomR=lambda x: x, marqueFonc=lambda z : False, marqueAlpha=0.5, marqueSurS=False, traceSurD=False):
        taille = np.array(taille)*tailleMult
        x = np.linspace(taille[0], taille[1], res)
        y = np.linspace(taille[2], taille[3], res)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j*Y
        fZ = f(Z)

        R = homeomR(clip(np.abs(fZ)))
        θ = np.angle(fZ)

        H = (θ+np.pi)/(2*np.pi)
        S = np.where(marqueFonc(fZ), np.ones(fZ.shape)*marqueAlpha, np.ones(fZ.shape)) if marqueSurS else np.ones(fZ.shape)
        L = (R - R.min()) / (lumZoom*R.max() - R.min())

        L = np.where(marqueFonc(fZ), np.ones(fZ.shape)*0.5, L) if marqueSurS else np.where(marqueFonc(fZ), 1-L, L)
        L = np.where((np.abs(Z) <= 1), L*(1-L), 0)**0.5 if traceSurD else L

        RGB = hsl2rgb(H, S, L)

        def format_coord(x, y):
            z = x + 1j*y
            return f"x={x:.2f}, y={y:.2f}, |f(x,y)|={np.abs(f(z)):.3g}, θ={np.angle(f(z)):.3g}"
        
        self.graphes[grapheX, grapheY].imshow(RGB, extent=taille, origin="lower")
        self.graphes[grapheX, grapheY].format_coord = format_coord

    def affiche(self):
        plt.show()
        