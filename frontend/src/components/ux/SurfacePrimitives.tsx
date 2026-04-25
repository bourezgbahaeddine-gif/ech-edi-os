'use client';

import type { ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { ArrowLeft, type LucideIcon } from 'lucide-react';

import { cn } from '@/lib/utils';

type Tone = 'default' | 'info' | 'success' | 'warn' | 'danger';

function toneClasses(tone: Tone): string {
    if (tone === 'danger') return 'border-red-500/30 bg-red-500/10 text-red-100';
    if (tone === 'warn') return 'border-amber-500/30 bg-amber-500/10 text-amber-100';
    if (tone === 'success') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100';
    if (tone === 'info') return 'border-cyan-500/30 bg-cyan-500/10 text-cyan-100';
    return 'border-white/10 bg-white/[0.04] text-white';
}

export function StatusBadge({
    children,
    tone = 'default',
    className,
}: {
    children: ReactNode;
    tone?: Tone;
    className?: string;
}) {
    return (
        <span className={cn('inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium', toneClasses(tone), className)}>
            {children}
        </span>
    );
}

export function PageHeader({
    eyebrow,
    title,
    description,
    icon: Icon,
    actions,
    meta,
}: {
    eyebrow?: string;
    title: string;
    description?: string;
    icon?: LucideIcon;
    actions?: ReactNode;
    meta?: ReactNode;
}) {
    return (
        <section className="rounded-[28px] border border-white/10 bg-[linear-gradient(135deg,rgba(15,23,42,0.88),rgba(15,23,42,0.72))] p-5 md:p-6" dir="rtl">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="min-w-0">
                    {eyebrow && <p className="text-[11px] font-medium tracking-[0.24em] text-cyan-300/80">{eyebrow}</p>}
                    <div className="mt-2 flex items-center gap-3">
                        {Icon && (
                            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-cyan-500/20 bg-cyan-500/10 text-cyan-200">
                                <Icon className="h-5 w-5" />
                            </div>
                        )}
                        <div className="min-w-0">
                            <h1 className="text-2xl font-bold text-white md:text-[2rem]">{title}</h1>
                            {description && <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">{description}</p>}
                        </div>
                    </div>
                    {meta && <div className="mt-4 flex flex-wrap items-center gap-2">{meta}</div>}
                </div>
                {actions && <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>}
            </div>
        </section>
    );
}

export function SectionHeader({
    title,
    description,
    icon: Icon,
    count,
    trailing,
}: {
    title: string;
    description?: string;
    icon?: LucideIcon;
    count?: number | null;
    trailing?: ReactNode;
}) {
    return (
        <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
                <div className="flex items-center gap-2">
                    {Icon && <Icon className="h-4 w-4 text-cyan-300" />}
                    <h2 className="text-base font-semibold text-white">{title}</h2>
                    {typeof count === 'number' && count > 0 && <StatusBadge tone="info">{count}</StatusBadge>}
                </div>
                {description && <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>}
            </div>
            {trailing && <div className="shrink-0">{trailing}</div>}
        </div>
    );
}

export function ActionCard({
    title,
    description,
    reason,
    meta,
    actionLabel,
    actionHref,
    actionTone = 'info',
    onAction,
    footer,
    className,
}: {
    title: string;
    description?: string;
    reason?: string;
    meta?: ReactNode;
    actionLabel: string;
    actionHref?: string;
    actionTone?: Tone;
    onAction?: () => void;
    footer?: ReactNode;
    className?: string;
}) {
    const buttonClass = cn(
        'inline-flex min-h-10 items-center justify-center gap-2 rounded-xl border px-3 py-2 text-xs font-medium transition-colors',
        toneClasses(actionTone),
    );

    return (
        <article className={cn('rounded-2xl border border-white/10 bg-white/[0.03] p-4', className)} dir="rtl">
            <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                    <h3 className="text-sm font-semibold text-white">{title}</h3>
                    {description && <p className="mt-2 text-xs leading-6 text-slate-300">{description}</p>}
                    {reason && <p className="mt-2 text-[11px] leading-6 text-slate-400">{reason}</p>}
                    {meta && <div className="mt-3 flex flex-wrap items-center gap-2">{meta}</div>}
                </div>
            </div>
            <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                {actionHref ? (
                    <a href={actionHref} onClick={onAction} className={buttonClass}>
                        {actionLabel}
                        <ArrowLeft className="h-4 w-4" />
                    </a>
                ) : (
                    <button type="button" onClick={onAction} className={buttonClass}>
                        {actionLabel}
                        <ArrowLeft className="h-4 w-4" />
                    </button>
                )}
                {footer && <div className="text-[11px] text-slate-500">{footer}</div>}
            </div>
        </article>
    );
}

export function InsightCard({
    title,
    value,
    hint,
    tone = 'default',
    className,
}: {
    title: string;
    value: ReactNode;
    hint?: string;
    tone?: Tone;
    className?: string;
}) {
    return (
        <article className={cn('rounded-2xl border p-4', toneClasses(tone), className)} dir="rtl">
            <p className="text-[11px] opacity-80">{title}</p>
            <div className="mt-2 text-2xl font-semibold">{value}</div>
            {hint && <p className="mt-2 text-xs leading-6 opacity-80">{hint}</p>}
        </article>
    );
}

export function FilterBar({
    children,
    className,
}: {
    children: ReactNode;
    className?: string;
}) {
    return (
        <div className={cn('flex flex-wrap items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.03] p-3', className)} dir="rtl">
            {children}
        </div>
    );
}

export function EmptyState({
    title,
    description,
    action,
    className,
}: {
    title: string;
    description?: string;
    action?: ReactNode;
    className?: string;
}) {
    return (
        <div className={cn('rounded-2xl border border-dashed border-white/10 bg-black/20 px-4 py-8 text-center', className)} dir="rtl">
            <p className="text-sm font-medium text-slate-200">{title}</p>
            {description && <p className="mt-2 text-xs leading-6 text-slate-400">{description}</p>}
            {action && <div className="mt-4 flex justify-center">{action}</div>}
        </div>
    );
}

export function Drawer({
    open,
    title,
    description,
    onClose,
    children,
    widthClassName = 'max-w-xl',
}: {
    open: boolean;
    title: string;
    description?: string;
    onClose: () => void;
    children: ReactNode;
    widthClassName?: string;
}) {
    if (typeof document === 'undefined' || !open) return null;

    return createPortal(
        <div className="fixed inset-0 z-[130] bg-black/70 p-4 backdrop-blur-sm" onClick={onClose}>
            <div
                className={cn('mr-auto h-full w-full rounded-[28px] border border-white/10 bg-[#0F172A]/96 p-4 shadow-2xl', widthClassName)}
                dir="rtl"
                onClick={(event) => event.stopPropagation()}
            >
                <div className="mb-4 flex items-start justify-between gap-3 border-b border-white/10 pb-4">
                    <div>
                        <h2 className="text-lg font-semibold text-white">{title}</h2>
                        {description && <p className="mt-1 text-sm leading-6 text-slate-400">{description}</p>}
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-200 hover:bg-white/10"
                    >
                        إغلاق
                    </button>
                </div>
                <div className="h-[calc(100%-72px)] overflow-y-auto">{children}</div>
            </div>
        </div>,
        document.body,
    );
}
