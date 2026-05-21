from django.db import models
from django.contrib.auth.models import User


class ParkingSpot(models.Model):
    """
    Reprezentuje jedno fizyczne miejsce parkingowe.
    """
    spot_number = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"Miejsce #{self.spot_number}"


class ParkingOccupation(models.Model):
    """
    Każdy wpis reprezentuje moment ZAJĘCIA miejsca parkingowego.
    """
    parking_spot = models.ForeignKey(
        ParkingSpot,
        on_delete=models.CASCADE,
        related_name="occupations"
    )
    occupied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parking_spot} zajęte o {self.occupied_at}"

