from django.db import models
from clients.models import Client
from fournisseurs.models import Fournisseur
from comptes.models import Compte

class ReglementClient(models.Model):

 
    mode_choix=[
        ("Espece", "Espèce"),
        ("Cheque", "Cheque"),
        ("Virement" ,"Virement"),
        ("Lettre de change", "Lettre de change"),
    ]

    numero = models.CharField(max_length=20, unique=True, blank=True)
    date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    montant = models.DecimalField(max_digits=12, decimal_places=3)

    compte=models.ForeignKey(Compte, on_delete=models.PROTECT,  verbose_name = "0.1- comptes")

    libelle = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    mode_paiement = models.CharField(max_length=50, blank=True, choices=mode_choix)

    def save(self, *args, **kwargs):

        nouveau = self.pk is None
        if not self.numero:

            dernier = ReglementClient.objects.order_by("-id").first()

            if dernier:
                num = int(dernier.numero.split("-")[1]) + 1
            else:
                num = 1

            self.numero = f"RC-{num:04d}"

        super().save(*args, **kwargs)

        if nouveau:
            MouvementCompte.objects.create(
                date=self.date,
                type_mouvement='entree',
                compte=self.compte,
                montant=self.montant,
                reference=f"Reglement client {self.id}"
            )
    def __str__(self):
        return self.numero



class ReglementFournisseur(models.Model):

    
    mode_choix=[
        ("Espece", "Espèce"),
        ("Cheque", "Cheque"),
        ("Virement" ,"Virement"),
        ("Lettre de change", "Lettre de change"),
    ]

    numero = models.CharField(max_length=20, unique=True, blank=True)
    date = models.DateField()
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)

    montant = models.DecimalField(max_digits=12, decimal_places=3)

    compte=models.ForeignKey(Compte, on_delete=models.PROTECT,  verbose_name = "0.1- comptes")

    libelle = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    mode_paiement = models.CharField(max_length=50, blank=True, choices=mode_choix)

    def save(self, *args, **kwargs):

        nouveau = self.pk is None

        if not self.numero:

            dernier = ReglementFournisseur.objects.order_by("-id").first()

            if dernier:
                num = int(dernier.numero.split("-")[1]) + 1
            else:
                num = 1

            self.numero = f"RF-{num:04d}"

        super().save(*args, **kwargs)

        if nouveau:
            MouvementCompte.objects.create(
                date=self.date,
                type_mouvement='sortie',
                compte=self.compte,
                montant=self.montant,
                reference=f"Reglement fournisseur {self.id}"
            )

    def __str__(self):
        return self.numero

#-------- Class mouvement des comptes


class MouvementCompte(models.Model):

    TYPE_MOUVEMENT = (
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    )

    date = models.DateField()
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT)
    compte = models.ForeignKey(
        'comptes.Compte',
        on_delete=models.PROTECT,
        related_name='mouvements'
    )
    montant = models.DecimalField(max_digits=12, decimal_places=3)
    reference = models.CharField(max_length=100, blank=True)
    observation = models.TextField(blank=True)
    origine = models.CharField(max_length=50, blank=True)

    # Ici on crée une propriété pour générer la référence automatique
    @property
    def reference_auto(self):
        # Si tu n'as pas de relation avec ReglementClient ou ReglementFournisseur
        # on retourne juste un libellé type "MC n°ID"
        return f"MC n°{self.id}"

    def __str__(self):
        return f"{self.date} - {self.compte} - {self.montant}"