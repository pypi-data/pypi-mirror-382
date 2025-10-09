import numpy as np
import plotly.graph_objects as go

def vue3D(fig, pos3D, matK, sizeim, attitude, position, camColor, operation):
    """
    Affiche une vue 3D interactive de nuages de points et de caméras avec Plotly.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Objet figure Plotly dans lequel la scène 3D est affichée ou mise à jour.
    pos3D : ndarray
        Coordonnées 3D des points dans le repère monde (array de forme (3, N)).
    matK : ndarray
        Matrice des paramètres intrinsèques de la caméra (3x3).
    sizeim : tuple of int
        Dimensions de l'image (hauteur, largeur), utilisées pour le champ de vision.
    attitude : ndarray
        Angles d'attitude de la caméra (angles d'Euler ou matrice de rotation).
    position : ndarray
        Position de la caméra dans le repère monde (vecteur de taille 3).
    camColor : str or tuple
        Couleur utilisée pour représenter la caméra dans la scène.
    operation : {'create', 'addcam', 'addpts'}
        Type d'opération à effectuer :
            - 'create' : crée une nouvelle scène 3D,
            - 'addcam' : ajoute une caméra à la scène,
            - 'addpts' : ajoute un nuage de points à la scène.
            
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Objet figure Plotly dans lequel la scène 3D est affichée ou mise à jour.
        
    Notes
    -----
    Cette fonction permet de visualiser des scènes 3D de manière interactive avec Plotly.
    Elle peut être utilisée pour représenter des caméras virtuelles, des trajectoires,
    ou des nuages de points 3D dans un repère monde, avec une gestion dynamique
    des éléments affichés selon l'opération demandée.

    Example
    -------
    >>> from imicpe.reco3D import vue3D
    >>> import plotly.graph_objects as go
    >>> fig = go.Figure()
    >>> vue3D(fig, pos3D, matK, (480, 640), attitude, position, 'blue', 'create')
    """

    # """
    # 3D view function for displaying point clouds and cameras.
    
    # :param fig: The figure handler
    # :param pos3D: 3D positions of the points in world coordinates (3xN array)
    # :param matK: Intrinsic camera parameters
    # :param sizeim: Image size (height, width)
    # :param attitude: Camera attitude angles (Euler angles)
    # :param position: Camera position in world coordinates
    # :param camColor: Camera display color
    # :param operation: Display operation, 'create', 'addcam', or 'addpts'
    # """
    seuil_dist = 30  # threshold for deleting points that are too far away
    # Check for correct number of arguments
    if fig is not None and type(fig) is not go.Figure:
        print('First argument must be a Plotly figure')
        return
    
    if len(attitude) == 0 or len(position) == 0:
        print('Attitude and position should be provided')
        return
    
    if (pos3D.shape[0] > 3):
        pos3D=pos3D.T
        print('warning : le tableau pos3D doit etre 3xN')
        
    # Prepare params
    params = {
        'fig': fig,
        'pt3DStyle': 'blue',
        'camColor': camColor,
        'holdon': False if operation == 'create' else True,
        'tail': 1,
    }
    
    nb_points = pos3D.shape[1]
    
    
    # Calculate distance between camera and 3D points
    if len(position) == 0:
        tensP = attitude
        vec = pos3D - np.repeat(tensP[:, 3].reshape(3, 1), nb_points, axis=1)
        dist = np.linalg.norm(vec, axis=0)
    else:
        Rloc = _euler_to_rot(attitude, 'zxy')
        tensP = np.hstack([Rloc, -np.dot(Rloc, position.reshape(-1, 1))])
        vec = pos3D - np.repeat(position.reshape(3, 1), nb_points, axis=1)
        dist = np.linalg.norm(vec, axis=0)
    
    # Filter points that are too far away
    indOK = np.where(dist < seuil_dist)[0]
    pos3D_filtered = pos3D[:, indOK]
    if fig is None:
        # Create the plotly figure
        fig = go.Figure()

    # Operation: 'addpts' means just add 3D points
    if operation == 'addpts':
        fig.add_trace(go.Scatter3d(
            x=pos3D_filtered[0, :],
            y=pos3D_filtered[1, :],
            z=pos3D_filtered[2, :],
            mode='markers',
            marker=dict(color='red', size=5)
        ))

    # Operation: 'addcam' means add the camera only
    elif operation == 'addcam':
        _plot_camera(tensP, matK, sizeim, fig, camColor)

    # Operation: 'create' means both camera and 3D points
    else:
        fig.add_trace(go.Scatter3d(
            x=pos3D_filtered[0, :],
            y=pos3D_filtered[1, :],
            z=pos3D_filtered[2, :],
            mode='markers',
            marker=dict(color='blue', size=5)
        ))
        _plot_camera(tensP, matK, sizeim, fig, camColor)

    # Set figure layout
    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
        ),
        title=f"3D View",
        width=800,
        height=800,
    )

    return fig

def _plot_camera(tensP, matK, sizeim, fig, camColor):
    """
    Plots the camera as a cone shape in the 3D space.
    """
    if len(tensP.shape) < 3:
        tensP = tensP[:,:,np.newaxis]
    nb_cam = tensP.shape[2]

    imasize =  [sizeim[1], sizeim[0]]#np.fliplr(sizeim).squeeze()  # Flip size to [width, height]
    for cptC in range(nb_cam):
        current_tensP = tensP[:, :, cptC]
        cone_vertices = np.zeros((3, 5))
        vtmp = np.array([
            [1, imasize[0], imasize[0], 1],
            [1, 1, imasize[1], imasize[1]],
            [1, 1, 1, 1]
        ])

        matK_inv = np.linalg.inv(matK)
        cone_vertices[:, 1:] = np.dot(matK_inv, vtmp) * 2  # Use tail length as scaling factor
    
    
        
        cVWorld = np.dot(current_tensP[:, :3].T, (cone_vertices - current_tensP[:, 3].reshape(3, 1)))

        # Add the cone edges to the plot
        for i in range(4):
            fig.add_trace(go.Scatter3d(
                x=[cVWorld[0, 0], cVWorld[0, i + 1]],
                y=[cVWorld[1, 0], cVWorld[1, i + 1]],
                z=[cVWorld[2, 0], cVWorld[2, i + 1]],
                mode='lines',
                line=dict(color=camColor, width=2),
                showlegend=False  # Exclude from legend
            ))
    
            fig.add_trace(go.Scatter3d(
                x=[cVWorld[0, i + 1], cVWorld[0, (i + 1) % 4 + 1]],  # Cycle through the vertices
                y=[cVWorld[1, i + 1], cVWorld[1, (i + 1) % 4 + 1]],
                z=[cVWorld[2, i + 1], cVWorld[2, (i + 1) % 4 + 1]],
                mode='lines',
                line=dict(color=camColor, width=2),
                showlegend=False  # Exclude from legend
            ))

def _euler_to_rot(euler_angles, euler_order='xyz'):
    """
    Convert Euler angles to rotation matrix using the specified order.
    """
    cx, cy, cz = np.cos(np.radians(euler_angles.squeeze()))
    sx, sy, sz = np.sin(np.radians(euler_angles.squeeze()))

    R_x = np.array([[1, 0, 0],
                    [0, cx, -sx],
                    [0, sx, cx]])

    R_y = np.array([[cy, 0, sy],
                    [0, 1, 0],
                    [-sy, 0, cy]])

    R_z = np.array([[cz, -sz, 0],
                    [sz, cz, 0],
                    [0, 0, 1]])

    if euler_order == 'xyz':
        return np.dot(R_z, np.dot(R_y, R_x))
    elif euler_order == 'zyx':
        return np.dot(R_x, np.dot(R_y, R_z))
    # Other orders can be added as needed

    return np.eye(3)  # Default to identity if no valid order is found

