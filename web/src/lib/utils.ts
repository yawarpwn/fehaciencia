import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChild<T> = T extends { child?: any } ? Omit<T, 'child'> : T;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChildren<T> = T extends { children?: any } ? Omit<T, 'children'> : T;
export type WithoutChildrenOrChild<T> = WithoutChildren<WithoutChild<T>>;
export type WithElementRef<T, U extends HTMLElement = HTMLElement> = T & { ref?: U | null };

// Helper para formatear periodo
export function formatPeriod(period: string): string {
	// "202601" → "Ene 2026"
	const year = period.slice(0, 4);
	const month = parseInt(period.slice(4, 6), 10) - 1;
	return new Intl.DateTimeFormat('es-PE', { month: 'short', year: 'numeric' })
		.format(new Date(parseInt(year), month, 1))
		.replace('.', '');
}
