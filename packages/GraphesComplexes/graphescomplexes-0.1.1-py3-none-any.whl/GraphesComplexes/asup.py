# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.widgets import Slider
# from cmath import *



# a = -0.6 + 0.21j
# θ = 1
# a = a*np.exp(1j*(1-θ))

# def borne10(x):
#     return np.clip(np.log(x), None, 3)

# fig, axs = plt.subplots(1, 1)
# axs = np.array([[axs]])

# def draw(f, plotX, plotY, sizeMult = 1, size = (-1, 1, -1, 1), res = 1000, lumZoom=1, fscale=None, markFunc=lambda Z : False, markAlpha=0.5, invS=False):
#     size = np.array(size)
#     x = np.linspace(size[0]*sizeMult, size[1]*sizeMult, res)
#     y = np.linspace(size[2]*sizeMult, size[3]*sizeMult, res)
#     X, Y = np.meshgrid(x, y)
#     Z = X + Y*1j
#     fZ = f(Z)
#     # Module et angle
#     eps = 1e-12
#     R = (np.clip(np.abs(fZ), eps, 1/eps))  # empêche 0 et inf
#     H = (np.angle(fZ) + np.pi) / (2*np.pi) # teinte
#     S = np.where(markIsomod(fZ), np.ones(fZ.shape)*markAlpha, np.ones(fZ.shape))
#     # S = np.ones(fZ.shape)
#     if invS:
#         S = 1-S                  

#     if(fscale != None):
#         R = fscale(R)
#     L = (R - R.min()) / (lumZoom*R.max() - R.min())  # luminosité normalisée
#     #L = 
#     L = np.where(markFunc(fZ), 1-L, L)
#     #L = np.where(np.abs(X + 1j*Y) < 1, L, 0)

#     RGB = hsl_to_rgb(H, S, L)

#     def format_coord(x, y):
#         # valeur f(x,y)
#         z = x + 1j*y
#         return f"x={x:.2f}, y={y:.2f}, |f(x,y)|={np.abs(f(z)):.3g}, θ={np.angle(f(z)):.3g}"

#     axs[plotY, plotX].imshow(RGB, extent=size*sizeMult, origin="lower")
#     axs[plotY, plotX].format_coord = format_coord
#     # plt.contour(X, Y, R, levels=np.linspace(np.min(R), np.max(R), 20), colors='white', linewidths=0.5)

# def drawOnD(a, θ, plotX, plotY, res=1000, markFunc=lambda R : False, markAlpha=0.05, invS=False):
#     size = 1.1
#     x = np.linspace(-size, size, res)
#     y = np.linspace(-size, size, res)
#     X, Y = np.meshgrid(x, y)

#     Z = X + 1j*Y
#     def f(z):
#         return np.exp(1j*θ)*(z-a)/(1-z*np.conj(a))

#     fZ = f(Z)
#     # Module et angle
#     eps = 1e-12
#     R = (np.clip(np.abs(Z), eps, 1/eps))  # empêche 0 et inf
#     H = (np.angle(Z) + np.pi) / (2*np.pi) # teinte
#     S = np.where(markFunc(R), np.ones(Z.shape)*markAlpha, np.ones(Z.shape))
#     if invS:
#         S = 1-S
#     L = np.where((R >= 0) & (R <= 1), R*(1-R), 0.0)**0.5


#     RGB = hsl_to_rgb(H, S, L)

#     def format_coord(x, y):
#         # valeur f(x,y)
#         r = np.abs(f(x, y))
#         θ = np.angle(f(x, y))
#         return f"x={x:.2f}, y={y:.2f}, |f(x,y)|={r:.3g}, θ={θ:.3g}"

#     axs[plotY, plotX].imshow(RGB, extent=[-size,size,-size,size], origin="lower")
#     axs[plotY, plotX].format_coord = format_coord

# # draw(id, 0, 0, lumZoom=10, fscale=log, markFunc=markIsomod2(id))
# # draw(exp, 0, 1, sizeMult=4, fscale=log)
# # draw(composée(exp, D2H), 1, 1, sizeMult=4, fscale=log)
# draw(D2H, 0, 0, sizeMult=2, fscale=log, markFunc=markIsomod2)

# # plt.tight_layout()

# # # Slider
# # ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
# # slider = Slider(ax_slider, "θ", 0, 2*np.pi, valinit=1.0, valstep=0.1)

# # Callback
# # def update(val):
# #     θ = slider.val
# #     img.set_data(calcul(θ))
# #     fig.canvas.draw_idle()

# # slider.on_changed(update)

# plt.show()