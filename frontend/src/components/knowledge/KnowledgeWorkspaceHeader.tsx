'use client';

import Link from 'next/link';
import { BookOpen, Library, ScrollText } from 'lucide-react';

import { PageHeader, StatusBadge } from '@/components/ux/SurfacePrimitives';
import { cn } from '@/lib/utils';

const tabs = [
    { href: '/stories', label: 'المتابعات والقصص', icon: Library },
    { href: '/archive', label: 'الأرشيف', icon: ScrollText },
    { href: '/memory', label: 'الذاكرة', icon: BookOpen },
];

export function KnowledgeWorkspaceHeader({
    activeHref,
    title,
    description,
}: {
    activeHref: string;
    title: string;
    description: string;
}) {
    return (
        <div className="space-y-4" dir="rtl">
            <PageHeader
                eyebrow="مساحة معرفة ومتابعة"
                title={title}
                icon={Library}
                description={description}
                meta={
                    <>
                        <StatusBadge tone="info">طبقة موحدة للمتابعة والسياق</StatusBadge>
                        <StatusBadge tone="warn">المسارات القديمة ما زالت تعمل</StatusBadge>
                    </>
                }
            />
            <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.03] p-3">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    const active = activeHref === tab.href;
                    return (
                        <Link
                            key={tab.href}
                            href={tab.href}
                            className={cn(
                                'inline-flex min-h-10 items-center gap-2 rounded-xl border px-3 py-2 text-xs transition-colors',
                                active
                                    ? 'border-cyan-500/30 bg-cyan-500/10 text-cyan-100'
                                    : 'border-white/10 bg-white/5 text-slate-300 hover:text-white',
                            )}
                        >
                            <Icon className="h-4 w-4" />
                            {tab.label}
                        </Link>
                    );
                })}
            </div>
        </div>
    );
}
