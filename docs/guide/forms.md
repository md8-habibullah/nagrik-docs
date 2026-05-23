# Government Form Auto-fill\n\n## Supported Forms (Phase 1)

| Form | Type | Submission |
|---|---|---|
| সিভিক কমপ্লেইন ফর্ম | Civic report | In-app → PDF download |
| পুলিশ GD (General Diary) | Crime/incident | PDF → Print/Email |
| ইউটিলিটি কমপ্লেইন | DESCO/WASA/TITAS | PDF |
| RTI আবেদন | Right to Information | PDF |
| ভোক্তা অধিকার অভিযোগ | Consumer complaint | PDF |

---

## Form Auto-fill Flow

```
User speaks issue
      │
      ▼
AI extracts structured data
      │
      ▼
User selects: "কোন ফর্মে ফাইল করবেন?"
[GD] [Civic] [Utility] [RTI]
      │
      ▼
AI maps extracted data → form fields
      │
      ▼
Show form with pre-filled fields
      │
      ▼
User reviews + edits any field
      │
      ▼
[Generate PDF] → Download/Share/Print
```

---

## Form Field Mapping

```typescript
// Backend: Map AI extraction to specific form fields

router.post('/fill', async (req, res) => {
  const { formType, civicReport, userProfile } = req.body;

  const fieldMap = await openRouterService.mapToFormFields({
    formType,
    report: civicReport,
    user: userProfile,
  });

  res.json({ fields: fieldMap });
});

// Prompt for field mapping:
const FORM_MAPPING_PROMPT = (formType: string) => \`
Map the civic report data to form fields for: \${formType}

Police GD form fields:
- ১. বাদীর নাম ও পিতার নাম
- ২. বর্তমান ঠিকানা
- ৩. থানার নাম
- ৪. ঘটনার তারিখ ও সময়
- ৫. ঘটনাস্থল
- ৬. ঘটনার বিবরণ (বিস্তারিত)
- ৭. আসামির নাম (যদি জানা থাকে)
- ৮. সাক্ষীর নাম (যদি থাকে)
- ৯. প্রার্থিত ব্যবস্থা

Return JSON with each field filled from the report data.
Leave unknown fields empty string.
\`;
```

---

## PDF Generation (Flutter)

```dart
// lib/features/forms/services/pdf_generator.dart

import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

class PdfGenerator {

  Future<Uint8List> generateGDForm({
    required Map<String, String> fields,
    required String thanaName,
    required DateTime date,
  }) async {
    final pdf = pw.Document();

    // Load Bengali font (MUST for Unicode support)
    final banglaFont = await PdfGoogleFonts.notoSansBengaliRegular();
    final banglaFontBold = await PdfGoogleFonts.notoSansBengaliBold();

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        build: (context) => pw.Column(
          crossAxisAlignment: pw.CrossAxisAlignment.start,
          children: [
            // Header
            pw.Center(
              child: pw.Text(
                'সাধারণ ডায়েরি (জিডি)',
                style: pw.TextStyle(
                  font: banglaFontBold,
                  fontSize: 18,
                ),
              ),
            ),
            pw.SizedBox(height: 8),
            pw.Center(
              child: pw.Text(
                '\$thanaName থানা, ঢাকা',
                style: pw.TextStyle(font: banglaFont, fontSize: 14),
              ),
            ),
            pw.Divider(),
            pw.SizedBox(height: 12),

            // Date
            pw.Text(
              'তারিখ: \${DateFormat('dd/MM/yyyy', 'bn').format(date)}',
              style: pw.TextStyle(font: banglaFont, fontSize: 12),
            ),
            pw.SizedBox(height: 16),

            // Form fields
            _buildFormField('বাদীর নাম', fields['name'] ?? '', banglaFont, banglaFontBold),
            _buildFormField('পিতার নাম', fields['father_name'] ?? '', banglaFont, banglaFontBold),
            _buildFormField('ঠিকানা', fields['address'] ?? '', banglaFont, banglaFontBold),
            _buildFormField('ঘটনার বিবরণ', fields['description'] ?? '', banglaFont, banglaFontBold, maxLines: 8),

            pw.SizedBox(height: 30),

            // Signature
            pw.Row(
              mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
              children: [
                pw.Text('দারোগার স্বাক্ষর', style: pw.TextStyle(font: banglaFont)),
                pw.Text('বাদীর স্বাক্ষর', style: pw.TextStyle(font: banglaFont)),
              ],
            ),
          ],
        ),
      ),
    );

    return pdf.save();
  }

  pw.Widget _buildFormField(String label, String value,
    pw.Font regular, pw.Font bold, {int maxLines = 1}) {

    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(label, style: pw.TextStyle(font: bold, fontSize: 11)),
        pw.Container(
          width: double.infinity,
          padding: const pw.EdgeInsets.all(6),
          decoration: pw.BoxDecoration(
            border: pw.Border.all(color: PdfColors.grey400),
            borderRadius: const pw.BorderRadius.all(pw.Radius.circular(4)),
          ),
          child: pw.Text(
            value.isEmpty ? ' ' : value,
            style: pw.TextStyle(font: regular, fontSize: 11),
          ),
        ),
        pw.SizedBox(height: 10),
      ],
    );
  }
}
```\n\n