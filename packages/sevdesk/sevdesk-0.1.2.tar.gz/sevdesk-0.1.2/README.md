# sevDesk API Client (Inoffiziell)

Ein Python-Client für die sevDesk API, automatisch generiert aus der OpenAPI-Spezifikation. Dies ist notwendig, da sich die sevdesk-Spezifikation mit dem Standard OpenApi-Generator nicht parsen lässt.

## ⚠️ Wichtige Hinweise

- **Dies ist KEINE offizielle sevDesk Library**
- Ich arbeite nicht für sevDesk und bin nicht mit sevDesk verbunden
- **Nutzung auf eigene Gefahr**
- Keine Garantie für Funktionalität oder Vollständigkeit
- Bei Problemen mit Markenrechten oder dem Library-Namen kontaktieren Sie mich bitte
- Falls sich offizielle Vertreter von sevDesk am Namen der Library stören, bin ich bereit, diesen zu übertragen oder die Library unter einem anderen Namen zu veröffentlichen

## Installation

```bash
pip install sevdesk
```

## Anforderungen

- Python 3.8+
- pydantic
- requests
- pyyaml
- jinja2

## Verwendung

### Client initialisieren

```python
from sevdesk import Client

# API Token von sevDesk Dashboard holen
client = Client('your-api-token-here')
```

### Kontakte abrufen

```python
# Alle Kontakte abrufen
contacts = client.contact.getContacts()

for contact in contacts:
    print(f"ID: {contact.id_}")
    print(f"Name: {contact.name or f'{contact.surename} {contact.familyname}'}")
    print(f"Kundennummer: {contact.customerNumber}")
    print(f"Status: {contact.status}")
    print("-" * 40)
```

### Neuen Kontakt erstellen

```python
from sevdesk.models.contact import Contact
from sevdesk.converters.category import Category

# Organisation erstellen
company = Contact(
    name="Acme Corporation GmbH",
    category=Category(id_=3, objectName="Category")
)
new_company = client.contact.createContact(body=company)
print(f"Organisation erstellt mit ID: {new_company.id_}")

# Person erstellen
person = Contact(
    surename="Max",
    familyname="Mustermann",
    gender="m",
    category=Category(id_=3, objectName="Category")
)
new_person = client.contact.createContact(body=person)
print(f"Person erstellt mit ID: {new_person.id_}")
```

### Rechnungen abrufen

```python
# Alle Rechnungen abrufen
invoices = client.invoice.getInvoices()

for invoice in invoices:
    print(f"Rechnungsnummer: {invoice.invoiceNumber}")
    print(f"Datum: {invoice.invoiceDate}")
    print(f"Betrag: {invoice.sumGross} {invoice.currency}")
    print(f"Status: {invoice.status}")
    print("-" * 40)
```

### Angebote abrufen

```python
# Alle Angebote abrufen
orders = client.order.getOrders()

for order in orders:
    print(f"Angebotsnummer: {order.orderNumber}")
    print(f"Datum: {order.orderDate}")
    print(f"Betrag: {order.sumGross} {order.currency}")
    print(f"Status: {order.status}")
    print("-" * 40)
```

### Kontakt aktualisieren

```python
from sevdesk.models.contactupdate import ContactUpdate

# Kontakt aktualisieren
update_data = ContactUpdate(
    name="Neue Firma GmbH"
)
updated = client.contact.updateContact(contactId=123456, body=update_data)
print(f"Kontakt aktualisiert: {updated.name}")
```

### Kontakt löschen

```python
# Kontakt löschen
client.contact.deleteContact(contactId=123456)
print("Kontakt gelöscht")
```

## Verfügbare Controller

Der Client lädt automatisch alle verfügbaren Controller aus der OpenAPI-Spezifikation:

- `client.contact` - Kontaktverwaltung
- `client.invoice` - Rechnungsverwaltung
- `client.order` - Angebotsverwaltung
- `client.voucher` - Belegverwaltung
- `client.part` - Artikelverwaltung
- ... und viele mehr

Alle Endpoints sind als Methoden verfügbar und vollständig typisiert für IDE-Unterstützung.

## Code neu generieren

Falls sich die sevDesk API ändert:

```bash
# Neue openapi.yaml herunterladen
# Dann Generator ausführen:
python -m generator
```

Dies generiert automatisch:
- Models in `sevdeskapi/models/`
- Converter in `sevdeskapi/converters/`
- Controller in `sevdeskapi/controllers/`

Das wird zeitnah über Github Actions abgebildet!

## Lizenz  / Haftungsausschluss

MIT License - Siehe LICENSE Datei

