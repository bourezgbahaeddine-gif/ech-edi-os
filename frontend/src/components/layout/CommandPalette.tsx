'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Command, FileText, FolderGit2, Library, Newspaper, Search, Sparkles, Wrench } from 'lucide-react';

import { editorialApi, newsApi, storiesApi, type ArticleBrief, type WorkspaceDraft, type StoryRecord } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { trackUiAction } from '@/lib/ux-telemetry';
import { cn } from '@/lib/utils';
import { getPrimaryNav, getSecondaryNav, getVisibleNav, normalizeRole, type NavItem } from '@/components/layout/navigation';

type CommandPaletteProps = {
    open: boolean;
    onClose: () => void;
};

type PaletteItem = {
    id: string;
    label: string;
    description?: string;
    href?: string;
    section: string;
    icon: NavItem['icon'];
    keywords?: string[];
    run?: () => void;
    kind?: 'nav' | 'article' | 'draft' | 'story' | 'action';
};

function articleToPaletteItem(article: ArticleBrief): PaletteItem {
    return {
        id: `article:${article.id}`,
        label: article.title_ar || article.original_title || `خبر #${article.id}`,
        description: `خبر تحريري · ${article.source_name || 'بدون مصدر ظاهر'}`,
        href: `/news/${article.id}`,
        section: 'فتح خبر',
        icon: Newspaper,
        kind: 'article',
        keywords: [String(article.id), article.status || '', article.source_name || ''],
    };
}

function draftToPaletteItem(draft: WorkspaceDraft): PaletteItem {
    const title = draft.title || `مسودة ${draft.work_id}`;
    const href = draft.article_id
        ? `/workspace-drafts?article_id=${draft.article_id}&work_id=${encodeURIComponent(draft.work_id)}`
        : `/workspace-drafts?work_id=${encodeURIComponent(draft.work_id)}`;

    return {
        id: `draft:${draft.work_id}`,
        label: title,
        description: `مسودة عمل · ${draft.status || 'draft'}`,
        href,
        section: 'فتح مسودة',
        icon: FolderGit2,
        kind: 'draft',
        keywords: [draft.work_id, draft.status || '', String(draft.article_id || '')],
    };
}

function storyToPaletteItem(story: StoryRecord): PaletteItem {
    return {
        id: `story:${story.id}`,
        label: story.title,
        description: `قصة تحريرية · ${story.story_key}`,
        href: '/stories',
        section: 'فتح قصة',
        icon: Library,
        kind: 'story',
        keywords: [story.story_key, story.category || '', story.status || ''],
    };
}

export default function CommandPalette({ open, onClose }: CommandPaletteProps) {
    const router = useRouter();
    const { user } = useAuth();
    const role = normalizeRole(user?.role || '');
    const inputRef = useRef<HTMLInputElement | null>(null);
    const [query, setQuery] = useState('');
    const [index, setIndex] = useState(0);

    const navItems = useMemo<PaletteItem[]>(() => {
        const primary = getPrimaryNav(role).map((item) => ({
            id: `primary:${item.href}`,
            label: item.label,
            description: item.description,
            href: item.href,
            section: 'المسار اليومي',
            icon: item.icon,
            kind: 'nav' as const,
        }));

        const secondary = getSecondaryNav(role).flatMap((section) =>
            section.items.map((item) => ({
                id: `${section.key}:${item.href}`,
                label: item.label,
                description: item.description,
                href: item.href,
                section: section.label,
                icon: item.icon,
                kind: 'nav' as const,
            })),
        );

        const remaining = getVisibleNav(role)
            .filter((item) => ![...primary, ...secondary].some((entry) => entry.href === item.href))
            .map((item) => ({
                id: `nav:${item.href}`,
                label: item.label,
                description: item.description,
                href: item.href,
                section: 'روابط إضافية',
                icon: item.icon,
                kind: 'nav' as const,
            }));

        const quickActions: PaletteItem[] = [
            {
                id: 'action:today',
                label: 'اذهب إلى الإجراء التالي في اليوم',
                description: 'عودة سريعة إلى صفحة القرار اليومية.',
                href: '/today',
                section: 'أوامر سريعة',
                icon: Sparkles,
                kind: 'action',
            },
            {
                id: 'action:news',
                label: 'افتح طابور الأخبار',
                description: 'اختصار للوصول إلى المواد الجديدة والعاجلة.',
                href: '/news',
                section: 'أوامر سريعة',
                icon: Newspaper,
                kind: 'action',
            },
            {
                id: 'action:workspace',
                label: 'افتح الكتابة والمسودات',
                description: 'عودة مباشرة إلى المحرر ومساحة العمل.',
                href: '/workspace-drafts',
                section: 'أوامر سريعة',
                icon: FileText,
                kind: 'action',
            },
        ];

        return [...quickActions, ...primary, ...secondary, ...remaining];
    }, [role]);

    const searchEnabled = open && query.trim().length >= 2;

    const articleResultsQuery = useQuery({
        queryKey: ['command-palette-news', query],
        queryFn: async () => (await newsApi.semanticSearch({ q: query.trim(), limit: 6, mode: 'editorial' })).data,
        enabled: searchEnabled,
        staleTime: 30_000,
    });

    const draftResultsQuery = useQuery({
        queryKey: ['command-palette-drafts'],
        queryFn: async () => (await editorialApi.workspaceDrafts({ status: 'draft', limit: 40 })).data,
        enabled: open,
        staleTime: 60_000,
    });

    const storyResultsQuery = useQuery({
        queryKey: ['command-palette-stories'],
        queryFn: async () => (await storiesApi.list({ limit: 60 })).data,
        enabled: open,
        staleTime: 60_000,
    });

    const queryLower = query.trim().toLowerCase();

    const liveItems = useMemo(() => {
        const items: PaletteItem[] = [];

        if (queryLower.length >= 2) {
            const articleItems = ((articleResultsQuery.data || []) as ArticleBrief[]).map(articleToPaletteItem);
            const draftItems = ((draftResultsQuery.data || []) as WorkspaceDraft[])
                .filter((draft) => {
                    const haystack = [draft.title, draft.work_id, draft.status]
                        .filter(Boolean)
                        .join(' ')
                        .toLowerCase();
                    return haystack.includes(queryLower);
                })
                .slice(0, 6)
                .map(draftToPaletteItem);
            const storyItems = ((storyResultsQuery.data || []) as StoryRecord[])
                .filter((story) => {
                    const haystack = [story.title, story.story_key, story.category, story.status]
                        .filter(Boolean)
                        .join(' ')
                        .toLowerCase();
                    return haystack.includes(queryLower);
                })
                .slice(0, 6)
                .map(storyToPaletteItem);

            items.push(...articleItems, ...draftItems, ...storyItems);
        }

        return items;
    }, [articleResultsQuery.data, draftResultsQuery.data, queryLower, storyResultsQuery.data]);

    const filteredItems = useMemo(() => {
        const clean = query.trim().toLowerCase();
        const combined = [...liveItems, ...navItems];
        const deduped = combined.filter(
            (item, itemIndex) =>
                combined.findIndex((candidate) => candidate.id === item.id || (candidate.href && candidate.href === item.href && candidate.section === item.section)) === itemIndex,
        );

        if (!clean) return deduped;
        return deduped.filter((item) => {
            return (
                item.label.toLowerCase().includes(clean) ||
                (item.description || '').toLowerCase().includes(clean) ||
                item.section.toLowerCase().includes(clean) ||
                (item.keywords || []).some((keyword) => keyword.toLowerCase().includes(clean))
            );
        });
    }, [liveItems, navItems, query]);

    const activeIndex = filteredItems.length ? Math.min(index, filteredItems.length - 1) : 0;

    const handleClose = () => {
        setQuery('');
        setIndex(0);
        onClose();
    };

    const runItem = (item: PaletteItem) => {
        trackUiAction('command_palette', item.kind === 'action' ? 'action' : 'navigate', {
            role: role || 'guest',
            href: item.href || null,
            item_id: item.id,
            section: item.section,
            kind: item.kind || 'nav',
        });

        handleClose();
        if (item.run) {
            item.run();
            return;
        }
        if (item.href) {
            router.push(item.href);
        }
    };

    useEffect(() => {
        if (open) {
            inputRef.current?.focus();
        }
    }, [open]);

    useEffect(() => {
        if (!open) return;
        const handler = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                event.preventDefault();
                handleClose();
                return;
            }
            if (!filteredItems.length) return;
            if (event.key === 'ArrowDown') {
                event.preventDefault();
                setIndex((prev) => Math.min(prev + 1, filteredItems.length - 1));
                return;
            }
            if (event.key === 'ArrowUp') {
                event.preventDefault();
                setIndex((prev) => Math.max(prev - 1, 0));
                return;
            }
            if (event.key === 'Enter') {
                event.preventDefault();
                const target = filteredItems[activeIndex];
                if (!target) return;
                runItem(target);
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [activeIndex, filteredItems, open]);

    if (typeof document === 'undefined' || !open) return null;

    return createPortal(
        <div className="fixed inset-0 z-[140] bg-black/70 p-4 backdrop-blur-sm" dir="rtl" onClick={handleClose}>
            <div
                className="mx-auto mt-[6vh] w-full max-w-4xl rounded-[28px] border border-white/10 bg-[#0F172A]/95 shadow-2xl"
                onClick={(event) => event.stopPropagation()}
            >
                <div className="border-b border-white/10 px-4 py-4">
                    <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-3 py-3">
                        <Search className="h-4 w-4 text-slate-400" />
                        <input
                            ref={inputRef}
                            value={query}
                            onChange={(event) => {
                                setQuery(event.target.value);
                                setIndex(0);
                            }}
                            placeholder="ابحث عن صفحة أو خبر أو مسودة أو قصة..."
                            className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
                        />
                        <span className="inline-flex items-center gap-1 rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-[10px] text-slate-400">
                            <Command className="h-3 w-3" />
                            K
                        </span>
                    </div>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
                        <Wrench className="h-3.5 w-3.5" />
                        <span>هذه الطبقة تجمع الصفحات المخفية من القائمة الرئيسية، وتبحث أيضًا داخل الأخبار والمسودات والقصص.</span>
                    </div>
                </div>

                <div className="max-h-[68vh] overflow-y-auto p-3">
                    {filteredItems.length === 0 ? (
                        <div className="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-sm text-slate-400">
                            لا توجد نتائج مطابقة. جرّب اسم صفحة أو رقم خبر أو عنوان مسودة مختلف.
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {filteredItems.map((item, itemIndex) => {
                                const active = itemIndex === activeIndex;
                                const Icon = item.icon;
                                return (
                                    <button
                                        key={item.id}
                                        type="button"
                                        onMouseEnter={() => setIndex(itemIndex)}
                                        onClick={() => runItem(item)}
                                        className={cn(
                                            'flex w-full items-center gap-3 rounded-2xl border px-4 py-3 text-right transition-colors',
                                            active
                                                ? 'border-cyan-500/30 bg-cyan-500/10 text-white'
                                                : 'border-white/10 bg-white/[0.03] text-slate-200 hover:bg-white/[0.06]',
                                        )}
                                    >
                                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/5">
                                            <Icon className="h-4.5 w-4.5" />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <div className="flex flex-wrap items-center gap-2">
                                                <span className="text-sm font-medium">{item.label}</span>
                                                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] text-slate-400">
                                                    {item.section}
                                                </span>
                                            </div>
                                            {item.description && <p className="mt-1 truncate text-xs text-slate-400">{item.description}</p>}
                                        </div>
                                        <ArrowLeft className="h-4 w-4 shrink-0 text-slate-500" />
                                    </button>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>,
        document.body,
    );
}
