# -*- coding: utf-8 -*-

import hashlib, datetime, random

from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template import RequestContext
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django import forms

from curriculums.models import Curriculum, TitolGeneric, CategoriaLaboralND, FamiliaTitol

MAX_UPLOAD_SIZE = "15242880"

# Quan treiem les pàgines amb RequestContext, fem visibles a la template
# algunes variables que no estarien disponibles.
# Les altres funcions cridaran a aquesta en haver de fer el render de les templates
def renderResponse(request,tmpl,dic):
    return render_to_response(tmpl, dic, context_instance=RequestContext(request))

# Mostra missatge d'error/warning
def showMsg(request, m1, m2, errors=None):
    return renderResponse(
        request,
        'curriculums/missatge.html', {
            'miss_title': m1,
            'miss_body': m2,
            'errors': errors,
        }
    )

# Formulari django per primera pantalla
class PrimerPasForm(forms.Form):
    email = forms.CharField(validators=[validate_email])
    feina = forms.ChoiceField([('D', 'Docent'), ('N', 'No Docent')])

# Formulari django per segona pantalla (docents)
class SegonPasForm_Docents(forms.Form):
    nom = forms.CharField(max_length=200)
    llinatges = forms.CharField(max_length=200)
    codi_edicio = forms.CharField(max_length=200)
    tel = forms.CharField(max_length=200)
    pob = forms.CharField(max_length=200)

    titol1 = forms.ModelChoiceField(queryset=TitolGeneric.objects.all())
    tit1 = forms.CharField(max_length=200)
    uni1 = forms.CharField(max_length=200)
    dta1 = forms.DateField()
    titol2 = forms.ModelChoiceField(queryset=TitolGeneric.objects.all(), required=False)
    tit2 = forms.CharField(required=False, max_length=200)
    uni2 = forms.CharField(required=False, max_length=200)
    dta2 = forms.DateField(required=False)
    titol3 = forms.ModelChoiceField(queryset=TitolGeneric.objects.all(), required=False)
    tit3 = forms.CharField(required=False, max_length=200)
    uni3 = forms.CharField(required=False, max_length=200)
    dta3 = forms.DateField(required=False)

    ref1 = forms.CharField(required=False, max_length=200)
    ref1_email = forms.CharField(required=False, validators=[validate_email])
    ref2 = forms.CharField(required=False, max_length=200)
    ref2_email = forms.CharField(required=False, validators=[validate_email])
    ref3 = forms.CharField(required=False, max_length=200)
    ref3_email = forms.CharField(required=False, validators=[validate_email])

    currfile = forms.FileField(required=False)

    # Custom clean: detectarem si els títols tenen informació parcial...
    def clean(self):
        cleaned_data = super(SegonPasForm_Docents, self).clean()

        titol2, tit2, uni2, dta2 = cleaned_data.get('titol2'), cleaned_data.get('tit2'), \
            cleaned_data.get('uni2'), cleaned_data.get('dta2')
        if (titol2 or tit2 or uni2 or dta2) and not (titol2 and tit2 and uni2 and dta2):
            raise forms.ValidationError("Necessitem tots els camps de títol2")

        titol3, tit3, uni3, dta3 = cleaned_data.get('titol3'), cleaned_data.get('tit3'), \
            cleaned_data.get('uni3'), cleaned_data.get('dta3')
        if (titol3 or tit3 or uni3 or dta3) and not (titol3 and tit3 and uni3 and dta3):
            raise forms.ValidationError("Necessitem tots els camps de títol3")

        return cleaned_data

# Formulari django per segona pantalla (docents)
class SegonPasForm_NoDocents(forms.Form):
    nom = forms.CharField(max_length=200)
    llinatges = forms.CharField(max_length=200)
    codi_edicio = forms.CharField(max_length=200)
    tel = forms.CharField(max_length=200)
    pob = forms.CharField(max_length=200)

    catlaboral = forms.ModelMultipleChoiceField(queryset=CategoriaLaboralND.objects.all())

    ref1 = forms.CharField(required=False, max_length=200)
    ref1_email = forms.CharField(required=False, validators=[validate_email])
    ref2 = forms.CharField(required=False, max_length=200)
    ref2_email = forms.CharField(required=False, validators=[validate_email])
    ref3 = forms.CharField(required=False, max_length=200)
    ref3_email = forms.CharField(required=False, validators=[validate_email])

    currfile = forms.FileField(required=False)

# Genera codi sha512 a partir de la data, email i cadena aleatòria (per link temporal)
def generarCodi(email):
    # Generem codi a partir de l'hora actual, mirant els microseconds...
    codi_sha = hashlib.sha512()
    random_string = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz1234567890?¿;:_<>") for i in range(200))
    codi_sha.update(random_string)
    codi_sha.update(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    codi_sha.update(email)
    return codi_sha.hexdigest()

# Vista de la primera pantalla (es demana email i tipus de feina)
@csrf_protect
def primerPas(request):
    if request.POST:
        f = PrimerPasForm(request.POST)
        if f.is_valid():
            email = f.cleaned_data['email']
            feina = f.cleaned_data['feina']
            codi = generarCodi(email)

            # Agafem l'objecte "curriculum" amb l'email que ens han proporcionat
            # des de la BBDD. Si no existeix, el creem.
            cr = None
            try:
                cr = Curriculum.objects.get(email=email,categoria=feina)
            except Curriculum.DoesNotExist:
                cr = Curriculum(email=email, categoria=feina, codi_edicio=codi)

            cr.data_inicial = datetime.datetime.now()
            cr.codi_edicio = codi
            cr.codi_data = datetime.datetime.now()
            cr.save()

            lnk = "%s/curriculums/next?codi=%s" % (settings.CURR_SERVER, codi)

            if settings.CURR_SEND_EMAIL:
                # Enviem un email i mostrem un missatge a l'usuari perquè continui
                txtEmail = unicode("Això és un missatge automàtic. No cal que responeu.\n\n" +
                    "Hem rebut la seva sol·ŀicitud per introduir el currículum. \n\n" +
                    "Li hem enviat un enllaç perquè pugui completar el procés d'inscripció a la borsa de currículums. " +
                    "Aquest enllaç només serà vàlid durant 24 hores.\n\n" +
                    "Feu clic en el següent enllaç per continuar: %s", 'utf-8')
                txt = txtEmail % (unicode(lnk))
                send_mail('[Es Liceu] Sol·licitud per enviar el currículum',
                    txt,
                    'curriculums@esliceu.com',
                    [cr.email],
                    fail_silently=False)

                return showMsg(request,
                    'Hem enregistrat la seva petició. Consulti el seu correu electrònic per a continuar.',
                    "Si no veu el missatge que li hem enviat, consulti la carpeta de correu brossa (SPAM). "
                )

            else:
                # DEBUG: Fem directament el redirect. En un entorn de producció,
                # S'ha d'enviar un email amb el link (controlar amb settings.CURR_SEND_EMAIL al settings.py principal)
                return redirect(lnk)

        else:
            return showMsg(request, "Error!", "Camps requerits")
            # raise Exception("ERROR!" + str(f.errors))

    return renderResponse(
        request,
        'curriculums/index.html', {
    } )

# Comprovem que no fa més de 1 dia que hem demanat el link
def tooLate(cr):
    delta_seconds = (datetime.datetime.now() - cr.codi_data).seconds
    if delta_seconds > 3600*24:
        return True
    return False

# Vista de la segona pantalla (es demana la resta de dades al candidat)
@csrf_protect
def segonPas(request):
    try:
        codi = request.GET.get('codi')
        cr = Curriculum.objects.get(codi_edicio=codi)
    except:
        return showMsg(request, "ERROR", "El link no és vàlid")

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
                'curriculums/segonpas.html', {
                    'cr': cr,
                    'tipus_curr': 'N',
                    'catlaborals': catlaborals,
                }
            )
        else:
            return showMsg(request, "ERROR", "Error en la categoria")
    else:
        showMsg(request, "ERROR", "L'enllaç ha caducat")


# Procediment que mira si el fitxer que l'aspirant ha pujat és vàlid
# (es comprova grandària, mime...)
def file_is_valid(content):
    # content_type = content.content_type.split('/')[0]
    # Falta comprovar el content_type, però s'han de fer experiments perquè
    # alguns navegadors no ho fan standard...
    if content._size > int(MAX_UPLOAD_SIZE):
        return False

    return True

# Processem candidat
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
            return showMsg(request, "ERROR", "Error en la categoria")

        fle = dta['currfile']

        if fle is None:
            if not cr.file:
                # ERROR: No tenim fitxer del currículum i tampoc ens ho proporcionen al formulari
                return showMsg(request, "ERROR", "Fitxer requerit")

        else:
            # Ens proporcionen fitxer al formulari.
            # Comprovem que el fitxer és vàlid (grandària, mimetype...)
            if file_is_valid(fle):
                if cr.file:
                    # Si ja en teníem, l'esborrem.
                    cr.file.delete()
                cr.file = fle

            else:
                return showMsg(request, "ERROR", "Fitxer no acceptat")

        # Enmmagatzemem l'objecte a la base de dades
        cr.valid = True
        cr.save()
        return renderResponse(
            request,
            'curriculums/missatge.html', {
                'miss_title': 'Sol·licitud Acceptada',
                'miss_body': 'Hem rebut el seu currículum correctament. Podeu modificar o esborrar el vostre currículum tornant a realitzar el procés.'
            }
        )

    return showMsg(request, "ERROR", "Error en l'enviament del formulari. Revisa la informació introduïda.", f.errors)
    # raise Exception("ERROR!!" + str(f.errors))

# Es crida al final, quan es fa el POST amb les dades definitives
# de l'aspirant
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
            return showMsg(request, "ERROR", "L'enllaç ha expirat")

    return showMsg(request, "ERROR", "Error inesperat en processar el formulari.")

# Eliminem usuari, es crida quan l'aspirant vol eliminar les seves dades
# del nostre sistema
def eliminaUsuari(request):
    # Quan eliminem un currículum, django s'encarrega d'eliminar també els objectes
    # d'altres taules que en fan referència (per exemple, a la taula Preferits).
    # No fa falta que ens ocupem...
    if request.POST:
        codi = request.POST.get('codi_edicio')
        print codi
        cr = Curriculum.objects.get(codi_edicio=codi)
        if not tooLate(cr):
            if cr.file:
                # Esborrem l'arxiu si existeix
                cr.file.delete()
            cr.delete()
            return HttpResponse("Eliminat")

    # No ha anat bé l'eliminació
    raise Exception("Error eliminant l'usuari. No hauria de passar...")

# Vista molt simple que es limita a mostrar un missatge perquè l'aspirant
# vegi que les seves dades s'han eliminades del servidor
def missatgeEliminat(request):
    return renderResponse(
        request,
        'curriculums/missatge.html', {
            'miss_title': 'Dades eliminades',
            'miss_body': 'Les teves dades s\'han eliminat del nostre servidor',
        }
    )
