'use client';

import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { CheckCircle2, Copy, ExternalLink, Search } from 'lucide-react';

import { archiveApi, type ArchiveSearchItem } from '@/lib/api';
import { formatDate, truncate } from '@/lib/utils';
import { KnowledgeWorkspaceHeader } from '@/components/knowledge/KnowledgeWorkspaceHeader';

function getApiErrorMessage(error: unknown, fallback: string): string {
    if (isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        if (typeof detail === 'string' && detail.trim()) return detail;
        const message = error.response?.data?.error?.message;
        if (typeof message === 'string' && message.trim()) return message;
    }
    return fallback;
}

export default function ArchivePage() {
    const [query, setQuery] = useState('');
    const [debouncedQuery, setDebouncedQuery] = useState('');
    const [limit, setLimit] = useState(10);
    const [copiedId, setCopiedId] = useState<number | null>(null);

    useEffect(() => {
        const timer = window.setTimeout(() => setDebouncedQuery(query.trim()), 350);
        return () => window.clearTimeout(timer);
    }, [query]);

    const { data, isLoading, isFetching, error } = useQuery({
        queryKey: ['archive-search', debouncedQuery, limit],
        queryFn: () => archiveApi.search({ q: debouncedQuery, limit, sort: 'recent' }),
        enabled: debouncedQuery.length >= 2,
    });

    const items = useMemo(() => (data?.data?.items || []) as ArchiveSearchItem[], [data?.data?.items]);
    const errorMessage = useMemo(() => {
        if (!error) return null;
        return getApiErrorMessage(error, 'تعذر جلب نتائج الأرشيف.');
    }, [error]);

    const handleCopy = async (item: ArchiveSearchItem) => {
        if (!item.url) return;
        try {
            await navigator.clipboard.writeText(item.url);
            setCopiedId(item.id);
            window.setTimeout(() => setCopiedId(null), 1500);
        } catch {
            // no-op
        }
    };

    return (
        <div className="space-y-5" dir="rtl">
            <KnowledgeWorkspaceHeader
                activeHref="/archive"
                title="أرشيف الشروق"
                description="ابحث في الأرشيف باعتباره جزءًا من مساحة معرفة موحدة مع القصص والذاكرة، لا كسطح منفصل معزول عن العمل اليومي."
            />

            {errorMessage && (
                <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                    {errorMessage}
                </div>
            )}

            <section className="space-y-3 rounded-2xl border border-white/10 bg-gray-900/40 p-4">
                <div className="flex flex-wrap items-center gap-2">
                    <div className="relative min-w-[220px] flex-1">
                        <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
                        <input
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="ابحث في أرشيف الشروق..."
                            className="h-10 w-full rounded-xl border border-white/10 bg-white/5 pr-10 pl-3 text-sm text-white placeholder:text-gray-500"
                            dir="rtl"
                        />
                    </div>
                    <select
                        value={limit}
                        onChange={(e) => setLimit(Number(e.target.value))}
                        className="h-10 rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-gray-200"
                    >
                        {[5, 10, 15, 20].map((value) => (
                            <option key={value} value={value}>
                                {value} نتيجة
                            </option>
                        ))}
                    </select>
                    <div className="text-xs text-gray-500">
                        {debouncedQuery.length >= 2 ? (isFetching ? 'جارٍ البحث...' : `نتائج: ${items.length}`) : 'اكتب كلمتين على الأقل'}
                    </div>
                </div>

                <div className="space-y-2">
                    {isLoading && debouncedQuery.length >= 2 ? (
                        <div className="p-3 text-sm text-gray-400">جارٍ جلب نتائج الأرشيف...</div>
                    ) : items.length === 0 && debouncedQuery.length >= 2 ? (
                        <div className="p-3 text-sm text-gray-500">لا توجد نتائج مطابقة.</div>
                    ) : (
                        items.map((item) => (
                            <article key={item.id} className="space-y-2 rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3">
                                <div className="flex items-start justify-between gap-3">
                                    <div className="space-y-1">
                                        <h3 className="text-sm font-semibold leading-relaxed text-white">{item.title || 'بدون عنوان'}</h3>
                                        <div className="flex flex-wrap gap-2 text-xs text-gray-400">
                                            <span>{item.source_name || 'الشروق أونلاين'}</span>
                                            <span>•</span>
                                            <span>{formatDate(item.published_at)}</span>
                                            <span>•</span>
                                            <span>درجة {(item.score * 100).toFixed(1)}%</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {item.url && (
                                            <a
                                                href={item.url}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-gray-300 hover:text-white"
                                                aria-label="فتح المصدر"
                                            >
                                                <ExternalLink className="h-4 w-4" />
                                            </a>
                                        )}
                                        {item.url && (
                                            <button
                                                type="button"
                                                onClick={() => handleCopy(item)}
                                                className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-gray-300 hover:text-white"
                                                aria-label="نسخ الرابط"
                                            >
                                                {copiedId === item.id ? <CheckCircle2 className="h-4 w-4 text-emerald-300" /> : <Copy className="h-4 w-4" />}
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {item.summary && (
                                    <p className="text-sm leading-7 text-gray-300">{truncate(item.summary, 280)}</p>
                                )}

                                <div className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-gray-400">
                                    {item.url || 'لا يوجد رابط ظاهر للمادة.'}
                                </div>
                            </article>
                        ))
                    )}
                </div>
            </section>
        </div>
    );
}
