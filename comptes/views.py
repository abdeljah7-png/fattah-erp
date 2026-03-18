from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from reglements.models import MouvementCompte
from .models import Compte
from core.models import Societe

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def releve_compte(request, compte_id):

    compte = get_object_or_404(Compte, id=compte_id)
    societe = Societe.objects.first()

    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    mouvements = MouvementCompte.objects.filter(compte=compte)

    report = 0

    if date_debut:
        mouvements_avant = mouvements.filter(date__lt=date_debut)

        total_entrees_avant = sum(
            m.montant for m in mouvements_avant if m.type_mouvement == "entree"
        )

        total_sorties_avant = sum(
            m.montant for m in mouvements_avant if m.type_mouvement == "sortie"
        )

        report = total_entrees_avant - total_sorties_avant

    mouvements = mouvements.order_by("date")

    if date_debut:
        mouvements = mouvements.filter(date__gte=date_debut)

    if date_fin:
        mouvements = mouvements.filter(date__lte=date_fin)

    lignes = []

    total_debit = 0
    total_credit = 0

    solde = report

    for m in mouvements:

        if m.type_mouvement == "entree":
            debit = m.montant
            credit = 0
        else:
            debit = 0
            credit = m.montant

        total_debit += debit
        total_credit += credit

        solde = solde + debit - credit

#------ Remplir les lignes
#------------------------
        lignes.append({
            "date": m.date,
            "libelle": m.reference,
            "debit": debit,
            "credit": credit,
            "solde": solde
        })

    context = {
        "societe": societe,
        "compte": compte,
        "lignes": lignes,
        "report": report,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "solde": solde,
        "date_debut": date_debut,
        "date_fin": date_fin
    }

    return render(request, "comptes/releve_compte.html", context)

#----- Impression de releve en pdf

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm
from .models import Compte
from reglements.models import MouvementCompte
from core.models import Societe

def releve_compte_pdf(request, compte_id):
    compte = get_object_or_404(Compte, id=compte_id)
    societe = Societe.objects.first()

    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    mouvements = MouvementCompte.objects.filter(compte=compte).order_by("date")

    # --- CALCUL DU REPORT ---
    report = 0
    if date_debut:
        mouvements_avant = mouvements.filter(date__lt=date_debut)
        total_entrees_avant = sum(m.montant for m in mouvements_avant if m.type_mouvement == "entree")
        total_sorties_avant = sum(m.montant for m in mouvements_avant if m.type_mouvement == "sortie")
        report = total_entrees_avant - total_sorties_avant

    # Filtrer mouvements selon période
    if date_debut:
        mouvements = mouvements.filter(date__gte=date_debut)
    if date_fin:
        mouvements = mouvements.filter(date__lte=date_fin)

    # --- Création du PDF ---
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=releve_compte_{compte.id}.pdf"
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 2*cm

    # --- Entête société ---
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2*cm, y, societe.nom if societe else "Société")
    y -= 0.6*cm
    p.setFont("Helvetica", 10)
    if societe:
        p.drawString(2*cm, y, societe.adresse)
        y -= 0.4*cm
        p.drawString(2*cm, y, f"Tél: {societe.telephone} | Email: {societe.email}")
    y -= 1*cm

    # --- Report initial ---
    p.setFont("Helvetica-Bold", 11)
    p.drawString(2*cm, y, f"Report initial avant {date_debut if date_debut else 'le début'} : {report:.3f}")
    y -= 0.6*cm

    # --- Période ---
    periode_text = "Période : "
    if date_debut and date_fin:
        periode_text += f"{date_debut} au {date_fin}"
    elif date_debut:
        periode_text += f"à partir de {date_debut}"
    elif date_fin:
        periode_text += f"jusqu'à {date_fin}"
    else:
        periode_text += "tous les mouvements"
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, y, periode_text)
    y -= 0.8*cm

    # --- Préparer tableau ---
    data = [["Date", "Libellé", "Débit", "Crédit", "Solde"]]

    solde = report
    total_debit = 0
    total_credit = 0

    for m in mouvements:
        # Débit / Crédit
        debit = m.montant if m.type_mouvement == "entree" else 0
        credit = m.montant if m.type_mouvement == "sortie" else 0
        solde += debit - credit
        total_debit += debit
        total_credit += credit

        # --- Libellé corrigé ---
        if hasattr(m, "reglement_client") and m.reglement_client:
            libelle = f"Règlement Client RC n°{m.reglement_client.numero}"
        elif hasattr(m, "reglement_fournisseur") and m.reglement_fournisseur:
            libelle = f"Règlement Fournisseur RF n°{m.reglement_fournisseur.numero}"
        else:
            libelle = m.reference or f"MC n°{m.id}"

        data.append([
            str(m.date),
            libelle,
            f"{debit:.3f}" if debit else "",
            f"{credit:.3f}" if credit else "",
            f"{solde:.3f}"
        ])

    # Ajouter ligne totaux
    data.append(["Totaux", "", f"{total_debit:.3f}", f"{total_credit:.3f}", f"{solde:.3f}"])

    # --- Création du tableau avec styles ---
    table = Table(data, colWidths=[3*cm, 5*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (2,0), (-1,-1), "RIGHT"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
    ]))

    w, h = table.wrapOn(p, width-4*cm, y)
    table.drawOn(p, 2*cm, y-h)

    # --- Sauvegarder PDF ---
    p.showPage()
    p.save()
    return response