class PlateGirderBridge:
    """High-level model for a plate girder bridge."""
    def __init__(self, dto):
        self.dto = dto

    def summary(self):
        return {"spans": self.dto.spans, "spacing": self.dto.girder_spacing}
