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

class Referencia(models.Model):
    nom = models.CharField(max_length=500)
    email = models.CharField(max_length=500)

    def __unicode__(self):
        return self.nom

class TitolUniversitari(models.Model):
    nom = models.CharField(max_length=500)
    titolgeneric = models.ForeignKey(TitolGeneric)

    def __unicode__(self):
        return self.nom

class Curriculum(models.Model):
    email = models.CharField(max_length=500)
    nom = models.CharField(max_length=500)
    file = models.FileField(storage=stor.fs, upload_to='.')

    # Suportem fins a tres titols (suficient?)
    titol1 = models.ForeignKey(TitolUniversitari, related_name='titol1')
    titol2 = models.ForeignKey(TitolUniversitari, related_name='titol2', blank=True, null=True)
    titol3 = models.ForeignKey(TitolUniversitari, related_name='titol3', blank=True, null=True)

    # Fins a tres referencies
    ref1 = models.ForeignKey(Referencia, related_name='ref1', blank=True, null=True)
    ref2 = models.ForeignKey(Referencia, related_name='ref2', blank=True, null=True)
    ref3 = models.ForeignKey(Referencia, related_name='ref3', blank=True, null=True)

    # entrevistat = models.BooleanField

    def __unicode__(self):
        return self.email
