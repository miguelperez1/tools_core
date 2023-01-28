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
    ]
}

LIGHT_TYPES = []

for k, v in LIGHT_CLASS.items():
    LIGHT_TYPES.append(v)
