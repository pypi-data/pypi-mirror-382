import numpy as np
import matplotlib.pyplot as plt

from .outils import hsl2rgb, clip, foncFinaleId

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

    def trace(self, f, grapheX=0, grapheY=0, tailleMult=1, taille=(-1, 1, -1, 1), res = 1000, borneSupLum=0, homeomR=lambda x: x, marqueFonc=lambda z : False, marqueAlpha=0.5, marqueSurS=True, lumMarque=False, traceSurD=False, foncFinale=foncFinaleId):
        taille = np.array(taille)*tailleMult
        x = np.linspace(taille[0], taille[1], res)
        y = np.linspace(taille[2], taille[3], res)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j*Y
        fZ = f(Z)

        R = homeomR(clip(np.abs(fZ)))
        θ = np.angle(fZ)

        H = (θ+np.pi)/(2*np.pi)
        S = np.where(marqueFonc(fZ), np.ones(fZ.shape)*(1-marqueAlpha), np.ones(fZ.shape)) if marqueSurS else np.ones(fZ.shape)
        Rmax = R.max() if borneSupLum == 0 else homeomR(borneSupLum)
        L = (R - R.min()) / (Rmax - R.min())

        Lmarque = np.ones(fZ.shape)*0.5 if lumMarque else L
        L = np.where(marqueFonc(fZ), Lmarque, L) if marqueSurS else np.where(marqueFonc(fZ), 1-L, L)

        RGB = hsl2rgb(foncFinale(H, S, L, Z, f))

        def format_coord(x, y):
            z = x + 1j*y
            fz = f(z)
            return f"x={x:.2f}, y={y:.2f}, f(z)={fz:.3g}, |f(x,y)|={np.abs(fz):.3g}, θ={np.angle(fz):.3g}={np.angle(fz)/np.pi:.3g}π"
        
        self.graphes[grapheY, grapheX].imshow(RGB, extent=taille, origin="lower")
        self.graphes[grapheY, grapheX].format_coord = format_coord

    def affiche(self):
        plt.show()
        