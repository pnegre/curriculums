# -*- coding: utf-8 -*-


from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

from django.contrib.auth.decorators import permission_required


from curriculums.models import Preferits, Curriculum


# Quan treiem les pàgines amb RequestContext, fem visibles a la template
# algunes variables que no estarien disponibles.
# Les altres funcions cridaran a aquesta en haver de fer el render de les templates
def renderResponse(request,tmpl,dic):
    return render_to_response(tmpl, dic, context_instance=RequestContext(request))


# Afegeix l'atribut "preferit" a l'objecte Currículum,
# si el currículum és dins la taula Preferits per aquest usuari
def getCurrPref(cr, user):
    try:
        Preferits.objects.get(usuari=user, curriculum=cr)
        cr.preferit = True
    except Preferits.DoesNotExist:
        cr.preferit = False

    return cr

# Funció molt simple que elimina els caràcters no ascii
def removeUTF(text):
    return ''.join([i if ord(i) < 128 else '_' for i in text])


# Vista dels currículums (tots)
@permission_required('curriculums.veure_curriculums_docents')
def index(request):
    crs = Curriculum.objects.filter(valid=True)
    return renderResponse(
        request,
        'curriculums/backend/llista.html', {
            'curriculums': crs,
        }
    )

# Vista dels currículums preferits per l'usuari que s'ha autenticat
@permission_required('curriculums.veure_curriculums_docents')
def showPreferits(request):
    crs = [ p.curriculum for p in Preferits.objects.filter(usuari=request.user) ]
    return renderResponse(
        request,
        'curriculums/backend/llista.html', {
            'curriculums': crs,
        }
    )

# Funció que es crida quan es vol baixar el fitxer d'un currículum
@permission_required('curriculums.veure_curriculums_docents')
def download(request, idc):
    # No emprem la variable request en aquesta funció
    del request
    cr = Curriculum.objects.get(id=idc)
    # Passem els caràcters del fitxer a ascii
    filename = cr.file.name.split('/')[-1]
    filename = removeUTF(filename)

    # Content/type????
    response = HttpResponse(cr.file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


# Mostra un currículum, afegeix l'atribut "preferit" per poder
# inicialitzar la checkbox de preferit.
@permission_required('curriculums.veure_curriculums_docents')
def show(request, idc):
    cr = Curriculum.objects.get(id=idc)
    cr = getCurrPref(cr, request.user)
    return renderResponse(
        request,
        'curriculums/backend/curriculum.html', {
            'cr': cr,
        }
    )

# AJAX (de fet és un GET) que es crida per javascript per posar un currículum
# dins preferits per l'usuari autenticat
# TODO: errors
@permission_required('curriculums.veure_curriculums_docents')
def setPreferit(request, idc, yn):
    cr = Curriculum.objects.get(id=idc)
    if yn == 'y':
        try:
            p = Preferits.objects.get(curriculum=cr, usuari=request.user)
        except Preferits.DoesNotExist:
            p = Preferits(curriculum=cr, usuari=request.user)
            p.save()
    else:
        try:
            p = Preferits.objects.get(curriculum=cr, usuari=request.user)
            p.delete()
        except Preferits.DoesNotExist:
            pass

    return HttpResponse()
