from .angles import ang2rot, rot2ang
import numpy as np
from scipy.linalg import svd
from scipy.optimize import least_squares
# ===============================================
# === Fonction principale : affinageRT ==========
# ===============================================

def affinageRT(anginit, Tinit, matK, pos3D, pos2D):
    """
    Affine rotation et translation par minimisation de l'erreur de reprojection
    Entrées :
      anginit : angles initiaux (3x1)
      Tinit : translation initiale (3x1)
      matK : matrice intrinsèque 3x3
      pos3D : points 3D (Nx3)
      pos2D : points 2D (Nx2)
    Sortie :
      angfin : angles affinés (3x1)
      Tfin : translation affinée (3x1)
      rmsInit : RMS initial
      rmsFin : RMS final
    """

    # ===============================================
    # === Fonctions de rotation =====================
    # ===============================================

    # def ang2rot(ang):
    #     """Conversion angles (3x1) → matrice de rotation 3x3 (ordre Rx*Ry*Rz typique MATLAB)"""
    #     cx, cy, cz = np.cos(ang)
    #     sx, sy, sz = np.sin(ang)

    #     Rx = np.array([[1, 0, 0],
    #                 [0, cx, -sx],
    #                 [0, sx,  cx]])
    #     Ry = np.array([[ cy, 0, sy],
    #                 [  0, 1,  0],
    #                 [-sy, 0, cy]])
    #     Rz = np.array([[cz, -sz, 0],
    #                 [sz,  cz, 0],
    #                 [ 0,   0, 1]])

    #     # MATLAB fait généralement R = Rz * Ry * Rx
    #     R = Rz @ Ry @ Rx
    #     return R


    # ===============================================
    # === Fonction de projection ====================
    # ===============================================

    def fct_proj_ck(d, X, K):
        """
        Projection 3D → 2D avec paramètres caméra.
        Équivalent MATLAB de fct_proj_ck
        Entrées :
        d : vecteur [T; ang] de taille (6,)
        X : points 3D (3xN)
        K : matrice intrinsèque (3x3)
        Sortie :
        x : projections 2D (2xN)
        """
        alx = K[0, 0]
        aly = K[1, 1]
        x0 = K[0, 2]
        y0 = K[1, 2]

        R = ang2rot(d[3:6])
        T = d[0:3].reshape(3, 1)

        # Projection
        D = R @ (X - T)  # même que R*(X - repmat(T,1,N)) en MATLAB
        x1 = alx * D[0, :] / D[2, :] + x0
        y1 = aly * D[1, :] / D[2, :] + y0

        x = np.vstack((x1, y1))
        return x


    # ===============================================
    # === Fonction d'évaluation =====================
    # ===============================================

    def eval_fct_proj_ck(d, xref, X, K):
        """
        Évalue la fonction de reprojection et retourne les résidus
        Entrées :
        d : [T; ang] (6,)
        xref : 2xN (positions 2D de référence)
        X : 3xN (points 3D)
        K : matrice intrinsèque
        Sortie :
        res : vecteur des résidus (2N,)
        x : projections (2xN)
        """
        x = fct_proj_ck(d, X, K)
        res = x - xref
        res = res.flatten(order='F')  # même ordre colonne que MATLAB
        return res, x

    nbPts = pos3D.shape[0]
    if nbPts != pos2D.shape[0]:
        print("Erreur : dimensions incompatibles entre pos3D et pos2D")
        return None, None, None, None

    # --- Calcul du résidu initial ---
    Rinit = ang2rot(anginit.flatten())
    Mproj3 = Rinit @ pos3D.T - Rinit @ Tinit.reshape(3, 1).repeat(nbPts, axis=1)
    aux = matK @ Mproj3
    mproj3 = aux[:2, :] / aux[2, :]
    mproj3 = mproj3.T

    residu3 = (mproj3.flatten() - pos2D.flatten())
    rmsInit = np.sqrt(np.mean(residu3 ** 2))

    # --- Optimisation non linéaire ---
    dinit = np.concatenate((Tinit.flatten(), anginit.flatten()))

    def fun(d):
        res, _ = eval_fct_proj_ck(d, pos2D.T, pos3D.T, matK)
        return res

    res_lsq = least_squares(fun, dinit, method='lm', verbose=0)
    dfin = res_lsq.x

    # --- Résidu final ---
    resfin, _ = eval_fct_proj_ck(dfin, pos2D.T, pos3D.T, matK)
    rmsFin = np.sqrt(np.mean(resfin ** 2))

    Tfin = dfin[0:3].reshape(3, 1)
    angfin = dfin[3:6].reshape(3, 1)

    # --- Résidu image final (comme MATLAB) ---
    Rfin = ang2rot(angfin.flatten())
    Mproj4 = Rfin @ pos3D.T - Rfin @ Tfin.repeat(nbPts, axis=1)
    aux = matK @ Mproj4
    mproj4 = aux[:2, :] / aux[2, :]
    mproj4 = mproj4.T

    residu4 = (mproj4.flatten() - pos2D.flatten())
    rmsFin = np.sqrt(np.mean(residu4 ** 2))
    return angfin.squeeze(), Tfin.squeeze(), rmsInit, rmsFin


def calculePose3D2D(pts3D, pts2D, matK, nbPts, AFFINAGE=False):    
    """
    Calcule la pose d’une caméra (rotation et translation) à partir de correspondances 3D-2D.

    Utilise la méthode DLT (Direct Linear Transform) avec une résolution par SVD pour estimer
    la matrice de projection, puis extrait la rotation et la translation. Un affinage optionnel
    permet d'améliorer la précision via une minimisation de l'erreur de reprojection.

    Parameters
    ----------
    pts3D : ndarray of shape (nbPts, 3)
        Coordonnées des points 3D dans le repère monde.

    pts2D : ndarray of shape (nbPts, 2)
        Coordonnées des points 2D correspondants dans l'image (en pixels).

    matK : ndarray of shape (3, 3)
        Matrice de calibration intrinsèque de la caméra.

    nbPts : int
        Nombre de points de correspondance 3D-2D utilisés pour le calcul.

    AFFINAGE : bool, optional
        Si True, active un affinage de la pose par minimisation de l'erreur de reprojection.
        Par défaut à False.

    Returns
    -------
    ang : ndarray of shape (3,)
        Angles d'Euler (rx, ry, rz) en radians, représentant la rotation de la caméra.

    T : ndarray of shape (3,)
        Vecteur de translation de la caméra dans le repère monde.

    rms_reproj : float
        Erreur RMS (Root Mean Square) de reprojection entre les points 2D projetés et les
        observations réelles.

    Notes
    -----
    - La rotation est estimée à partir de la matrice de projection, et corrigée
      pour s'assurer qu'elle appartient au groupe SO(3).
    - Le vecteur d'angles `ang` est sélectionné comme la solution avec la norme minimale.
    - Si `AFFINAGE` est activé, une fonction interne est utilisée pour optimiser
      les paramètres `(R, T)` en minimisant l'erreur de reprojection.

    Examples
    --------
    >>> ang, T, rms = calculePose3D2D(pts3D, pts2D, matK, len(pts3D), AFFINAGE=True)
    >>> print("Angles (deg):", np.degrees(ang))
    >>> print("Translation:", T)
    >>> print("RMS reprojection error:", rms)
    """
    ROTPROJ=False
    
    fx = matK[0, 0]
    fy = matK[1, 1]
    x0 = matK[0, 2]
    y0 = matK[1, 2]
    # --- Constitution du système ---
    Kinv = np.linalg.inv(matK)
    posN = Kinv @ np.vstack((pts2D.T, np.ones((1, nbPts))))
    posN = posN.T
    M1 = np.hstack([
        -pts3D, -np.ones((nbPts, 1)),
        np.zeros((nbPts, 4)),
        (posN[:, [0]] * pts3D), posN[:, [0]]
    ])

    M2 = np.hstack([
        np.zeros((nbPts, 4)),
        -pts3D, -np.ones((nbPts, 1)),
        (posN[:, [1]] * pts3D), posN[:, [1]]
    ])

    M = np.vstack([M1, M2])

    # --- Résolution SVD ---
    U, S, Vt = svd(M)
    pest = Vt[-1, :]  # dernière ligne
    pest = pest / np.linalg.norm(pest[8:11])
    Pest = pest.reshape(4,3, order='F').T  # comme reshape(...,4,3)' en MATLAB

    if np.linalg.det(Pest[:, :3]) < 0:
        Pest = -Pest

    # --- R/T et angles ---
    if ROTPROJ:
        Ur, Sr, Vr = svd(Pest[:, :3])
        Rest = Ur @ Vr
    else:
        Rest = Pest[:3, :3]


    angcandidat = rot2ang(Rest)
    # Sélection du plus proche angle (ici, le plus faible)
    imin = np.argmin(np.sum(angcandidat**2, axis=0))
    ang = angcandidat[:, imin]
    T = -Rest.T @ Pest[:, 3]
    # --- Affinage optionnel ---
    if AFFINAGE:
        angfin, Tfin, rmsInit, rmsFin = affinageRT(ang, T, matK, pts3D, pts2D)
        mvtfin = np.concatenate((angfin.flatten(), Tfin.flatten()))
        ang = angfin
        T = Tfin
    else:
        rmsInit = 0
        rmsFin = 0

    # --- Erreur de reprojection ---
    
    Xw = pts3D.T
    R = ang2rot(ang.flatten())
    # Xc = R @ (Xw - T.reshape(3, 1))
    # xn = Xc[:2, :] / Xc[2, :]
    # x = np.vstack([fx * xn[0, :] + x0, fy * xn[1, :] + y0]).T
    # res = (x - pts2D).flatten()
    # rms_reproj = np.sqrt(np.mean(res**2))
    # Transformation 3D → caméra
    Xc = R @ (Xw - np.tile(T.reshape(3, 1), (1, nbPts)))  # (3 x nbPts)

    # Normalisation en coordonnées homogènes
    xn = Xc[0:2, :] / np.tile(Xc[2, :], (2, 1))  # (2 x nbPts)

    # Projection avec les paramètres intrinsèques
    x = np.vstack((fx * xn[0, :] + x0, fy * xn[1, :] + y0))  # (2 x nbPts)
    x = x.T  # (nbPts x 2)

    # Calcul du résidu et RMS
    res = x.reshape(-1) - pts2D.reshape(-1)
    rms_reproj = np.sqrt(np.mean(res**2))
    # --- Affichage résultats ---
    print(f"ang = [{ang[0]*180/np.pi:.2f}, {ang[1]*180/np.pi:.2f}, {ang[2]*180/np.pi:.2f}] deg")
    print(f"T = [{T[0]:.4f}, {T[1]:.4f}, {T[2]:.4f}]")
    if AFFINAGE:
        print(f"nbPts={nbPts} --- RMS : avant={rmsInit:.4f}, après={rms_reproj:.4f}")
    else:
        print(f"nbPts={nbPts} --- RMS={rms_reproj:.4f}")
    return ang, T, rms_reproj
