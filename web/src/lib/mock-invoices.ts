// src/lib/mock-invoices.ts
import type { SaleInvoice } from './types';

export const mockInvoices: SaleInvoice[] = [
	{
		id: '1',
		invoiceCode: 'E001-1341',
		period: '202601',
		status: 'ACTIVE',
		customerRuc: '20569270422',
		customerName: 'GRUPO GEM SOLUCIONES INTEGRALES S.A.C.',
		customerShortName: 'GRUPO GEM SOLUCIONES...',
		totalAmount: 2520,
		isAdvance: false,
		isCreditNote: false,

		purchaseOrder: {
			id: 'd1',
			documentType: 'PURCHASE_ORDER',
			fileName: 'OC-2026-001.pdf',
			uploadedAt: '2026-01-07 10:00',
			fileUrl: '/documents/d1/file'
		},
		deliveryGuides: [
			{
				id: 'd2',
				documentType: 'DELIVERY_GUIDE',
				fileName: 'guia-remision-1341.pdf',
				uploadedAt: '2026-01-08 09:00',
				fileUrl: '/documents/d2/file'
			},

			{
				id: 'd11',
				documentType: 'DELIVERY_GUIDE',
				fileName: 'guia-remision-1341.pdf',
				uploadedAt: '2026-01-08 09:00',
				fileUrl: '/documents/d2/file'
			}
		],
		agencyGuides: [
			{
				id: 'd3',
				documentType: 'AGENCY_GUIDE',
				fileName: 'guia-agencia-1341.pdf',
				uploadedAt: '2026-01-08 09:30',
				fileUrl: '/documents/d3/file'
			},
			{
				id: 'd10x',
				documentType: 'AGENCY_GUIDE',
				fileName: 'guia-agencia-1341.pdf',
				uploadedAt: '2026-01-08 09:30',
				fileUrl: '/documents/d3/file'
			}
		],
		signedDeliveryGuides: [],
		photos: [
			{
				id: 'd5',
				documentType: 'PHOTO',
				fileName: 'foto-1.jpg',
				uploadedAt: '2026-01-08 09:45',
				fileUrl: '/documents/d5/file',
				thumbnailUrl: 'https://picsum.photos/seed/d5/80/80'
			},
			{
				id: 'd6',
				documentType: 'PHOTO',
				fileName: 'foto-2.jpg',
				uploadedAt: '2026-01-08 09:46',
				fileUrl: '/documents/d6/file',
				thumbnailUrl: 'https://picsum.photos/seed/d6/80/80'
			},
			{
				id: 'd7',
				documentType: 'PHOTO',
				fileName: 'foto-3.jpg',
				uploadedAt: '2026-01-08 09:47',
				fileUrl: '/documents/d7/file',
				thumbnailUrl: 'https://picsum.photos/seed/d7/80/80'
			}
		],
		// Pago en 2 partes — vouchers sin miniatura real, solo PDF
		vouchers: [
			{
				id: 'd8',
				documentType: 'PAYMENT_VOUCHER',
				fileName: 'voucher-parte1.pdf',
				uploadedAt: '2026-01-08 12:00',
				fileUrl: '/documents/d8/file'
			},
			{
				id: 'd9',
				documentType: 'PAYMENT_VOUCHER',
				fileName: 'voucher-parte2.pdf',
				uploadedAt: '2026-01-10 16:30',
				fileUrl: '/documents/d9/file'
			}
		],
		isComplete: true,
		missing: []
	},
	{
		id: '2',
		invoiceCode: 'E001-1342',
		period: '202601',
		status: 'ACTIVE',
		customerRuc: '20100123456',
		customerName: 'COMERCIAL LOS ANDES E.I.R.L.',
		customerShortName: 'COMERCIAL LOS ANDES',
		totalAmount: 980.5,
		isAdvance: false,
		isCreditNote: false,

		purchaseOrder: null,
		deliveryGuides: [
			{
				id: 'd10',
				documentType: 'DELIVERY_GUIDE',
				fileName: 'guia-remision-1342.pdf',
				uploadedAt: '2026-01-09 10:00',
				fileUrl: '/documents/d10/file'
			}
		],
		agencyGuides: [],
		signedDeliveryGuides: [
			{
				id: 'd4',
				documentType: 'DELIVERY_GUIDE_SIGNED',
				fileName: 'guia-firmada-1341.pdf',
				uploadedAt: '2026-01-09 15:00',
				fileUrl: '/documents/d4/file'
			}
		],
		photos: [
			{
				id: 'd11',
				documentType: 'PHOTO',
				fileName: 'foto-entrega-1342.jpg',
				uploadedAt: '2026-01-09 11:00',
				fileUrl: '/documents/d11/file',
				thumbnailUrl: 'https://picsum.photos/seed/d11/80/80'
			}
		],
		vouchers: [],
		isComplete: false,
		missing: ['Orden de compra', 'Guía de agencia', 'Guía firmada', 'Voucher de pago']
	},
	{
		id: '3',
		invoiceCode: 'E001-1343',
		period: '202602',
		status: 'ACTIVE',
		customerRuc: '20458887412',
		customerName: 'DISTRIBUIDORA NORTE S.A.C.',
		customerShortName: 'DISTRIBUIDORA NORTE',
		totalAmount: 4150,
		isAdvance: false,
		isCreditNote: false,

		purchaseOrder: null,
		deliveryGuides: [],
		agencyGuides: [],
		signedDeliveryGuides: [],
		photos: [],
		vouchers: [],
		isComplete: false,
		missing: [
			'Orden de compra',
			'Guía de remisión',
			'Guía de agencia',
			'Guía firmada',
			'Fotos de entrega',
			'Voucher de pago'
		]
	}
];
