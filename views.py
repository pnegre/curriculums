# -*- coding: utf-8 -*-

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

class SegonPasForm(forms.Form):
    nom = forms.CharField()
    email = forms.CharField()
    currfile = forms.FileField()

def primerPas(request):
    return renderResponse(
        request,
        'curriculums/index.html', {
    } )

def segonPas(request):
    # Aquí només hi hauria d'arribar en cas de clicar al link enviat al correu
    if request.POST:
        f = PrimerPasForm(request.POST)
        if f.is_valid():
            # TODO: comprovar...
            email = f.cleaned_data['email']

            families = FamiliaTitol.objects.all()

            return renderResponse(
                request,
                'curriculums/segonpas.html', {
                    'email': email,
                    'families': families,
            } )

    # TODO: Mostrar errors
    return redirect('curr-primerpas')

def final(request):
    return redirect('curr-primerpas')
    
    if request.POST:
        # ALERTA: VALIDAR!!! (o fer amb form django)
        f = SegonPasForm(request.POST, request.FILES)
        if f.is_valid():
            # TODO: comprovar amb codi de seguretat...
            dta = f.cleaned_data
            fle = dta['currfile']
            nom = dta['nom']
            email = dta['email']
            # real_name = stor.fs.save('prova', fle)

            c = Curriculum(nom=nom, email=email, file=fle)
            c.save()

            return renderResponse(
                request,
                'curriculums/final.html', {}
            )

    # TODO: Mostrar errors
    return redirect('curr-primerpas')
