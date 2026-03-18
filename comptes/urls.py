from django.urls import path
from .views import releve_compte,releve_compte_pdf


urlpatterns = [
    path("releve/<int:compte_id>/", releve_compte, name="releve_compte"),
    path(
        "releve/<int:compte_id>/pdf/",
        releve_compte_pdf,
        name="releve_compte_pdf",
    ),
]

 



