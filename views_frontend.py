# -*- coding: utf-8 -*-

import hashlib, datetime, random

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.core.mail import send_mail
from django.template import RequestContext
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_protect

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

    currfile = forms.FileField(required=False)

class SegonPasForm_NoDocents(forms.Form):
    nom = forms.CharField()
    llinatges = forms.CharField()
    codi_edicio = forms.CharField()
    tel = forms.CharField()
    pob = forms.CharField()
    catlaboral = forms.ModelChoiceField(queryset=CategoriaLaboralND.objects.all())

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
    random_string = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz1234567890?¿;:_<>") for i in range(200))
    codi_sha.update(random_string)
    codi_sha.update(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    codi_sha.update(email)
    return codi_sha.hexdigest()

@csrf_protect
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
                cr = Curriculum.objects.get(email=email,categoria=feina)
            except:
                # Si no existeix, creem un objecte nou
                cr = Curriculum(email=email, categoria=feina, codi_edicio=codi)

            cr.data_inicial = datetime.datetime.now()
            cr.codi_edicio = codi
            cr.codi_data = datetime.datetime.now()
            cr.save()

            lnk = "%s/curriculums/next?codi=%s" % (settings.CURR_SERVER, codi)

            if settings.CURR_SEND_EMAIL:
                # Enviem un email i mostrem un missatge a l'usuari perquè continui
                txtEmail = unicode("Això és un missatge automàtic. No cal que responeu.\n\n" +
                    "Hem rebut la teva sol·ŀicitud per introduir el teu currículum \n" +
                    "Fes clic en el següent enllaç per continuar: %s", 'utf-8')
                txt = txtEmail % (unicode(lnk))
                send_mail('[Es Liceu] Sol·licitud per enviar el currículum',
                    txt,
                    'curriculums@esliceu.com',
                    [cr.email],
                    fail_silently=False)

                return renderResponse(
                    request,
                    'curriculums/missatge.html', {
                    }
                )

            else:
                # DEBUG: Fem directament el redirect. En un entorn de producció,
                # S'ha d'enviar un email amb el link (controlar amb settings.CURR_SEND_EMAIL al settings.py principal)
                return redirect(lnk)
        else:
            raise Exception("ERROR!!" + str(f.errors))

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

@csrf_protect
def segonPas(request):
    codi = request.GET.get('codi')
    cr = Curriculum.objects.get(codi_edicio=codi)
    if not tooLate(cr):
        if cr.categoria == 'D':
            # Docent
            families = FamiliaTitol.objects.all().order_by('ordre_numeric')
            return renderResponse(
                request,
                'curriculums/segonpas.html', {
                    'cr': cr,
                    'tipus_curr': 'D',
                    'families': families,
            } )
        elif cr.categoria == 'N':
            # No docent
            catlaborals = CategoriaLaboralND.objects.all()
            return renderResponse(
                request,
                'curriculums/segonpas_nd.html', {
                    'cr': cr,
                    'tipus_curr': 'N',
                    'catlaborals': catlaborals,
                }
            )

    # TODO: Mostrar errors
    raise Exception("ERROR")


def file_is_valid(content):
    content_type = content.content_type.split('/')[0]
    # Falta comprovar el content_type, però s'han de fer experiments perquè
    # alguns navegadors no ho fan standard...
    if content._size > int(MAX_UPLOAD_SIZE):
        return False

    return True


@csrf_protect
def processar_candidat(request, cr, f):
    if f.is_valid():
        dta = f.cleaned_data
        cr.nom = dta['nom']
        cr.llinatges = dta['llinatges']
        cr.poblacio = dta['pob']
        cr.telefon = dta['tel']

        cr.ref1 = dta['ref1']
        cr.ref1_email = dta['ref1_email']
        cr.ref2 = dta['ref2']
        cr.ref2_email = dta['ref2_email']
        cr.ref3 = dta['ref3']
        cr.ref3_email = dta['ref3_email']

        if cr.categoria == 'D':
            cr.titol1_generic = dta['titol1']
            cr.titol1_nom = dta['tit1']
            cr.titol1_uni = dta['uni1']
            cr.titol1_data = dta['dta1']

            cr.titol2_generic = dta['titol2']
            cr.titol2_nom = dta['tit2']
            cr.titol2_uni = dta['uni2']
            cr.titol2_data = dta['dta2']

            cr.titol3_generic = dta['titol3']
            cr.titol3_nom = dta['tit3']
            cr.titol3_uni = dta['uni3']
            cr.titol3_data = dta['dta3']
        elif cr.categoria == 'N':
            cr.categoria_laboral_nodocent = dta['catlaboral']
        else:
            raise Exception("Error en categoria")

        file = dta['currfile']

        if file is None:
            if not cr.file:
                # ERROR: No tenim fitxer del currículum i tampoc ens ho proporcionen al formulari
                raise Exception("Fitxer requerit")

        else:
            # Ens proporcionen fitxer al formulari.
            # Comprovem que el fitxer és vàlid (grandària, mimetype...)
            if file_is_valid(file):
                if cr.file:
                    # Si ja en teníem, l'esborrem.
                    cr.file.delete()
                cr.file = file

            else:
                raise Exception("Fitxer no acceptat")

        # Enmmagatzemem l'objecte a la base de dades
        cr.valid = True
        cr.save()
        return renderResponse(
            request,
            'curriculums/final.html', {}
        )

    # TODO: Mostrar errors
    raise Exception("ERROR!!" + str(f.errors))


def final(request):
    if request.POST:
        codi = request.POST.get('codi_edicio')
        cr = Curriculum.objects.get(codi_edicio=codi)
        if not tooLate(cr):
            if cr.categoria == 'D':
                f = SegonPasForm_Docents(request.POST, request.FILES)
                return processar_candidat(request, cr, f)
            elif cr.categoria == 'N':
                f = SegonPasForm_NoDocents(request.POST, request.FILES)
                return processar_candidat(request, cr, f)

        else:
            raise Exception("Link no vàlid")

    # TODO: Mostrar errors
    raise Exception("Esperàvem POST")
