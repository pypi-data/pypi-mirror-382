def evalTrajecto(repBase, traj_pos, traj_ang, carte=None):
    """
    Évalue une trajectoire estimée par rapport à une trajectoire de référence.

    Cette fonction compare une trajectoire estimée (positions et angles) avec une solution
    de référence stockée dans des fichiers `.npz`. Elle calcule différents scores d'erreur
    (distance, position, orientation) et affiche une visualisation 3D comparative.

    Parameters
    ----------
    repBase : str
        Chemin vers le dossier contenant les fichiers `solution.npz` et `info_seq.npz`.

    traj_pos : ndarray of shape (3, N)
        Positions estimées de la trajectoire. Chaque colonne représente une position 3D
        (X, Y, Z) pour une image donnée.

    traj_ang : ndarray of shape (3, N)
        Angles d'Euler estimés (rx, ry, rz) pour chaque position. Les angles sont en radians.

    carte : optional
        Paramètre optionnel (non utilisé dans la fonction actuelle).

    Returns
    -------
    score_pos1 : float
        Pourcentage d'erreur relative entre la distance totale estimée et la distance réelle.

    score_pos2 : float
        Pourcentage maximal d'erreur relative entre les distances inter-images estimées et
        celles de la trajectoire de référence.

    score_ang : float
        Erreur angulaire normalisée (en degrés par mètre), calculée entre la rotation finale
        estimée et la rotation finale réelle.

    score_posint : list of float
        Intégrale des erreurs de position (X, Y, Z), calculées comme l'aire sous la courbe
        des différences de position au cours du temps.

    delta_pos : ndarray of shape (3, N-1)
        Différences de position entre la solution de référence et la trajectoire estimée
        pour chaque image (sauf la dernière).
    
    Notes
    -----
    - Cette fonction utilise la bibliothèque Plotly pour afficher une figure 3D comparant 
      les trajectoires de référence et estimée.
    - Les fichiers `solution.npz` doivent contenir les clés ``sol_pos`` et ``sol_ang``.
    - Le fichier `info_seq.npz` doit contenir la clé ``Kleft``, même si elle n'est pas utilisée
      dans cette fonction.
    - Les angles d'Euler sont interprétés dans l'ordre ZYX pour la conversion en matrices de rotation.

    Examples
    --------
    >>> score_pos1, score_pos2, score_ang, score_posint, delta_pos = evalTrajecto(
    ...     repBase='data/test_seq',
    ...     traj_pos=estimated_positions,
    ...     traj_ang=estimated_angles
    ... )
    """

    import numpy as np
    import plotly.graph_objects as go
    import os
    
    def ang2rot(angles):
        """
        Convert Euler angles (rx, ry, rz) to rotation matrix.
        Angles are assumed in radians.
        """
        rx, ry, rz = angles
        Rx = np.array([[1, 0, 0],
                    [0, np.cos(rx), -np.sin(rx)],
                    [0, np.sin(rx), np.cos(rx)]])
        Ry = np.array([[np.cos(ry), 0, np.sin(ry)],
                    [0, 1, 0],
                    [-np.sin(ry), 0, np.cos(ry)]])
        Rz = np.array([[np.cos(rz), -np.sin(rz), 0],
                    [np.sin(rz), np.cos(rz), 0],
                    [0, 0, 1]])
        return Rz @ Ry @ Rx


    def rodrigues(R):
        """
        Convert rotation matrix to rotation vector (axis-angle) or vice versa.
        """
        if R.shape == (3,):
            # Rotation vector -> matrix
            theta = np.linalg.norm(R)
            if theta < 1e-12:
                return np.eye(3)
            omega = R / theta
            K = np.array([[0, -omega[2], omega[1]],
                        [omega[2], 0, -omega[0]],
                        [-omega[1], omega[0], 0]])
            return np.eye(3) + np.sin(theta)*K + (1-np.cos(theta))*(K@K)
        elif R.shape == (3, 3):
            # Matrix -> rotation vector
            U, _, Vt = np.linalg.svd(R)
            R = U @ Vt  # project onto SO(3)
            theta = np.arccos(np.clip((np.trace(R)-1)/2, -1, 1))
            if theta < 1e-12:
                return np.zeros(3)
            else:
                return (theta/(2*np.sin(theta))) * np.array([R[2,1]-R[1,2],
                                                            R[0,2]-R[2,0],
                                                            R[1,0]-R[0,1]])
        else:
            raise ValueError("Input must be 3-vector or 3x3 matrix")


    # Chargement des données MATLAB
    # solution = loadmat(f"{repBase}/solution.mat")
    # info_seq = loadmat(f"{repBase}/info_seq.mat")
    solution = np.load(os.path.join(repBase, 'solution.npz'))
    info_seq = np.load(os.path.join(repBase, 'info_seq.npz'))
    sol_pos = solution['sol_pos']
    sol_ang = solution['sol_ang']
    matK = info_seq['Kleft']
    
    nbIma = sol_pos.shape[1]
    interdist_est = []
    delta_pos = []

    # Calcul des distances et différences de positions
    for cpt in range(nbIma-1):
        interdist_est.append(np.linalg.norm(traj_pos[:,cpt+1]-traj_pos[:,cpt]))
        delta_pos.append(sol_pos[:,cpt] - traj_pos[:,cpt])
    
    interdist_est = np.array(interdist_est)
    delta_pos = np.array(delta_pos).T  # 3 x (nbIma-1)
    
    totaldist_est = np.sum(interdist_est)
    totaldist = np.sum(np.linalg.norm(np.diff(sol_pos, axis=1), axis=0))
    interdist = np.linalg.norm(np.diff(sol_pos, axis=1), axis=0)

    score_pos1 = 100 * np.abs(totaldist_est - totaldist) / totaldist
    score_pos2 = 100 * np.max(np.abs(interdist_est - interdist) / interdist)

    # Calcul de l'erreur angulaire
    Rest = ang2rot(traj_ang[:, -1])
    Rtrue = ang2rot(sol_ang[:, -1])
    Rerr = Rest.T @ Rtrue
    rodri = rodrigues(Rerr)
    score_ang = np.linalg.norm(rodri) * 180 / (np.pi * totaldist)

    score_posint = [np.trapezoid(delta_pos[0,:]), np.trapezoid(delta_pos[1,:]), np.trapezoid(delta_pos[2,:])]

    print(f"score_pos1 = {score_pos1:.2f}")
    print(f"score_pos2 = {score_pos2:.2f}")
    print(f"score_ang = {score_ang:.2f}")
    print(f"integral Delta pos X = {score_posint[0]:.2f}")
    print(f"integral Delta pos Y = {score_posint[1]:.2f}")
    print(f"integral Delta pos Z = {score_posint[2]:.2f}")

    # ==== Affichage comparatif ====
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=sol_pos[0,:], y=sol_pos[1,:], z=sol_pos[2,:], mode='lines', line=dict(color='red'), name='ref'))
    fig.add_trace(go.Scatter3d(x=traj_pos[0,:], y=traj_pos[1,:], z=traj_pos[2,:], mode='lines', line=dict(color='blue'), name='estim'))
    fig.update_layout(title='Comparaison estimation de la trajectoire 3D (rouge=ref)',
                      scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
                      legend=dict(x=0, y=1))
    fig.show()

    return score_pos1, score_pos2, score_ang, score_posint, delta_pos
