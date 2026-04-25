'use client';

import Link from 'next/link';
import type { ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, ArrowRight, Radar, TrendingUp } from 'lucide-react';

import { milApi, type MILDashboardListItem, type MILDashboardResponse } from '@/lib/api';
import { EmptyState, InsightCard, PageHeader, SectionHeader, StatusBadge } from '@/components/ux/SurfacePrimitives';

function metricTone(tone: string): 'default' | 'warn' | 'danger' | 'success' {
    if (tone === 'high') return 'danger';
    if (tone === 'medium') return 'warn';
    if (tone === 'positive') return 'success';
    return 'default';
}

function DashboardList({
    title,
    hint,
    items,
    icon,
}: {
    title: string;
    hint: string;
    items: MILDashboardListItem[];
    icon: ReactNode;
}) {
    return (
        <section className="rounded-[28px] border border-white/10 bg-gray-900/40 p-4 space-y-3" dir="rtl">
            <SectionHeader title={title} description={hint} count={items.length || null} />
            <div className="absolute sr-only">{icon}</div>
            {items.length === 0 ? (
                <EmptyState
                    title="لا توجد عناصر بارزة الآن."
                    description="ستظهر هنا فقط العناصر التي تستحق انتباهًا تنفيذيًا حقيقيًا."
                />
            ) : (
                <div className="space-y-2">
                    {items.map((item) => {
                        const content = (
                            <div className="rounded-xl border border-white/10 bg-black/20 px-3 py-3">
                                <div className="flex items-start justify-between gap-3">
                                    <div>
                                        <p className="text-sm text-white">{item.title}</p>
                                        {item.subtitle && <p className="mt-1 text-xs text-cyan-200">{item.subtitle}</p>}
                                        <p className="mt-1 text-xs leading-5 text-gray-300">{item.hint}</p>
                                    </div>
                                    {item.confidence_score != null && (
                                        <StatusBadge tone="info">{Math.round(item.confidence_score * 100)}%</StatusBadge>
                                    )}
                                </div>
                            </div>
                        );
                        if (item.href) {
                            return (
                                <Link key={`${title}-${item.title}`} href={item.href}>
                                    {content}
                                </Link>
                            );
                        }
                        return <div key={`${title}-${item.title}`}>{content}</div>;
                    })}
                </div>
            )}
        </section>
    );
}

export default function DashboardPage() {
    const dashboardQuery = useQuery({
        queryKey: ['mil-dashboard'],
        queryFn: async () => (await milApi.dashboard()).data,
        refetchInterval: 45_000,
    });

    const dashboard = (dashboardQuery.data || null) as MILDashboardResponse | null;

    return (
        <div className="space-y-6" dir="rtl">
            <PageHeader
                eyebrow="طبقة المدير"
                title="لوحة الاستخبارات التنفيذية"
                icon={Radar}
                description="هذه اللوحة للقراءة الاستراتيجية واتخاذ القرار التنفيذي، وليست بديلًا عن مسار الصحفي اليومي. راقب أين يرتفع الضغط وأين توجد فرص أو مخاطر تحتاج تدخلًا إداريًا."
                meta={
                    <>
                        <StatusBadge tone="info">استراتيجية فقط</StatusBadge>
                        <StatusBadge tone="warn">منفصلة عن طابور العمل اليومي</StatusBadge>
                    </>
                }
                actions={
                    <>
                        <Link href="/" className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-200 hover:text-white">
                            لوحة الأداء
                        </Link>
                        <Link href="/today" className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-200 hover:text-white">
                            <ArrowRight className="h-4 w-4" />
                            فتح اليوم
                        </Link>
                    </>
                }
            />

            {dashboardQuery.isLoading ? (
                <div className="rounded-2xl border border-white/10 bg-gray-900/40 p-6 text-center text-gray-400">
                    جاري تحميل لوحة الاستخبارات التنفيذية...
                </div>
            ) : !dashboard ? (
                <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-6 text-center text-red-200">
                    تعذر تحميل لوحة الاستخبارات التنفيذية.
                </div>
            ) : (
                <>
                    <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                        {dashboard.metrics
                            .filter((metric) => Number(metric.value) > 0 || metric.tone === 'high' || metric.tone === 'medium')
                            .map((metric) => (
                                <InsightCard
                                    key={metric.key}
                                    title={metric.label}
                                    value={metric.value}
                                    hint={metric.hint || undefined}
                                    tone={metricTone(metric.tone)}
                                />
                            ))}
                    </section>

                    <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
                        <DashboardList
                            title="القصص الصاعدة"
                            hint="زخم تحريري يستحق المتابعة أو التملك الآن."
                            items={dashboard.rising_stories}
                            icon={<TrendingUp className="h-4 w-4" />}
                        />
                        <DashboardList
                            title="فرص فاتتنا"
                            hint="موضوعات عالية القيمة لم تتحول بعد إلى ملكية تحريرية واضحة."
                            items={dashboard.missed_opportunities}
                            icon={<AlertTriangle className="h-4 w-4" />}
                        />
                        <DashboardList
                            title="ضغط المنافسين"
                            hint="المسارات التي يتحرك فيها المنافسون أسرع منا أو قبلنا."
                            items={dashboard.competitor_pressure}
                            icon={<Radar className="h-4 w-4" />}
                        />
                        <DashboardList
                            title="مراقبة الثقة بالمصادر"
                            hint="تحولات تستدعي الحذر أو إعادة ترتيب الاعتماد على المصادر."
                            items={dashboard.source_trust_watch}
                            icon={<Radar className="h-4 w-4" />}
                        />
                    </div>
                </>
            )}
        </div>
    );
}
