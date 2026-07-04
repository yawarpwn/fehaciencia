import type { Component } from 'svelte';
import ShoppingCartIcon from '@lucide/svelte/icons/shopping-cart';
import TruckIcon from '@lucide/svelte/icons/truck';
import BuildingIcon from '@lucide/svelte/icons/building-2';
import FileSignatureIcon from '@lucide/svelte/icons/file-signature';
import type { MultiDocType, SingleDocType } from './types';

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
	PHOTO: { label: 'Guía de remisión', shortLabel: 'FT', icon: BuildingIcon },
	AGENCY_GUIDE: { label: 'Guía de agencia', shortLabel: 'GA', icon: TruckIcon },
	DELIVERY_GUIDE_SIGNED: { label: 'Guía firmada', shortLabel: 'GF', icon: FileSignatureIcon },
	PAYMENT_VOUCHER: { label: 'Voucher de pago', shortLabel: 'DP', icon: FileSignatureIcon },
	DELIVERY_GUIDE: { label: 'Guía de remisión', shortLabel: 'GR', icon: BuildingIcon }
};

// Orden fijo en que se muestran las columnas de documentos únicos
export const SINGLE_DOC_ORDER: SingleDocType[] = ['PURCHASE_ORDER'];

export const MULTI_DOC_ORDER: MultiDocType[] = [
	'PHOTO',
	'PAYMENT_VOUCHER',
	'DELIVERY_GUIDE',
	'AGENCY_GUIDE',
	'DELIVERY_GUIDE_SIGNED'
];
