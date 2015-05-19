# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns('',

	# URLS FRONT-END
	(r'^$', 'curriculums.views_frontend.primerPas', {}, 'curr-primerpas'),
	(r'^next$', 'curriculums.views_frontend.segonPas'),
	(r'^final$', 'curriculums.views_frontend.final'),
	(r'^delete$', 'curriculums.views_frontend.eliminaUsuari'),
	(r'^missatge$', 'curriculums.views_frontend.missatgeEliminat'),

	# URLS BACK-END
	(r'^backend/$', 'curriculums.views_backend.index'),
	(r'^backend/docents$', 'curriculums.views_backend.llista_docents'),
	(r'^backend/nodocents$', 'curriculums.views_backend.llista_nodocents'),
	(r'^backend/download/(\d+)$', 'curriculums.views_backend.download'),
	(r'^backend/show/(\d+)$', 'curriculums.views_backend.show'),
	(r'^backend/setPref/(\d+)/(y|n)$', 'curriculums.views_backend.setPreferit'),

)
