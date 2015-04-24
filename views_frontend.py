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

CONTENT_TYPES = ['image', 'video', 'application/pdf']
MAX_UPLOAD_SIZE = "5242880"

# Quan treiem les pàgines amb RequestContext, fem visibles a la template
# algunes variables que no estarien disponibles.
# Les altres funcions cridaran a aquesta en haver de fer el render de les templates
def renderResponse(request,tmpl,dic):
    return render_to_response(tmpl, dic, context_instance=RequestContext(request))

class PrimerPasForm(forms.Form):
    email = forms.CharField()
    feina = forms.CharField()

class SegonPasForm_Docents(forms.Form):
    nom = forms.CharField()
    llinatges = forms.CharField()
    codi_edicio = forms.CharField()
    tel = forms.CharField()
    pob = forms.CharField()
    titol1 = forms.ModelChoiceField(queryset=TitolGeneric.objects.all())
    tit1 = forms.CharField()
    uni1 = forms.CharField()
    dta1 = forms.DateField()
    titol2 = forms.ModelChoiceField(queryset=TitolGeneric.objects.all(), required=False)
    tit2 = forms.CharField(required=False)
    uni2 = forms.CharField(required=False)
    dta2 = forms.DateField(required=False)
    titol3 = forms.ModelChoiceField(queryset=TitolGeneric.objects.all(), required=False)
    tit3 = forms.CharField(required=False)
    uni3 = forms.CharField(required=False)
    dta3 = forms.DateField(required=False)

    ref1 = forms.CharField(required=False)
    ref1_email = forms.CharField(required=False)
    ref2 = forms.CharField(required=False)
    ref2_email = forms.CharField(required=False)
    ref3 = forms.CharField(required=False)
    ref3_email = forms.CharField(required=False)

    currfile = forms.FileField()

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

            cr = None
            try:
                # Comprovem que l'adreça email ja existeix...
                cr = Curriculum.objects.get(email=email)
            except:
                # Si no existeix, creem un objecte nou
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

# Comprovem que no fa més de 1 hora que hem demanat el link
def tooLate(cr):
    delta_seconds = (datetime.datetime.now() - cr.codi_data).seconds
    if delta_seconds > 3600:
        return True
    return False

def segonPas(request):
    codi = request.GET.get('codi')
    try:
        cr = Curriculum.objects.get(codi_edicio=codi)
        if not tooLate(cr):
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

def getTitolUniversitari(gen, nom, uni, data):
    try:
        t = TitolUniversitari(nom=nom, titolgeneric=gen, uni=uni, data=data)
        return t
    except:
        return None

def file_is_valid(content):
    content_type = content.content_type.split('/')[0]
    # Falta comprovar el content_type, però s'han de fer experiments perquè
    # alguns navegadors no ho fan standard...
    if content._size > int(MAX_UPLOAD_SIZE):
        return False

    # if content_type in CONTENT_TYPES:
    #     if content._size > int(MAX_UPLOAD_SIZE):
    #         return False
    # else:
    #     return False

    return True

def processar_docent(request, cr, f):
    if f.is_valid():
        dta = f.cleaned_data

        cr.nom = dta['nom']
        cr.llinatges = dta['llinatges']
        cr.poblacio = dta['pob']
        cr.telefon = dta['tel']

        # TODO: també mirar com podem posar una grandària màxima pel fitxer
        # TODO: i que el fitxer sigui de tipus PDF, odt... (que no hi pugui haver .exes...)
        file = dta['currfile']
        if file_is_valid(file):
            print "---file valid"
            cr.file = file
            cr.ref1 = dta['ref1']
            cr.ref1_email = dta['ref1_email']
            cr.ref2 = dta['ref2']
            cr.ref2_email = dta['ref2_email']
            cr.ref3 = dta['ref3']
            cr.ref3_email = dta['ref3_email']

            tu1 = getTitolUniversitari(dta['titol1'], dta['tit1'], dta['uni1'], dta['dta1'])
            tu2 = getTitolUniversitari(dta['titol2'], dta['tit2'], dta['uni2'], dta['dta2'])
            tu3 = getTitolUniversitari(dta['titol3'], dta['tit3'], dta['uni3'], dta['dta3'])

            if tu1 is not None:
                tu1.save()
                cr.titol1 = tu1
            if tu2 is not None:
                tu2.save()
                cr.titol2 = tu2
            if tu3 is not None:
                tu3.save()
                cr.titol3 = tu3

            try:
                cr.save()
                return renderResponse(
                    request,
                    'curriculums/final.html', {}
                )
            except Exception as e:
                print e

                # Error gravant el currículum. Esborrar dades...
                if tu1 is not None: tu1.delete()
                if tu2 is not None: tu2.delete()
                if tu3 is not None: tu3.delete()

    # TODO: Mostrar errors
    # print f
    return redirect('curr-primerpas')

def processar_nodocent(cr, f):
    pass


def final(request):
    if request.POST:
        codi = request.POST.get('codi_edicio')
        cr = Curriculum.objects.get(codi_edicio=codi)
        if not tooLate(cr):
            if cr.categoria == 'D':
                f = SegonPasForm_Docents(request.POST, request.FILES)
                return processar_docent(request, cr, f)
            elif cr.categoria == 'N':
                f = SegonPasForm_NoDocents(request.POST, request.FILES)
                return processar_nodocent(cr, f)

    # TODO: Mostrar errors
    return redirect('curr-primerpas')
