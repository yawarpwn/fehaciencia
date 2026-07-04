import type { SaleInvoice } from '$lib/types';
import { mockInvoices } from '@/mock-invoices';

const ellipsisName = (name: string) => {
	return name.length > 30 ? name.slice(0, 30) + '...' : name;
};

//responde from api
/*{
    "period": "202601",
    "serie": "E001",
    "number": 1341,
    "issue_date": "2026-01-08",
    "customer_ruc": "20569270422",
    "customer_name": "GRUPO GEM SOLUCIONES INTEGRALES S.A.C.",
    "currency": "PEN",
    "total_amount": 2520,
    "local_path": "202601/VENTAS/E001-1341",
    "status": "ACTIVE",
    "documents": [
      {
        "id": "f8b6dabf-e90d-423f-ac0d-81643ddc4c7c",
        "document_type": "INVOICE_ZIP",
        "file_name": "FACTURAE001-134120610555536.zip",
        "uploaded_at": "2026-06-29 19:40:15"
      },
      {
        "id": "ead64cb6-f214-484d-8066-58ddcbb44153",
        "document_type": "INVOICE_PDF",
        "file_name": "PDF-DOC-E001-134120610555536.pdf",
        "uploaded_at": "2026-06-29 19:40:15"
      },
      {
        "id": "3fce9db1-b33a-4dbd-ba41-009229835c67",
        "document_type": "DELIVERY_GUIDE_PDF",
        "file_name": "20610555536-09-EG07-728.pdf",
        "uploaded_at": "2026-06-29 19:40:15"
      },
      {
        "id": "ccddac65-e7ea-4ce2-a887-c7fa2ac4d196",
        "document_type": "DELIVERY_GUIDE_XML",
        "file_name": "20610555536-09-EG07-728.xml",
        "uploaded_at": "2026-06-29 19:40:15"
      }
    ],
}
*/

async function fetchInvoices(): Promise<SaleInvoice[]> {
	const res = await fetch('http://localhost:8000/sales-invoices');
	const data = await res.json();

	const sorted = data.reverse();

	const mappedInvoices = sorted.map((invoice: any) => {
		return {
			id: invoice.id,
			amount: invoice.amount,
			status: invoice.status,
			customerRuc: invoice.customer_ruc,
			customerName: invoice.customer_name,
			customerShortName: ellipsisName(invoice.customer_name),
			number: invoice.number,
			serie: invoice.serie,
			totalAmount: invoice.total_amount,
			issueDate: invoice.issue_date,
			documents: invoice.documents.map((doc: any) => ({
				id: doc.id,
				documentType: doc.document_type,
				fileName: doc.file_name,
				uploadedAt: doc.uploaded_at
			})),
			missingDocuments: invoice.missing_documents ?? [],
			isComplete: invoice.is_complete ?? invoice.documents.length > 0
		};
	});

	return mappedInvoices;
}
export async function load() {
	// logic to fetch payments data here
	return {
		invoices: mockInvoices
	};
}
