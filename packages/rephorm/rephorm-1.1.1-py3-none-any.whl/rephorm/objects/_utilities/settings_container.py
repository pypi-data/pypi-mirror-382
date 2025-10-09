"""
Generic settings container.
Encapsulates all settings for a specific object.
"""
class SettingsContainer:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)