// src/lib/types.ts

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

export type InvoiceDocument = {
	id: string;
	documentType: DocumentType;
	fileName: string;
	uploadedAt: string;
	fileUrl: string;
	thumbnailUrl?: string; // fotos → miniatura real; vouchers → null (muestra icono PDF)
};

export type SaleInvoice = {
	id: string;
	invoiceId: string; // "E001-1341" — armado en el backend
	period: string; // "202601"
	status: InvoiceStatus;
	customerRuc: string;
	customerName: string;
	customerShortName: string;
	totalAmount: number;
	creditNote: InvoiceDocument | null;
	isAdvance: boolean;
	isAgencyShipment: boolean;
	isVoided: boolean;

	// Documentos únicos
	pdfFile: InvoiceDocument;
	purchaseOrder: InvoiceDocument | null;
	deliveryGuides: InvoiceDocument[];
	agencyGuides: InvoiceDocument[];
	signedDeliveryGuides: InvoiceDocument[];

	// Documentos múltiples
	photos: InvoiceDocument[];
	vouchers: InvoiceDocument[];

	// Calculado en el backend
	isComplete: boolean;
	missing: string[]; // ej. ["Guía firmada", "Voucher de pago"] — listo para mostrar al usuario
};
