from django.db import models

# Create your models here.

import storage as stor

class FamiliaTitol(models.Model):
    nom = models.CharField(max_length=500)

    def __unicode__(self):
        return self.nom

class TitolGeneric(models.Model):
    nom = models.CharField(max_length=500)
    familia = models.ForeignKey(FamiliaTitol)

    def __unicode__(self):
        return self.nom

class TitolUniversitari(models.Model):
    nom = models.CharField(max_length=500)
    titolgeneric = models.ForeignKey(TitolGeneric)

    def __unicode__(self):
        return self.nom

class CategoriaLaboralND(models.Model):
    nom = models.CharField(max_length=500)

    def __unicode__(self):
        return self.nom


class Curriculum(models.Model):
    email = models.CharField(max_length=500)
    nom = models.CharField(max_length=500)
    poblacio = models.CharField(max_length=500)
    telefon = models.CharField(max_length=500)
    categoria_laboral_nodocent = models.ForeignKey(CategoriaLaboralND, blank=True, null=True)
    file = models.FileField(storage=stor.fs, upload_to='.')
    observacions = models.CharField(max_length=1000, blank=True, null=True)
    entrevistat = models.BooleanField(default=False)

    # Suportem fins a tres titols (suficient?)
    titol1 = models.ForeignKey(TitolUniversitari, related_name='titol1', blank=True, null=True)
    titol2 = models.ForeignKey(TitolUniversitari, related_name='titol2', blank=True, null=True)
    titol3 = models.ForeignKey(TitolUniversitari, related_name='titol3', blank=True, null=True)

    # Fins a tres referencies
    ref1 = models.CharField(max_length=500, blank=True, null=True)
    ref1_email = models.CharField(max_length=500, blank=True, null=True)
    ref2 = models.CharField(max_length=500, blank=True, null=True)
    ref2_email = models.CharField(max_length=500, blank=True, null=True)
    ref3 = models.CharField(max_length=500, blank=True, null=True)
    ref3_email = models.CharField(max_length=500, blank=True, null=True)

    def __unicode__(self):
        return self.email
