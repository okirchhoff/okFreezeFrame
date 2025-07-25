# create_frozen_camera_view.py
#
# Original concept and initial code by the user.
# Refactoring and debugging by Google's Gemini.
# Final, correct logic for image plane freezing by the user.
#
# v2.0.0 (25/07/2025):
#   - FINAL WORKING VERSION: The user correctly identified that freezing an image
#     sequence requires disconnecting 'time1.outTime' from the image plane's
#     '.frameExtension' attribute before setting the frame value.
#     This is the robust, correct solution.

import maya.cmds as cmds

def create_frozen_camera_view():
    """
    Creates a static, "frozen" duplicate of the active model panel's camera
    at the current frame. This includes freezing its transform, camera settings,
    and any associated image planes. A new floating modelPanel is created
    to display the view from the frozen camera.
    """
    current_time = cmds.currentTime(q=True)

    # 1. Get the active camera
    panel = cmds.getPanel(withFocus=True)
    if not panel or "modelPanel" not in cmds.getPanel(typeOf=panel):
        cmds.warning("Please make sure your cursor is over a viewport.")
        return None

    cam_transform = cmds.modelEditor(panel, q=True, camera=True)
    if not cam_transform:
        cmds.warning("Could not get a camera from the active viewport.")
        return None

    if cmds.objectType(cam_transform, isType='camera'):
        cam_shape = cmds.ls(cam_transform, long=True)[0]
        cam_transform = cmds.listRelatives(cam_shape, parent=True, fullPath=True)[0]
    else:
        cam_transform = cmds.ls(cam_transform, long=True)[0]
        cam_shape = cmds.listRelatives(cam_transform, shapes=True, type='camera', fullPath=True)[0]

    # 2. Duplicate camera and bake its transform
    frozen_cam_name = f"frozenCam_{cam_transform.split('|')[-1].replace(':', '_')}_{int(current_time)}"
    frozen_cam = cmds.duplicate(cam_transform, name=frozen_cam_name, renameChildren=True)[0]
    frozen_shape = cmds.listRelatives(frozen_cam, shapes=True, type='camera', fullPath=True)[0]
    cmds.bakeResults(frozen_cam, simulation=True, time=(current_time, current_time))

    # 3. Freeze and lock camera attributes
    for attr in ['t', 'r', 's']:
        for axis in ['x', 'y', 'z']: cmds.setAttr(f"{frozen_cam}.{attr}{axis}", lock=True)
    
    cam_attrs = [
        "focalLength", "verticalFilmAperture", "horizontalFilmAperture", "lensSqueezeRatio", "cameraScale",
        "filmFit", "filmFitOffset", "nearClipPlane", "farClipPlane", "fStop", "focusDistance"
    ]
    for attr in cam_attrs:
        source_attr, dest_attr = f"{cam_shape}.{attr}", f"{frozen_shape}.{attr}"
        if not cmds.objExists(source_attr): continue
        connections = cmds.listConnections(dest_attr, s=True, d=False, p=True) or []
        for c in connections: cmds.disconnectAttr(c, dest_attr)
        try:
            val = cmds.getAttr(source_attr, time=current_time)
            cmds.setAttr(dest_attr, val, lock=True)
        except Exception as e:
            print(f"Could not transfer camera attribute '{attr}': {e}")

    # 4. Handle Image Planes
    all_ip_shapes = cmds.ls(type='imagePlane', long=True)
    for source_ip_shape in all_ip_shapes:
        dest_plugs = cmds.listConnections(f"{source_ip_shape}.message", plugs=True, d=True, s=False)
        if not dest_plugs: continue
        
        connected_cam_shape = cmds.ls(dest_plugs[0].split('.')[0], long=True)[0]
        if connected_cam_shape == cam_shape:
            source_ip_transform = cmds.listRelatives(source_ip_shape, parent=True, fullPath=True)[0]

            frozen_ip_nodes = cmds.imagePlane(camera=frozen_cam, showInAllViews=False)
            frozen_ip_transform = cmds.rename(frozen_ip_nodes[0], f"frozen_{source_ip_transform.split('|')[-1].replace(':', '_')}#")
            frozen_ip_shape = cmds.listRelatives(frozen_ip_transform, shapes=True, fullPath=True)[0]

            # Copy all relevant attributes from the source
            shape_attrs_to_copy = ['displayMode', 'imageName', 'alphaGain', 'depth', 'offsetX', 'offsetY', 'sizeX', 'sizeY', 'fit', 'useFrameExtension', 'frameOffset']
            for attr in shape_attrs_to_copy:
                if cmds.attributeQuery(attr, node=source_ip_shape, exists=True):
                    val = cmds.getAttr(f"{source_ip_shape}.{attr}", time=current_time)
                    if cmds.getAttr(f"{source_ip_shape}.{attr}", type=True) == 'string':
                        cmds.setAttr(f"{frozen_ip_shape}.{attr}", val, type='string')
                    else:
                        cmds.setAttr(f"{frozen_ip_shape}.{attr}", val)
            
            # This is the user's correct and working solution to freeze an image sequence.
            if cmds.getAttr(f"{frozen_ip_shape}.useFrameExtension"):
                # Calculate the target frame
                frame_to_set = current_time + cmds.getAttr(f"{frozen_ip_shape}.frameOffset")
                
                # Disconnect the timeline's control over the image sequence
                try:
                    cmds.disconnectAttr('time1.outTime', f"{frozen_ip_shape}.frameExtension")
                except Exception as e:
                    print(f"Info: Could not disconnect time from frameExtension (likely already disconnected). {e}")

                # Now, set the static frame and lock it
                cmds.setAttr(f"{frozen_ip_shape}.frameExtension", frame_to_set, lock=True)

            # Lock everything down
            for attr in ['t', 'r', 's']:
                for axis in ['x', 'y', 'z']: cmds.setAttr(f"{frozen_ip_transform}.{attr}{axis}", lock=True)
            
            attrs_to_lock = ['imageNumber', 'useFrameExtension', 'depth', 'offsetX', 'offsetY', 'sizeX', 'sizeY', 'alphaGain', 'fit', 'displayMode']
            for attr in attrs_to_lock:
                if cmds.attributeQuery(attr, node=frozen_ip_shape, exists=True) and not cmds.getAttr(f"{frozen_ip_shape}.{attr}", lock=True):
                     cmds.setAttr(f"{frozen_ip_shape}.{attr}", lock=True)

    # 5. Create new floating viewport
    win_name = f"frozenView_{cam_transform.split('|')[-1].replace(':', '_')}_{int(current_time)}_win"
    if cmds.window(win_name, exists=True): cmds.deleteUI(win_name)
    win = cmds.window(win_name, title=win_name.replace("_win", ""), widthHeight=(800, 450))
    layout = cmds.paneLayout()
    new_panel = cmds.modelPanel(camera=frozen_cam)
    
    try: # Copy display settings
        settings = {
            'displayAppearance': cmds.modelEditor(panel, q=True, displayAppearance=True),
            'wireframeOnShaded': cmds.modelEditor(panel, q=True, wireframeOnShaded=True),
            'displayTextures': cmds.modelEditor(panel, q=True, displayTextures=True),
            'useDefaultMaterial': cmds.modelEditor(panel, q=True, useDefaultMaterial=True)
        }
        cmds.modelEditor(new_panel, edit=True, **settings)
    except: pass

    cmds.showWindow(win)
    print(f"Successfully created frozen camera '{frozen_cam}' in new view.")
    return frozen_cam