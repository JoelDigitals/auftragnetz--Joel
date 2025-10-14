# compile_po.py
import os
import polib

# Sprachen definieren (hier Deutsch, Englisch, Französisch)
locales = ['de', 'en', 'fr']

# Basisverzeichnis, in dem dein "locale"-Ordner liegt
base_path = os.path.join(os.path.dirname(__file__), 'locale')

for lang in locales:
    po_path = os.path.join(base_path, lang, 'LC_MESSAGES', 'django.po')
    mo_path = os.path.join(base_path, lang, 'LC_MESSAGES', 'django.mo')

    if not os.path.exists(po_path):
        print(f"⚠️  Übersetzungsdatei fehlt: {po_path}")
        continue

    try:
        po = polib.pofile(po_path)
        po.save_as_mofile(mo_path)
        print(f"✅ Kompiliert: {po_path} → {mo_path}")
    except Exception as e:
        print(f"❌ Fehler beim Kompilieren von {lang}: {e}")

print("\nFertig! Du kannst jetzt `django.mo` in Django verwenden.")
