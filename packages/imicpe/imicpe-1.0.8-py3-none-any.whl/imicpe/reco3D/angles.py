import numpy as np

def ang2rot(ang):
    """
    
    Calcule la matrice de rotation 3x3 à partir de 3 angles (Euler Z–X–Y)
    (ONERA/DTIM)
    
    Parameters
    ----------
    ang : array_like of shape (3,)
        Angles des rotations autour des axes z, x, y (en radians)
    
    Returns
    -------
    R : ndarray of shape (3,3)
        Matrice de rotation correspondante
    """

    ang = np.array(ang, dtype=float).flatten()
    if ang.size != 3:
        raise ValueError("ang doit être un vecteur de 3 éléments (z, x, y)")

    cz, sz = np.cos(ang[0]), np.sin(ang[0])
    cx, sx = np.cos(ang[1]), np.sin(ang[1])
    cy, sy = np.cos(ang[2]), np.sin(ang[2])

    # === Codage Euler z-x-y ===
    Rz = np.array([
        [cz,  sz,  0],
        [-sz, cz,  0],
        [0,   0,   1]
    ])

    Rx = np.array([
        [1,  0,   0],
        [0,  cx,  sx],
        [0, -sx,  cx]
    ])

    Ry = np.array([
        [cy,  0, -sy],
        [0,   1,  0],
        [sy,  0,  cy]
    ])

    R = Rz @ Rx @ Ry
    return R

def rot2ang(matR):
    """
    Conversion d'une matrice de rotation 3x3 en angles d'Euler (z, x, y)
    Codage : Euler Z–X–Y
    Retourne : ang (3x2) — deux solutions possibles
    (ONERA/DTIM)
    
    Parameters
    ----------
    R : ndarray (3,3)
        Matrice de rotation correspondante

    Returns
    -------
    ang : array_like (3,2)
        Angles des rotations autour des axes z, x, y (en radians)
    """

    # Sécurité : s'assurer que matR est un array numpy 3x3
    matR = np.array(matR, dtype=float).reshape(3, 3)

    # Cas général
    if abs(matR[2, 1]) != 1:
        ang = np.zeros((3, 2))  # (3x2) comme MATLAB après transposition finale

        # rotation angle around x axis
        ang[1, 0] = np.arcsin(-matR[2, 1])
        ang[1, 1] = np.sign(ang[1, 0]) * np.pi - ang[1, 0]

        # rotation angle around y axis (colonne 3 MATLAB → ligne 2 ici avant transpose)
        ang[2, 0] = np.arctan2(matR[2, 0] / np.cos(ang[1, 0]),
                            matR[2, 2] / np.cos(ang[1, 0]))
        ang[2, 1] = np.arctan2(matR[2, 0] / np.cos(ang[1, 1]),
                            matR[2, 2] / np.cos(ang[1, 1]))

        # rotation angle around z axis (colonne 1 MATLAB → ligne 0 ici avant transpose)
        ang[0, 0] = np.arctan2(matR[0, 1] / np.cos(ang[1, 0]),
                            matR[1, 1] / np.cos(ang[1, 0]))
        ang[0, 1] = np.arctan2(matR[0, 1] / np.cos(ang[1, 1]),
                            matR[1, 1] / np.cos(ang[1, 1]))

        return ang  # déjà (3x2) comme après transpose MATLAB

    # Cas dégénéré : matR[3,2] = ±1 → gimbal lock
    else:
        ang = np.zeros(3)
        # variable "roll" inexistante en MATLAB original → non utilisée ici
        # on garde simplement les 3 angles comme définis par le cas particulier

        if matR[2, 1] == 1:
            ang[1] = -np.pi / 2
            ang[2] = np.arctan2(-matR[0, 2], -matR[1, 2]) - ang[0]
            if ang[2] > np.pi:
                ang[2] -= 2 * np.pi
            elif ang[2] < -np.pi:
                ang[2] += 2 * np.pi

        else:  # matR[2,1] == -1
            ang[1] = np.pi / 2
            ang[2] = ang[0] - np.arctan2(matR[0, 2], matR[1, 2])
            if ang[2] > np.pi:
                ang[2] -= 2 * np.pi
            elif ang[2] < -np.pi:
                ang[2] += 2 * np.pi

        # Le MATLAB retourne ang = ang'
        return ang.reshape(3, 1)
  