# FenixTrace Odoo Connector

Odoo module that registers products on the **IOTA L1** blockchain via the FenixTrace Integration Kit.
Click a button on any product, and it gets uploaded to IPFS, registered on-chain, and notarized — all automatically.

> Built by [Fenix Software Labs](https://www.fenixsoftwarelabs.com)

---

## How It Works

```
Odoo Product → JSON file → Integration Kit → IPFS + IOTA L1 → FenixTrace Scanner
```

1. User clicks **"Send to FenixTrace"** on a product (or batch selects multiple)
2. Module builds a JSON payload with product data
3. Writes the JSON to the Integration Kit's `uploads/` folder
4. Calls the Integration Kit REST API to process the file
5. Kit uploads to IPFS, registers on blockchain, notarizes
6. TX hashes are saved back on the Odoo product record

---

## Requirements

| Requirement | Details |
|---|---|
| **Odoo** | 16.0 or 17.0 (Community or Enterprise) |
| **Integration Kit** | [FenixTrace Integration Kit](https://github.com/SantoBaldassarre/FenixTrace-IOTA-auto-add-product-Integration-Kit) running and configured |
| **FenixTrace Subscription** | Active plan on [trace.fenixsoftwarelabs.com](https://trace.fenixsoftwarelabs.com) |
| **Shared Filesystem** | Odoo server must be able to write to the Integration Kit's `uploads/` directory |

---

## Installation

1. Copy the `fenixtrace_odoo_connector` folder into your Odoo addons path:

```bash
cp -r fenixtrace_odoo_connector /opt/odoo/addons/
```

2. Restart Odoo:

```bash
sudo systemctl restart odoo
```

3. In Odoo, go to **Apps** → **Update Apps List** → Search for **"FenixTrace"** → **Install**

---

## Configuration

Go to **Settings** → **General Settings** → scroll to **FenixTrace Integration**:

| Setting | Description | Example |
|---|---|---|
| **Upload Directory** | Path to the Integration Kit's `uploads/` folder | `/opt/fenixtrace-kit/uploads` |
| **Integration Kit URL** | URL where the Integration Kit is running | `http://localhost:3005` |

> Both must be configured before you can send products.

---

## Usage

### Single Product

1. Open any product in **Inventory** → **Products**
2. Click **"Send to FenixTrace"** in the header
3. Check the **FenixTrace** tab for TX hashes and status

### Batch Sync

1. Go to the **Products** list view
2. Select multiple products with checkboxes
3. Click **Action** → **"Send to FenixTrace (Batch)"**

### Auto-Sync (Cron)

A scheduled action runs **every hour** and automatically syncs all products in `draft` or `error` state. You can adjust the frequency in **Settings** → **Technical** → **Scheduled Actions** → **"FenixTrace: Auto-sync Products"**.

### Retry Failed Products

If a product sync fails (state = `error`), a **"Retry FenixTrace"** button appears in the header. Click it to reset and retry.

---

## Product Fields

The module adds these fields to each product (visible in the **FenixTrace** tab):

| Field | Description |
|---|---|
| **State** | `draft` → `queued` → `synced` / `error` |
| **Last Sync** | Timestamp of last successful sync |
| **Product Tx Hash** | IOTA blockchain transaction hash |
| **Notarization Tx Hash** | Notarization transaction hash |
| **Last File** | JSON filename sent to the Integration Kit |
| **Last Error** | Error message if sync failed |

---

## JSON Payload

Each product generates a JSON like this:

```json
{
  "name": "Olive Oil Extra Virgin",
  "description": "Cold-pressed organic olive oil",
  "category": "Food",
  "manufacturer": "My Company",
  "defaultCode": "OIL-001",
  "barcode": "8012345678901",
  "listPrice": 12.50,
  "standardPrice": 8.00,
  "currency": "EUR",
  "createdAt": "2026-03-22T10:30:00Z",
  "source": "odoo_plugin",
  "odoo": {
    "productTemplateId": 42,
    "productName": "Olive Oil Extra Virgin",
    "companyId": 1,
    "companyName": "My Company SRL"
  }
}
```

---

## Troubleshooting

### "Upload directory does not exist"
Create the directory and ensure Odoo has write access:
```bash
sudo mkdir -p /opt/fenixtrace-kit/uploads
sudo chown odoo:odoo /opt/fenixtrace-kit/uploads
```

### "Cannot reach Integration Kit URL"
Verify the Kit is running:
```bash
curl http://localhost:3005/status
```

### "FenixTrace processing failed"
Check the Integration Kit logs:
```bash
curl http://localhost:3005/logs
```

### Products stuck in "queued" state
The Integration Kit may have processed the file but the response wasn't received. Check the Kit's `/processed` endpoint and manually update the product state.

---

## Module Structure

```
fenixtrace_odoo_connector/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_template.py      # Product extension + sync logic
│   └── res_config_settings.py   # Configuration fields
├── views/
│   ├── product_template_views.xml   # Product form + FenixTrace tab
│   └── res_config_settings_views.xml  # Settings page
├── data/
│   ├── server_actions.xml       # Batch action for product list
│   └── ir_cron.xml              # Scheduled auto-sync (hourly)
└── security/
    └── ir.model.access.csv      # Access rights
```

---

## Links

- [FenixTrace Platform](https://trace.fenixsoftwarelabs.com)
- [FenixTrace Integration Kit](https://github.com/SantoBaldassarre/FenixTrace-IOTA-auto-add-product-Integration-Kit)
- [FenixTrace API Docs](https://trace.fenixsoftwarelabs.com/docs/api)
- [FenixTrace Scanner](https://trace.fenixsoftwarelabs.com/scanner)
- [Fenix Software Labs](https://www.fenixsoftwarelabs.com)

---

## License

LGPL-3 — [Fenix Software Labs](https://www.fenixsoftwarelabs.com)
