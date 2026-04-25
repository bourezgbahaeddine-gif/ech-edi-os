'use client';

import Link from 'next/link';
import { ArrowLeft, Sparkles } from 'lucide-react';

import { cn } from '@/lib/utils';

type NextActionBarProps = {
    eyebrow?: string;
    title: string;
    description: string;
    href?: string;
    actionLabel?: string;
    onAction?: () => void;
    meta?: string[];
    tone?: 'default' | 'warn' | 'danger' | 'success';
};

export function NextActionBar({
    eyebrow = 'الإجراء التالي المقترح',
    title,
    description,
    href,
    actionLabel,
    onAction,
    meta = [],
    tone = 'default',
}: NextActionBarProps) {
    const toneClass =
        tone === 'danger'
            ? 'border-rose-500/30 bg-rose-500/10'
            : tone === 'warn'
              ? 'border-amber-500/30 bg-amber-500/10'
              : tone === 'success'
                ? 'border-emerald-500/30 bg-emerald-500/10'
                : 'border-cyan-500/25 bg-cyan-500/10';

    return (
        <section className={cn('rounded-3xl border p-4', toneClass)} dir="rtl">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="min-w-0">
                    <div className="inline-flex items-center gap-2 text-[11px] text-slate-300">
                        <Sparkles className="h-3.5 w-3.5" />
                        {eyebrow}
                    </div>
                    <h2 className="mt-2 text-lg font-semibold text-white">{title}</h2>
                    <p className="mt-1 text-sm leading-6 text-slate-300">{description}</p>
                    {meta.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                            {meta.map((item) => (
                                <span
                                    key={item}
                                    className="rounded-full border border-white/10 bg-white/[0.05] px-2.5 py-1 text-[11px] text-slate-300"
                                >
                                    {item}
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                {href && actionLabel && (
                    <Link
                        href={href}
                        onClick={onAction}
                        className="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-sm font-medium text-white hover:bg-white/15"
                    >
                        {actionLabel}
                        <ArrowLeft className="h-4 w-4" />
                    </Link>
                )}
                {!href && actionLabel && onAction && (
                    <button
                        type="button"
                        onClick={onAction}
                        className="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-sm font-medium text-white hover:bg-white/15"
                    >
                        {actionLabel}
                        <ArrowLeft className="h-4 w-4" />
                    </button>
                )}
            </div>
        </section>
    );
}
