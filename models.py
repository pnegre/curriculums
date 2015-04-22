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
    CAT_CHOICES = (
		(u'D', u'Docent'),
		(u'N', u'No Docent'),
    )

    email = models.CharField(max_length=500)
    nom = models.CharField(max_length=500, blank=True, null=True)
    poblacio = models.CharField(max_length=500, blank=True, null=True)
    telefon = models.CharField(max_length=500, blank=True, null=True)
    categoria_laboral_nodocent = models.ForeignKey(CategoriaLaboralND, blank=True, null=True)
    file = models.FileField(storage=stor.fs, upload_to='.', blank=True, null=True)
    observacions = models.CharField(max_length=1000, blank=True, null=True)
    entrevistat = models.BooleanField(default=False)

    categoria = models.CharField(max_length=2, choices=CAT_CHOICES)
    codi_edicio = models.CharField(max_length=500) # Codi per editar el curriculum

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
