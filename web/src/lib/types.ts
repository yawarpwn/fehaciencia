// src/lib/types.ts
//
export type InvoiceDocument = {
	id: string;
	invoice_id: string;
	document_type: DocumentType;
	file_name: string;
	file_url: string;
	mime_type: string;
	file_size: number;
	thumbnail_url: string;
};

export interface SaleInvoice {
	id: string;
	document_id: string;
	period: string;
	customer_ruc: string;
	customer_name: string;
	currency: string;
	customer_short_name: string;
	total_amount: number;
	is_advance: boolean;
	issue_date: string;
	purchase_order: InvoiceDocument | null;
	agency_guides: InvoiceDocument[];
	signed_delivery_guides: InvoiceDocument[];
	payment_vouchers: InvoiceDocument[];
	delivery_notes: DeliveryNote[];
	credit_notes: CreditNote[];
	photos: InvoiceDocument[];
	pdf_file_url: string;
	zip_file_url: string;
	missing: string[]; // ej. ["Guía firmada", "Voucher de pago"] — listo para mostrar al usuario
	status: InvoiceStatus;
	payment_method: string;
}

export interface AgencyGuide {
	id: string;
	document_type: string;
	file_name: string;
	file_url: string;
	thumbnail_url: string;
}

export interface DeliveryNote {
	id: string;
	document_id: string;
	is_agency_shipment: boolean;
	issue_date: string;
	pdf_file_url: string;
	zip_file_url: string;
	xml_file_url: string;
	sales_invoices: SaleInvoice[];
}

export interface CreditNote {
	id: string;
	document_id: string;
	pdf_file_url: string;
	zip_file_url: string;
	xml_file_url: string;
}

// Documentos únicos (máx. 1 por factura) → columna de icono
export type SingleDocType = 'PURCHASE_ORDER'; // Orden de compra

// Documentos múltiples (0..N por factura) → columna de miniaturas
export type MultiDocType =
	| 'PHOTO'
	| 'PAYMENT_VOUCHER'
	| 'DELIVERY_GUIDE' // Guía de remisión
	| 'AGENCY_GUIDE' // Guía de agencia
	| 'DELIVERY_GUIDE_SIGNED'; // Guía firmada

export type InvoiceStatus = 'COMPLETE' | 'VOIDED' | 'INCOMPLETE' | 'ADVANCE';

export type DocumentType = SingleDocType | MultiDocType;
