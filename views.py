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
    tel = forms.CharField()
    pob = forms.CharField()
    email = forms.CharField()
    titol1 = forms.ModelChoiceField(queryset=TitolGeneric.objects.all())
    tit1 = forms.CharField()
    # uni1 = forms.CharField()
    # dta1 = forms.CharField()
    currfile = forms.FileField()

def generarCodi():
    # Generem codi a partir de l'hora actual, mirant els microseconds...
    codi_sha = hashlib.sha512()
    codi_sha.update(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    return codi_sha.hexdigest()

def primerPas(request):
    if request.POST:
        f = PrimerPasForm(request.POST)
        if f.is_valid():
            email = f.cleaned_data['email']
            feina = f.cleaned_data['feina']
            codi = generarCodi()
            # Comprovem que l'adreça email ja existeix...
            # TODO: el codi hauria de tenir només vigència en 24h...
            try:
                cr = Curriculum.objects.get(email=email)
                cr.codi_edicio = codi
                cr.save()
            except:
                c = Curriculum(email=email, categoria=feina, codi_edicio=codi)
                c.save()

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

    # TODO: Mostrar errors
    return redirect('curr-primerpas')

def final(request):
    if request.POST:
        # ALERTA: VALIDAR!!! (o fer amb form django)
        f = SegonPasForm(request.POST, request.FILES)
        if f.is_valid():
            # TODO: comprovar amb codi de seguretat...
            dta = f.cleaned_data
            fle = dta['currfile']
            nom = dta['nom']
            email = dta['email']
            tit_generic_1 = dta['titol1']
            tit1 = dta['tit1']
            titol_1 = TitolUniversitari(nom=tit1, titolgeneric=tit_generic_1)
            titol_1.save()

            c = Curriculum(nom=nom, email=email, file=fle, titol1=titol_1)
            # Caldria comprovar que s'ha enregistrat bé...
            c.save()

            return renderResponse(
                request,
                'curriculums/final.html', {}
            )

    # TODO: Mostrar errors
    return redirect('curr-primerpas')
