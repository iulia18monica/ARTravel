from django.db import models
from django.contrib.auth.models import User

class Locatie(models.Model):
    CATEGORII = [
        ('food', 'Food'),
        ('art', 'Art'),
        ('selfcare', 'Selfcare'),
    ]
    nume = models.CharField(max_length=100)
    imagine = models.ImageField(upload_to='locatii/')
    descriere = models.TextField()
    categorie = models.CharField(max_length=20, choices=CATEGORII)

    def __str__(self):
        return self.nume

class Favorit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    locatie = models.ForeignKey(Locatie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'locatie')

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Cine a scris
    content = models.TextField() # Textul recenziei
    rating = models.IntegerField(default=5) # Nota (1-5)
    created_at = models.DateTimeField(auto_now_add=True) # Data automată

    def __str__(self):
        return f"{self.user.username} - {self.rating}★"
    
class SavedRoute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nume_ruta = models.CharField(max_length=100) # Ex: "Plimbare de seară"
    descriere_locatii = models.TextField()       # Ex: "Samsara, Muzeu, Parc"
    google_maps_url = models.TextField()         # Link-ul lung către Maps
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nume_ruta} ({self.user.username})"