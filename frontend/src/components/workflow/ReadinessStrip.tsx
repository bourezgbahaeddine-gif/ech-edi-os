'use client';

import { CheckCircle2, CircleAlert } from 'lucide-react';

import { cn } from '@/lib/utils';

export type ReadinessStripItem = {
    id: string;
    label: string;
    passed: boolean;
    hint?: string;
    actionLabel?: string;
    onAction?: () => void;
};

export function ReadinessStrip({
    title,
    subtitle,
    items,
}: {
    title: string;
    subtitle?: string;
    items: ReadinessStripItem[];
}) {
    return (
        <section className="rounded-2xl border border-white/10 bg-gray-900/45 p-4" dir="rtl">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <div>
                    <h3 className="text-sm font-semibold text-white">{title}</h3>
                    {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
                </div>
                <div className="text-[11px] text-slate-500">{items.filter((item) => item.passed).length}/{items.length} مكتمل</div>
            </div>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2 xl:grid-cols-4">
                {items.map((item) => (
                    <div
                        key={item.id}
                        className={cn(
                            'rounded-xl border px-3 py-3',
                            item.passed ? 'border-emerald-500/25 bg-emerald-500/10' : 'border-amber-500/25 bg-amber-500/10',
                        )}
                    >
                        <div className="flex items-start gap-2">
                            {item.passed ? (
                                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" />
                            ) : (
                                <CircleAlert className="mt-0.5 h-4 w-4 shrink-0 text-amber-200" />
                            )}
                            <div className="min-w-0">
                                <div className="text-sm font-medium text-white">{item.label}</div>
                                {item.hint && <p className="mt-1 text-[11px] leading-5 text-slate-300">{item.hint}</p>}
                            </div>
                        </div>
                        {item.actionLabel && item.onAction && (
                            <button
                                type="button"
                                onClick={item.onAction}
                                className="mt-3 inline-flex min-h-8 items-center rounded-lg border border-white/15 bg-white/10 px-2.5 py-1.5 text-[11px] text-slate-100 hover:bg-white/15"
                            >
                                {item.actionLabel}
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </section>
    );
}
