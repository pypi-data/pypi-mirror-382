import json
import os

class _GLOBALNETWORK:
    def __init__(self):
        self.collisions = []
        self.playerPosition = None
        self.BaseInfo = {}
        self.screen  = None

class _CONFIG:
    def __init__(self, path="Defaults.json"):
        self.data = {}
        self.load(path)

    def load(self, path):
        """Load JSON data with fallback defaults."""
        if not os.path.exists(path):
            print("[GameBox] No Default.json found — using override settings.")
            return
        
        with open(path, "r") as f:
            try:
                self.data = json.load(f)
                print("[GameBox] Config loaded successfully.")
            except json.JSONDecodeError:
                print("[GameBox] Error: Invalid JSON format.")

    def get(self, *keys, default=None):
        """Nested key access: config.get('player', 'speed')"""
        ref = self.data
        for key in keys:
            if isinstance(ref, dict) and key in ref:
                ref = ref[key]
            else:
                return default
        return ref



GLOBAL = _GLOBALNETWORK()