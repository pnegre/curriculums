# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

import storage as stor

class FamiliaTitol(models.Model):
    nom = models.CharField(max_length=500)
    ordre_numeric = models.IntegerField()

    def __unicode__(self):
        return self.nom

class TitolGeneric(models.Model):
    nom = models.CharField(max_length=500)
    familia = models.ForeignKey(FamiliaTitol)

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

    # Data en que s'introdueix el currículum el primer cop
    data_inicial = models.DateTimeField()

    # DOCENT / NO DOCENT
    categoria = models.CharField(max_length=2, choices=CAT_CHOICES)

    email = models.CharField(max_length=500)
    nom = models.CharField(max_length=500, blank=True, null=True)
    llinatges = models.CharField(max_length=500, blank=True, null=True)
    poblacio = models.CharField(max_length=500, blank=True, null=True)
    telefon = models.CharField(max_length=500, blank=True, null=True)
    categoria_laboral_nodocent = models.ForeignKey(CategoriaLaboralND, blank=True, null=True)
    file = models.FileField(storage=stor.fs, upload_to='.', blank=True, null=True)
    observacions = models.CharField(max_length=1000, blank=True, null=True)
    entrevistat = models.BooleanField(default=False)

    # Indica si el currículum és vàlid (l'usuari ha executat el 2on pas)
    valid = models.BooleanField(default=False)

    # Codi per editar el curriculum
    codi_edicio = models.CharField(max_length=500)
    # Data de creació del codi
    codi_data = models.DateTimeField()

    # Suportem fins a tres titols (suficient?)
    titol1_generic = models.ForeignKey(TitolGeneric, related_name='titol1_generic', blank=True, null=True)
    titol1_nom = models.CharField(max_length=500, blank=True, null=True)
    titol1_uni = models.CharField(max_length=500, blank=True, null=True)
    titol1_data = models.DateTimeField(blank=True, null=True)

    titol2_generic = models.ForeignKey(TitolGeneric, related_name='titol2_generic', blank=True, null=True)
    titol2_nom = models.CharField(max_length=500, blank=True, null=True)
    titol2_uni = models.CharField(max_length=500, blank=True, null=True)
    titol2_data = models.DateTimeField(blank=True, null=True)

    titol3_generic = models.ForeignKey(TitolGeneric, related_name='titol3_generic', blank=True, null=True)
    titol3_nom = models.CharField(max_length=500, blank=True, null=True)
    titol3_uni = models.CharField(max_length=500, blank=True, null=True)
    titol3_data = models.DateTimeField(blank=True, null=True)

    # Fins a tres referencies
    ref1 = models.CharField(max_length=500, blank=True, null=True)
    ref1_email = models.CharField(max_length=500, blank=True, null=True)
    ref2 = models.CharField(max_length=500, blank=True, null=True)
    ref2_email = models.CharField(max_length=500, blank=True, null=True)
    ref3 = models.CharField(max_length=500, blank=True, null=True)
    ref3_email = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
		permissions = (
			("veure_curriculums_docents","Pot veure currículums docents"),
			("veure_curriculums_no_docents","Pot veure currículums no docents"),
		)

    def __unicode__(self):
        return self.email


class Preferits(models.Model):
    curriculum = models.ForeignKey(Curriculum)
    usuari = models.ForeignKey(User)
