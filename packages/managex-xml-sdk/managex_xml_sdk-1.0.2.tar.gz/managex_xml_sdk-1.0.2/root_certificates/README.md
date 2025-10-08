# Root Certificates Folder Structure

This folder contains trusted root and intermediate CA certificates organized by CA provider.

## Folder Structure:

```
root_certificates/
├── CCA_India/           # CCA India certificates
├── Capricorn/          # Capricorn CA certificates
├── eMudhra/            # eMudhra certificates
├── NSDL/               # NSDL certificates
├── Sify/               # Sify certificates
└── README.md           # This file
```

## Capricorn CA Certificate Chain:

Based on your certificate chain, you need to add these certificates to `Capricorn/` folder:

### Required Certificates for Capricorn:

1. **CCA India 2022.pem** ✅ (Already added to CCA_India/)
2. **Capricorn CA 2022.pem** ❌ (Add this to Capricorn/)
3. **Capricorn Sub CA for Individual DSC 2022.pem** ❌ (Add this to Capricorn/)
4. **Capricorn Sub CA for Organization DSC 2022.pem** ❌ (Add this to Capricorn/)
5. **Capricorn Sub CA for Document Signer DSC 2022.pem** ❌ (Add this to Capricorn/)

## Certificate Chain Flow:

```
CCA India 2022 (Root CA)
    ↓
Capricorn CA 2022 (Intermediate CA)
    ↓
Capricorn Sub CA for Individual DSC 2022 (Sub CA)
    ↓
Your Certificate (Aniket Chaturvedi)
```

## How to Add Certificates:

1. Download certificates from Capricorn website
2. Convert to .pem format if needed
3. Add to appropriate CA folder:
   - `Capricorn/Capricorn CA 2022.pem`
   - `Capricorn/Capricorn Sub CA Individual 2022.pem`
   - `Capricorn/Capricorn Sub CA Organization 2022.pem`
   - `Capricorn/Capricorn Sub CA Document Signer 2022.pem`

## Future CA Support:

To add support for other CAs:
1. Create new folder: `root_certificates/NewCA/`
2. Add root and intermediate certificates
3. Script will automatically load all .pem files recursively

## Testing:

After adding certificates, test with:
```bash
python imb.py --use-hsm --cn "Aniket" --file "test.xml"
```

The script will show which certificates are loaded from each CA folder.