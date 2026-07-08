# GROBÉ OS v3

Dit is een concrete basisversie van GROBÉ OS. De app draait als Flask-webapp en is geschikt voor Render.

## In deze versie

- Dashboard als controlekamer.
- Grafische IBC-weergave voor grondstoffen.
- Centrale JSON-database voor artikelen, producten, recepturen, leveranciers en mutaties.
- Voorraad van grondstoffen, verpakkingen, etiketten en dozen.
- Huidige Universol-receptuur met ECOSURF.
- Nieuwe Universol-receptuur na ECOSURF:
  - Water 867
  - BDG 36
  - Ampholak 29
  - KOH 10
  - Dissolvine 20
  - NL8P4 9
  - GA8W 9
  - NCS 20
- Kostprijs per receptuur, per liter en per product.
- Productmarge per verpakking.
- Factuur-upload blijft aanwezig: PDF uitlezen, legacy-artikelnummers herkennen, prijshistorie opslaan, voorraadmutatie klaarzetten voor goedkeuring.
- Voorraad wordt pas verhoogd na handmatige goedkeuring.

## Niet in deze versie

- Nog geen echte Dropbox-koppeling.
- Nog geen automatische koppeling met de bestaande Pakbon-app.
- Nog geen volledige gebruikers/login-module.
- PDF-uitlezing is basisherkenning. Voor Julius Hoesch, Superdoos en Distrifill moeten we daarna per factuurlay-out verder verfijnen.

## Lokaal draaien

```bash
pip install -r requirements.txt
python -m app.main
```

Daarna openen:

```text
http://127.0.0.1:5000
```

## Render

Deze ZIP bevat `render.yaml`. Upload de inhoud naar GitHub. Render kan daarna automatisch deployen.
