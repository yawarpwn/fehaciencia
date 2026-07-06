import type { Component } from 'svelte';
import ShoppingCartIcon from '@lucide/svelte/icons/shopping-cart';
import TruckIcon from '@lucide/svelte/icons/truck';
import FileSignatureIcon from '@lucide/svelte/icons/file-signature';
import LandMarkIcon from '@lucide/svelte/icons/landmark';
import ImageOffIcon from '@lucide/svelte/icons/image-off';
import type { MultiDocType, SingleDocType } from './types';
import FileTextIcon from '@lucide/svelte/icons/file-text';

export const SINGLE_DOC_META: Record<
	SingleDocType,
	{ label: string; icon: Component; shortLabel: string }
> = {
	PURCHASE_ORDER: { label: 'Orden de compra', shortLabel: 'OC', icon: ShoppingCartIcon }
};

export const MULTI_DOC_META: Record<
	MultiDocType,
	{ label: string; icon: Component; shortLabel: string }
> = {
	PHOTO: { label: 'Guía de remisión', shortLabel: 'FT', icon: ImageOffIcon },
	AGENCY_GUIDE: { label: 'Guía de agencia', shortLabel: 'GA', icon: TruckIcon },
	DELIVERY_GUIDE_SIGNED: { label: 'Guía firmada', shortLabel: 'GF', icon: FileSignatureIcon },
	PAYMENT_VOUCHER: { label: 'Voucher de pago', shortLabel: 'DP', icon: LandMarkIcon },
	DELIVERY_GUIDE: { label: 'Guía de remisión', shortLabel: 'GR', icon: FileTextIcon }
};

// Orden fijo en que se muestran las columnas de documentos únicos
export const SINGLE_DOC_ORDER: SingleDocType[] = ['PURCHASE_ORDER'];

export const MULTI_DOC_ORDER: MultiDocType[] = [
	'AGENCY_GUIDE',
	'DELIVERY_GUIDE',
	'DELIVERY_GUIDE_SIGNED',
	'PAYMENT_VOUCHER',
	'PHOTO'
];

// Documentos múltiples (0..N por factura) → columna de miniaturas
