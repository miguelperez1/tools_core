LIGHT_CLASS = {
    "vray": [
        'VRayLightIESShape',
        'VRayLightSphereShape',
        'VRayLightRectShape',
        'VRayLightDomeShape',
    ],
    "maya": [
        'volumeLight',
        'areaLight',
        'spotLight',
        'pointLight',
        'directionalLight',
        'ambientLight'
    ],
    "arnold": [
        'aiAreaLight',
        'aiSkyDomeLight'
    ]
}

LIGHT_TYPES = []

for render_engine, lights in LIGHT_CLASS.items():
    for light_type in lights:
        LIGHT_TYPES.append(light_type)

ICONS = {
    "VRayLightRectShape": "C:\\Program Files\\Chaos Group\\V-Ray\\Maya 2023 for x64\\maya_vray\\icons\\shelf_LightRect_200.png",
    "VRayLightSphereShape": "C:\\Program Files\\Chaos Group\\V-Ray\\Maya 2023 for x64\\maya_vray\\icons\\shelf_LightSphere_200.png",
    "VRayLightDomeShape": "C:\\Program Files\\Chaos Group\\V-Ray\\Maya 2023 for x64\\maya_vray\\icons\\shelf_LightDome_200.png",
    "VRayLightIESShape": "C:\\Program Files\\Chaos Group\\V-Ray\\Maya 2023 for x64\\maya_vray\\icons\\shelf_LightIES_200.png",
    "directionalLight": ":/directionallight.png",
    "aiAreaLight": "C:\\Program Files\\Autodesk\\Arnold\\maya2023\\icons\\out_aiAreaLight_200.png",
    "aiSkyDomeLight": "C:\\Program Files\\Autodesk\\Arnold\\maya2023\\icons\\out_aiSkyDomeLight_200.png",
    "connection_in": ":/hsUpStreamCon.png",
    "transform": "F:\\share\\tools\\shelf_icons\\group.png"
}
