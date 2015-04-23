# -*- coding: utf-8 -*-

import hashlib, datetime

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.core.mail import send_mail
from django.template import RequestContext

from django import forms

from curriculums.models import *

import storage as stor

# Quan treiem les pàgines amb RequestContext, fem visibles a la template
# algunes variables que no estarien disponibles.
# Les altres funcions cridaran a aquesta en haver de fer el render de les templates
def renderResponse(request,tmpl,dic):
    return render_to_response(tmpl, dic, context_instance=RequestContext(request))

class PrimerPasForm(forms.Form):
    email = forms.CharField()
    feina = forms.CharField()

class SegonPasForm(forms.Form):
    nom = forms.CharField()
    llinatges = forms.CharField()
    codi_edicio = forms.CharField()
    # tel = forms.CharField()
    # pob = forms.CharField()
    # email = forms.CharField()
    # titol1 = forms.ModelChoiceField(queryset=TitolGeneric.objects.all())
    # tit1 = forms.CharField()
    # # uni1 = forms.CharField()
    # # dta1 = forms.CharField()
    # currfile = forms.FileField()

def generarCodi(email):
    # Generem codi a partir de l'hora actual, mirant els microseconds...
    codi_sha = hashlib.sha512()
    codi_sha.update(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    codi_sha.update(email)
    return codi_sha.hexdigest()

def primerPas(request):
    if request.POST:
        f = PrimerPasForm(request.POST)
        if f.is_valid():
            email = f.cleaned_data['email']
            feina = f.cleaned_data['feina']
            codi = generarCodi(email)
            # Comprovem que l'adreça email ja existeix...
            # TODO: el codi hauria de tenir només vigència en 24h...
            cr = None
            try:
                cr = Curriculum.objects.get(email=email)
            except:
                cr = Curriculum(email=email, categoria=feina, codi_edicio=codi)

            cr.codi_edicio = codi
            cr.codi_data = datetime.datetime.now()
            cr.save()
            return renderResponse(
                request,
                'curriculums/codi.html', {
                    'codi': codi,
                }
            )
    return renderResponse(
        request,
        'curriculums/index.html', {
    } )

def segonPas(request):
    codi = request.GET.get('codi')
    try:
        cr = Curriculum.objects.get(codi_edicio=codi)
        if cr.categoria == 'D':
            # Docent
            families = FamiliaTitol.objects.all()
            return renderResponse(
                request,
                'curriculums/segonpas.html', {
                    'cr': cr,
                    'families': families,
            } )
        elif cr.categoria == 'N':
            # No docent
            catlaborals = CategoriaLaboralND.objects.all()
            return renderResponse(
                request,
                'curriculums/segonpas_nd.html', {
                    'cr': cr,
                    'catlaborals': catlaborals,
                }
            )
    except:
        pass

    # TODO: Mostrar errors
    return redirect('curr-primerpas')

def final(request):
    if request.POST:
        # ALERTA: VALIDAR!!! (o fer amb form django)
        f = SegonPasForm(request.POST, request.FILES)
        if f.is_valid():
            # TODO: també mirar com podem posar una grandària màxima pel fitxer
            # TODO: i que el fitxer sigui de tipus PDF, odt... (que no hi pugui haver .exes...)
            dta = f.cleaned_data
            codi = dta['codi_edicio']

            try:
                cr = Curriculum.objects.get(codi_edicio=codi)
                # fle = dta['currfile']
                nom = dta['nom']
                llinatges = dta['llinatges']
                # tit_generic_1 = dta['titol1']
                # tit1 = dta['tit1']
                # titol_1 = TitolUniversitari(nom=tit1, titolgeneric=tit_generic_1)
                # titol_1.save()

                # c = Curriculum(nom=nom, email=email, file=fle, titol1=titol_1)
                # Caldria comprovar que s'ha enregistrat bé...
                cr.nom = nom
                cr.llinatges = llinatges
                cr.save()

                return renderResponse(
                    request,
                    'curriculums/final.html', {}
                )
            except:
                pass

    # TODO: Mostrar errors
    return redirect('curr-primerpas')
