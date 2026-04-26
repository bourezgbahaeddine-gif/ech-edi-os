'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { CalendarClock, CheckCircle2, Inbox, RefreshCw, Send, ShieldAlert, Zap } from 'lucide-react';

import {
    dashboardApi,
    editorialApi,
    eventsApi,
    milApi,
    newsApi,
    type ArticleBrief,
    type ChiefPendingItem,
    type DashboardNotification,
    type EventActionItem,
    type MILTodayFullResponse,
} from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { type WorkflowTone } from '@/components/workflow/WorkflowCard';
import { NextActionBar } from '@/components/workflow/NextActionBar';
import { getWorkflowStatusLabel } from '@/lib/workflow-language';
import { RoleOnboardingBanner } from '@/components/workflow/RoleOnboardingBanner';
import { trackMetricEvent, trackNextAction, useTrackFirstAction, useTrackSurfaceView } from '@/lib/ux-telemetry';
import { TutorialOverlay } from '@/components/onboarding/TutorialOverlay';
import { TutorialWelcomeModal } from '@/components/onboarding/TutorialWelcomeModal';
import { useTutorialState } from '@/lib/tutorial';
import { ActionCard, EmptyState, PageHeader, SectionHeader, StatusBadge } from '@/components/ux/SurfacePrimitives';
import { classifyNotificationInterruption, filterNotificationsForRole } from '@/lib/notification-policy';

type Role =
    | 'director'
    | 'editor_chief'
    | 'journalist'
    | 'presenter'
    | 'show_host'
    | 'social_media'
    | 'print_editor'
    | 'fact_checker'
    | 'observer';

type QueueItem = {
    id: string;
    title: string;
    subtitle: string;
    workflowLabel: string;
    reason: string;
    nextAction: string;
    href: string;
    status: string;
    timestamp?: string | null;
    blockers?: string[];
    tone?: WorkflowTone;
};

function normalizeRole(role: string): Role | null {
    const value = (role || '').trim().toLowerCase();
    if (value === 'chief_editor' || value === 'editor_in_chief' || value === 'editor-chief') {
        return 'editor_chief';
    }
    const allowed: Role[] = [
        'director',
        'editor_chief',
        'journalist',
        'presenter',
        'show_host',
        'social_media',
        'print_editor',
        'fact_checker',
        'observer',
    ];
    return allowed.includes(value as Role) ? (value as Role) : null;
}

function articleTitle(article: ArticleBrief): string {
    return article.title_ar || article.original_title || `مادة #${article.id}`;
}

function articleTimestamp(article: ArticleBrief): string | null {
    return article.created_at || article.crawled_at || null;
}

function ageInHours(value?: string | null): number {
    if (!value) return 0;
    const time = new Date(value).getTime();
    if (!Number.isFinite(time)) return 0;
    return Math.max(0, (Date.now() - time) / 3_600_000);
}

function articleToQueueItem(
    article: ArticleBrief,
    config: {
        workflowLabel: string;
        reason: string;
        nextAction: string;
        href: string;
        tone?: WorkflowTone;
        blockers?: string[];
    },
): QueueItem {
    return {
        id: `article-${article.id}-${article.status}`,
        title: articleTitle(article),
        subtitle: `${article.source_name || 'بدون مصدر ظاهر'} · ${getWorkflowStatusLabel(article.status)}`,
        workflowLabel: config.workflowLabel,
        reason: config.reason,
        nextAction: config.nextAction,
        href: config.href,
        status: article.status || 'unknown',
        timestamp: articleTimestamp(article),
        blockers: config.blockers || [],
        tone: config.tone,
    };
}

function chiefItemToQueueItem(
    item: ChiefPendingItem,
    config?: {
        workflowLabel?: string;
        nextAction?: string;
        href?: string;
        reason?: string;
        tone?: WorkflowTone;
    },
): QueueItem {
    const blockers = [
        ...(item.decision_card?.quality_issues || []),
        ...(item.decision_card?.claims_issues || []),
        ...(item.policy?.required_fixes || []),
    ].filter(Boolean);

    return {
        id: `chief-${item.id}-${item.status || 'unknown'}`,
        title: item.title_ar || item.original_title || `مادة #${item.id}`,
        subtitle: `${item.source_name || 'بدون مصدر ظاهر'} · ${getWorkflowStatusLabel(item.status || 'ready_for_chief_approval')}`,
        workflowLabel: config?.workflowLabel || 'بانتظار اعتماد رئيس التحرير',
        reason:
            config?.reason ||
            (blockers[0]
                ? `وصلت إليك لأن المادة دخلت مرحلة الاعتماد ومعها تنبيه واضح: ${blockers[0]}`
                : 'وصلت إليك لأن المادة دخلت مرحلة اعتماد رئيس التحرير وتحتاج قرارًا نهائيًا.'),
        nextAction: config?.nextAction || 'اتخذ القرار',
        href: config?.href || (item.work_id ? `/workspace-drafts?article_id=${item.id}&work_id=${encodeURIComponent(item.work_id)}` : '/editorial'),
        status: item.status || 'ready_for_chief_approval',
        timestamp: item.updated_at,
        blockers,
        tone: config?.tone || (item.is_breaking ? 'danger' : blockers.length ? 'warn' : 'default'),
    };
}

function notificationToQueueItem(item: DashboardNotification): QueueItem {
    return {
        id: `notification-${item.id}`,
        title: item.title,
        subtitle: item.type,
        workflowLabel: 'تنبيه غرفة الأخبار',
        reason: item.message,
        nextAction: item.article_id ? 'افتح الخبر المرتبط' : 'افتح طابور اليوم',
        href: item.article_id ? `/news/${item.article_id}` : '/today',
        status: item.severity,
        timestamp: item.created_at,
        tone: item.severity === 'high' ? 'danger' : item.severity === 'medium' ? 'warn' : 'default',
    };
}

export default function TodayPage() {
    const { user } = useAuth();
    const router = useRouter();
    const { state: tutorialState, update: updateTutorial, complete: completeTutorial, active: tutorialActive } = useTutorialState();
    const role = normalizeRole(user?.role || '');
    const isChiefFlow = role === 'editor_chief' || role === 'director';
    const isAuthorFlow = !isChiefFlow;
    const surfaceDetails = useMemo(
        () => ({
            role: role || 'guest',
            flow: isChiefFlow ? 'chief' : 'author',
        }),
        [isChiefFlow, role],
    );

    useTrackSurfaceView('today', surfaceDetails);
    const trackFirstAction = useTrackFirstAction('today', surfaceDetails);

    const pendingCandidatesQuery = useQuery({
        queryKey: ['today-pending-candidates'],
        queryFn: async () => (await newsApi.pending(12)).data,
        enabled: isAuthorFlow,
        refetchInterval: 30_000,
    });

    const draftGeneratedQuery = useQuery({
        queryKey: ['today-draft-generated'],
        queryFn: async () => (await newsApi.list({ page: 1, per_page: 12, status: 'draft_generated' })).data.items,
        enabled: role !== 'observer',
        refetchInterval: 30_000,
    });

    const reservationsQuery = useQuery({
        queryKey: ['today-reservations'],
        queryFn: async () => (await newsApi.list({ page: 1, per_page: 12, status: 'approval_request_with_reservations' })).data.items,
        enabled: role !== 'observer',
        refetchInterval: 30_000,
    });

    const readyManualPublishQuery = useQuery({
        queryKey: ['today-ready-manual-publish'],
        queryFn: async () => (await newsApi.list({ page: 1, per_page: 12, status: 'ready_for_manual_publish' })).data.items,
        enabled: isChiefFlow,
        refetchInterval: 30_000,
    });

    const chiefPendingQuery = useQuery({
        queryKey: ['today-chief-pending'],
        queryFn: async () => (await editorialApi.chiefPending(12)).data,
        enabled: isChiefFlow,
        refetchInterval: 30_000,
    });

    const breakingQuery = useQuery({
        queryKey: ['today-breaking'],
        queryFn: async () => (await newsApi.breaking(6)).data,
        enabled: role !== 'observer',
        refetchInterval: 20_000,
    });

    const notificationsQuery = useQuery({
        queryKey: ['today-notifications'],
        queryFn: async () => (await dashboardApi.notifications({ limit: 12 })).data.items,
        enabled: role !== 'observer',
        refetchInterval: 20_000,
    });

    const eventOverviewQuery = useQuery({
        queryKey: ['today-events-overview'],
        queryFn: async () => (await eventsApi.overview({ window_days: 7 })).data,
        enabled: role !== 'observer',
        refetchInterval: 60_000,
    });

    const eventRemindersQuery = useQuery({
        queryKey: ['today-events-reminders'],
        queryFn: async () => (await eventsApi.reminders({ limit: 8 })).data,
        enabled: role !== 'observer',
        refetchInterval: 60_000,
    });

    const eventActionsQuery = useQuery({
        queryKey: ['today-events-actions'],
        queryFn: async () => (await eventsApi.actionItems({ limit: 8 })).data,
        enabled: role !== 'observer',
        refetchInterval: 60_000,
    });

    const milTodayQuery = useQuery({
        queryKey: ['today-mil-full'],
        queryFn: async () => (await milApi.todayFull({ limit_per_section: 3 })).data,
        enabled: role !== 'observer',
        refetchInterval: 60_000,
    });

    const pendingCandidates = useMemo(() => pendingCandidatesQuery.data || [], [pendingCandidatesQuery.data]);
    const draftGenerated = useMemo(() => draftGeneratedQuery.data || [], [draftGeneratedQuery.data]);
    const reservations = useMemo(() => reservationsQuery.data || [], [reservationsQuery.data]);
    const readyManualPublish = useMemo(() => readyManualPublishQuery.data || [], [readyManualPublishQuery.data]);
    const chiefPending = useMemo(() => chiefPendingQuery.data || [], [chiefPendingQuery.data]);
    const breaking = useMemo(() => breakingQuery.data || [], [breakingQuery.data]);
    const notifications = useMemo(
        () => filterNotificationsForRole((notificationsQuery.data || []) as DashboardNotification[], role || 'guest'),
        [notificationsQuery.data, role],
    );
    const milToday = useMemo<MILTodayFullResponse | null>(() => milTodayQuery.data || null, [milTodayQuery.data]);
    const eventsOverview = eventOverviewQuery.data || null;
    const eventReminders = eventRemindersQuery.data || null;
    const eventActions = eventActionsQuery.data || null;

    const journalistNow = useMemo(() => {
        const returned = reservations.slice(0, 3).map((article) =>
            articleToQueueItem(article, {
                workflowLabel: 'عاد من الاعتماد بتحفظات',
                reason: 'ظهرت لك الآن لأن المادة رجعت من رئيس التحرير مع ملاحظات واضحة وتحتاج تعديلًا سريعًا قبل إعادة الإرسال.',
                nextAction: 'افتح المسودة وعدّل',
                href: `/workspace-drafts?article_id=${article.id}`,
                tone: 'warn',
            }),
        );
        const urgentBreaking = breaking
            .filter((article) => article.status === 'candidate' || article.status === 'classified')
            .slice(0, 3)
            .map((article) =>
                articleToQueueItem(article, {
                    workflowLabel: 'مرشّح عاجل في طابور الأخبار',
                    reason: 'دخلت هذه المادة نطاقك لأن النظام رصدها كمادة عاجلة وتحتاج قرارًا تحريريًا سريعًا.',
                    nextAction: 'افتح طابور الأخبار',
                    href: '/news?status=candidate',
                    tone: 'danger',
                }),
            );
        return [...returned, ...urgentBreaking].slice(0, 6);
    }, [breaking, reservations]);

    const journalistNext = useMemo(() => {
        const followUps = draftGenerated.slice(0, 6).map((article) =>
            articleToQueueItem(article, {
                workflowLabel: 'مسودة قيد الاستكمال',
                reason: 'المادة موجودة في مرحلة draft_generated؛ أي أنها دخلت مساحة التحرير وتحتاج استكمالًا أو فحصًا سريعًا ثم إرسالًا للاعتماد.',
                nextAction: 'أكمل في المحرر',
                href: `/workspace-drafts?article_id=${article.id}`,
            }),
        );
        const freshCandidates = pendingCandidates.slice(0, Math.max(0, 6 - followUps.length)).map((article) =>
            articleToQueueItem(article, {
                workflowLabel: 'مرشّح جديد في طابور الأخبار',
                reason: 'دخلت المادة حديثًا إلى قائمة الأخبار وتنتظر بدء العمل التحريري عليها.',
                nextAction: 'افتح قائمة الأخبار',
                href: '/news?status=candidate',
            }),
        );
        return [...followUps, ...freshCandidates].slice(0, 6);
    }, [draftGenerated, pendingCandidates]);

    const journalistRisk = useMemo(() => {
        const staleDrafts = draftGenerated
            .filter((article) => ageInHours(articleTimestamp(article)) >= 4)
            .slice(0, 4)
            .map((article) =>
                articleToQueueItem(article, {
                    workflowLabel: 'مسودة متأخرة',
                    reason: 'هذه المادة بقيت في draft_generated أكثر من اللازم، ما يعني أنها قد تتأخر عن المسار الطبيعي إذا لم تُستكمل الآن.',
                    nextAction: 'استكملها الآن',
                    href: `/workspace-drafts?article_id=${article.id}`,
                    tone: 'warn',
                }),
            );
        const criticalNotifications = notifications
            .filter((item) => item.severity === 'high')
            .slice(0, Math.max(0, 4 - staleDrafts.length))
            .map(notificationToQueueItem);
        return [...staleDrafts, ...criticalNotifications].slice(0, 4);
    }, [draftGenerated, notifications]);

    const chiefNow = useMemo(() => {
        return chiefPending
            .slice()
            .sort((a, b) => Number(b.is_breaking) - Number(a.is_breaking) || b.importance_score - a.importance_score)
            .slice(0, 6)
            .map((item) =>
                chiefItemToQueueItem(item, {
                    workflowLabel: 'بانتظار قرار رئيس التحرير',
                    nextAction: 'اتخذ القرار',
                    reason: item.is_breaking
                        ? 'المادة عاجلة ووصلت الآن إلى مرحلة الاعتماد النهائي، لذلك تحتاج حسمًا مباشرًا.'
                        : undefined,
                }),
            );
    }, [chiefPending]);

    const chiefNext = useMemo(() => {
        const readyItems = readyManualPublish.slice(0, 3).map((article) =>
            articleToQueueItem(article, {
                workflowLabel: 'جاهز للنشر اليدوي',
                reason: 'اجتازت المادة الاعتماد وأصبحت في ready_for_manual_publish، أي أنها جاهزة للتسليم أو النشر اليدوي.',
                nextAction: 'راجع الجاهز للنشر',
                href: '/news?status=ready_for_manual_publish',
                tone: 'success',
            }),
        );
        const reservationItems = reservations.slice(0, Math.max(0, 6 - readyItems.length)).map((article) =>
            articleToQueueItem(article, {
                workflowLabel: 'اعتماد بتحفظات',
                reason: 'هذه المواد ما زالت في حالة تحفظات؛ تحتاج متابعة حتى لا تبقى عالقة بين التحرير والاعتماد.',
                nextAction: 'راجع التحفظات',
                href: '/editorial',
                tone: 'warn',
            }),
        );
        return [...readyItems, ...reservationItems].slice(0, 6);
    }, [readyManualPublish, reservations]);

    const chiefRisk = useMemo(() => {
        const staleApprovals = chiefPending
            .filter((item) => ageInHours(item.updated_at) >= 2)
            .slice(0, 4)
            .map((item) =>
                chiefItemToQueueItem(item, {
                    workflowLabel: 'اعتماد متأخر',
                    nextAction: 'احسم القرار الآن',
                    reason: 'هذه المادة بقيت في طابور الاعتماد أكثر من الحد المرغوب، وقد تعطل المسار إن لم تُحسم الآن.',
                    tone: 'danger',
                }),
            );
        const criticalNotifications = notifications
            .filter((item) => item.severity === 'high')
            .slice(0, Math.max(0, 4 - staleApprovals.length))
            .map(notificationToQueueItem);
        return [...staleApprovals, ...criticalNotifications].slice(0, 4);
    }, [chiefPending, notifications]);

    const tutorialRole = tutorialState.role;
    const tutorialStep = tutorialState.step;
    const journalistFirst = journalistNow[0] || journalistNext[0];
    const chiefFirst = chiefNow[0] || chiefNext[0];
    const recommendedAction = isChiefFlow ? chiefFirst || chiefRisk[0] : journalistFirst || journalistRisk[0];
    const showWelcome = tutorialActive && !tutorialRole;
    const showJournalistOverlay = tutorialActive && tutorialRole === 'journalist' && tutorialStep === 'today_open';
    const showChiefOverlay = tutorialActive && tutorialRole === 'editor_chief' && tutorialStep === 'chief_today';
    const nowItems = isChiefFlow ? chiefNow : journalistNow;
    const nextItems = isChiefFlow ? chiefNext : journalistNext;
    const riskItems = isChiefFlow ? chiefRisk : journalistRisk;

    const urgentItems = useMemo(() => {
        const criticalNotifications = notifications
            .filter((item) => classifyNotificationInterruption(item, role || 'guest') === 'interrupt_now')
            .slice(0, 2)
            .map(notificationToQueueItem);

        const urgentEventActions = ((eventActions?.items || []) as EventActionItem[])
            .filter((item) => String(item.severity).toLowerCase() === 'high')
            .slice(0, 2)
            .map((item) => ({
                id: `event-action-${item.code}-${item.event.id}`,
                title: item.title,
                subtitle: item.event.title,
                workflowLabel: 'حدث يحتاج تحركًا عاجلًا',
                reason: item.recommendation,
                nextAction: item.action || 'افتح مكتب الأحداث',
                href: '/events',
                status: item.severity,
                timestamp: item.event.starts_at,
                tone: 'danger' as WorkflowTone,
            }));

        const criticalMil = (milToday?.critical_now.items || []).slice(0, 2).map((item) => ({
            id: `mil-${item.signal_id}`,
            title: item.title,
            subtitle: `MIL · ${Math.round(item.confidence_score * 100)}٪`,
            workflowLabel: 'إشارة استخبارية حرجة',
            reason: item.why_it_matters,
            nextAction: item.recommended_action,
            href: item.href || '/stories',
            status: item.priority,
            timestamp: item.created_at,
            tone: 'danger' as WorkflowTone,
        }));

        return [...criticalNotifications, ...urgentEventActions, ...criticalMil].slice(0, 6);
    }, [eventActions?.items, milToday?.critical_now.items, notifications, role]);

    const eventSummaryItems = useMemo(() => {
        const items = [];
        if ((eventReminders?.t6 || []).length > 0) {
            items.push({
                label: 'خلال 6 ساعات',
                value: eventReminders?.t6.length || 0,
                tone: 'warn' as const,
            });
        }
        if ((eventReminders?.t24 || []).length > 0) {
            items.push({
                label: 'خلال 24 ساعة',
                value: eventReminders?.t24.length || 0,
                tone: 'info' as const,
            });
        }
        if ((eventsOverview?.overdue || 0) > 0) {
            items.push({
                label: 'متأخر ويحتاج تغطية',
                value: eventsOverview?.overdue || 0,
                tone: 'danger' as const,
            });
        }
        return items;
    }, [eventReminders?.t24, eventReminders?.t6, eventsOverview?.overdue]);

    const headerMeta = useMemo(() => {
        const items: Array<{ label: string; tone: 'info' | 'warn' | 'danger' | 'success' }> = [];
        if (isChiefFlow && chiefPending.length > 0) items.push({ label: `مواد بانتظار القرار: ${chiefPending.length}`, tone: 'info' });
        if (!isChiefFlow && pendingCandidates.length > 0) items.push({ label: `مواد جديدة لك: ${pendingCandidates.length}`, tone: 'info' });
        if (reservations.length > 0) items.push({ label: `تحفظات تحتاج متابعة: ${reservations.length}`, tone: 'warn' });
        if ((eventReminders?.t24 || []).length > 0) items.push({ label: `أحداث قريبة: ${eventReminders?.t24.length}`, tone: 'warn' });
        if (riskItems.length > 0) items.push({ label: `عناصر معرضة للتعطل: ${riskItems.length}`, tone: 'danger' });
        return items;
    }, [chiefPending.length, eventReminders?.t24, isChiefFlow, pendingCandidates.length, reservations.length, riskItems.length]);

    const handleTutorialStart = (selectedRole: 'journalist' | 'editor_chief', pace: 'full' | 'quick') => {
        updateTutorial({
            role: selectedRole,
            pace,
            step: selectedRole === 'editor_chief' ? 'chief_today' : 'today_open',
            done: false,
        });
    };

    const handleTutorialSkip = () => {
        completeTutorial();
    };

    const handleTodayNext = async () => {
        if (tutorialRole === 'journalist') {
            if (journalistFirst?.href) {
                updateTutorial({ step: 'news_open' });
                router.push(journalistFirst.href);
                return;
            }
            try {
                const res = await editorialApi.createManualWorkspaceDraft({
                    title: 'مادة تدريبية سريعة',
                    body: 'هذه مادة تجريبية هدفها تدريبك على المسار بسرعة قبل العمل على المواد الحقيقية.',
                    summary: 'مادة تدريبية لاختبار التحرير.',
                    category: 'general',
                    urgency: 'low',
                    source_action: 'tutorial_sandbox',
                });
                const workId = res.data?.work_id;
                if (workId) {
                    updateTutorial({ step: 'editor_edit' });
                    router.push(`/workspace-drafts?work_id=${workId}`);
                    return;
                }
            } catch {
                // ignore and let user continue
            }
        }
        if (tutorialRole === 'editor_chief') {
            updateTutorial({ step: 'chief_editorial' });
            router.push('/editorial');
            return;
        }
        completeTutorial();
    };

    const isLoading =
        pendingCandidatesQuery.isLoading ||
        draftGeneratedQuery.isLoading ||
        reservationsQuery.isLoading ||
        readyManualPublishQuery.isLoading ||
        chiefPendingQuery.isLoading ||
        breakingQuery.isLoading ||
        notificationsQuery.isLoading ||
        eventOverviewQuery.isLoading ||
        eventActionsQuery.isLoading ||
        eventRemindersQuery.isLoading;

    const renderQueueCard = (item: QueueItem, queueSection: 'now' | 'urgent' | 'next' | 'risk') => (
        <ActionCard
            key={item.id}
            title={item.title}
            description={item.subtitle}
            reason={item.reason}
            actionLabel={item.nextAction}
            actionHref={item.href}
            actionTone={item.tone === 'danger' ? 'danger' : item.tone === 'warn' ? 'warn' : item.tone === 'success' ? 'success' : 'info'}
            onAction={() => {
                trackFirstAction(item.nextAction, { queue_section: queueSection, item_id: item.id });
                trackNextAction('today', item.nextAction, {
                    ...surfaceDetails,
                    queue_section: queueSection,
                    item_id: item.id,
                    workflow_label: item.workflowLabel,
                    target_href: item.href,
                });
            }}
            meta={
                <>
                    <StatusBadge tone={item.tone === 'danger' ? 'danger' : item.tone === 'warn' ? 'warn' : 'default'}>{item.workflowLabel}</StatusBadge>
                    {item.blockers && item.blockers.length > 0 && <StatusBadge tone="warn">عائق: {item.blockers.length}</StatusBadge>}
                    {item.timestamp && <StatusBadge tone="default">{new Date(item.timestamp).toLocaleDateString('ar-DZ')}</StatusBadge>}
                </>
            }
        />
    );

    const isQuickTour = tutorialState.pace === 'quick';

    return (
        <div className="space-y-6" dir="rtl">
            <TutorialWelcomeModal open={showWelcome} onSelectRole={handleTutorialStart} onSkip={handleTutorialSkip} />
            <TutorialOverlay
                open={showJournalistOverlay}
                stepLabel={`الخطوة 1 / ${isQuickTour ? 4 : 5}`}
                title="ابدأ من Today"
                description="هنا تجد موادك اليومية. افتح أول مادة لننتقل مباشرة للمحرر ونكمل الجولة خلال دقيقتين."
                targetSelector={journalistFirst ? '[data-tutorial=\"today-first-card\"]' : undefined}
                primaryLabel={journalistFirst ? 'افتح أول مادة' : 'أنشئ مادة تجريبية'}
                onPrimary={handleTodayNext}
                onSkip={handleTutorialSkip}
            />
            <TutorialOverlay
                open={showChiefOverlay}
                stepLabel="الخطوة 1 / 2"
                title="ابدأ طابور القرار"
                description="هذه الخطوة توصلك مباشرة إلى المواد التي تنتظر قرارك التحريري."
                targetSelector='[data-tutorial="today-chief-queue"]'
                primaryLabel="افتح طابور الاعتماد"
                onPrimary={handleTodayNext}
                onSkip={handleTutorialSkip}
            />
            <RoleOnboardingBanner
                storageKey={`ech_today_onboarding_v1_${role || 'guest'}`}
                title={isChiefFlow ? 'ابدأ يومك من هنا كرئيس تحرير' : 'ابدأ يومك من هنا كصحفي'}
                description={
                    isChiefFlow
                        ? 'هذه الصفحة ليست dashboard عامة؛ هي طابور قرارك اليومي. ابدأ من المواد التي دخلت نطاقك الآن ثم تحرك إلى ما يليه.'
                        : 'هذه الصفحة ليست قائمة لكل شيء؛ هي نقطة البداية اليومية. ابدأ بما دخل نطاقك الآن ثم اتبع الإجراء التالي المقترح.'
                }
                steps={
                    isChiefFlow
                        ? [
                              { title: '1. احسم العاجل', description: 'ابدأ بالمواد التي دخلت مرحلة الاعتماد النهائي أو تحمل مخاطر عالية.' },
                              { title: '2. تابع التحفظات', description: 'راجع ما عاد بتحفظات حتى لا يبقى عالقًا بين التحرير والاعتماد.' },
                              { title: '3. راجع الجاهز للنشر', description: 'بعد الحسم، انتقل إلى المواد الجاهزة للنشر اليدوي أو التسليم.' },
                          ]
                        : [
                              { title: '1. ابدأ الآن', description: 'خذ المواد التي ظهرت في طابورك الآن، خصوصًا العاجلة أو العائدة من الاعتماد.' },
                              { title: '2. نفّذ الإجراء التالي', description: 'افتح المحرر أو طابور الأخبار من الزر الرئيسي بدل البحث بين الصفحات.' },
                              { title: '3. راقب ما يعوق التقدم', description: 'إذا ظهرت مادة متأخرة أو متحفظ عليها، تعامل معها قبل أن تتعطل.' },
                          ]
                }
            />
            {recommendedAction && (
                <NextActionBar
                    title={recommendedAction.nextAction}
                    description={recommendedAction.reason}
                    href={recommendedAction.href}
                    actionLabel={recommendedAction.nextAction}
                    tone={recommendedAction.tone}
                    meta={[recommendedAction.workflowLabel, recommendedAction.subtitle].filter(Boolean)}
                    onAction={() => {
                        trackFirstAction(recommendedAction.nextAction, { queue_section: 'recommended', item_id: recommendedAction.id });
                        trackNextAction('today', recommendedAction.nextAction, {
                            ...surfaceDetails,
                            queue_section: 'recommended',
                            item_id: recommendedAction.id,
                            workflow_label: recommendedAction.workflowLabel,
                            target_href: recommendedAction.href,
                        })
                    }}
                />
            )}

            <PageHeader
                eyebrow={isChiefFlow ? 'قرار اليوم' : 'غرفة القرار اليومية'}
                title="اليوم"
                icon={Zap}
                description={
                    isChiefFlow
                        ? 'هذه ليست لوحة مؤشرات عامة. هذه غرفة قرار رئيس التحرير: ما يحتاج حسمًا الآن، ما هو حرج، وما الإجراء التالي الآمن داخل مسار الاعتماد.'
                        : 'هذه ليست جدار بيانات. هذه صفحة قرار يومية: ما الذي يجب أن تبدأ به الآن، ما الذي قد يعطل المسار، وما الإجراء التالي المقترح بأقل حمل ذهني.'
                }
                meta={headerMeta.map((item) => (
                    <StatusBadge key={item.label} tone={item.tone}>
                        {item.label}
                    </StatusBadge>
                ))}
                actions={
                    <>
                        <Link
                            href={isChiefFlow ? '/editorial' : '/news'}
                            data-tutorial={showChiefOverlay ? 'today-chief-queue' : undefined}
                            className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-200 hover:text-white"
                        >
                            <Inbox className="w-4 h-4" />
                            {isChiefFlow ? 'فتح طابور الاعتماد' : 'فتح طابور الأخبار'}
                        </Link>
                        <Link href="/events" className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-200 hover:text-white">
                            <CalendarClock className="w-4 h-4" />
                            مكتب الأحداث
                        </Link>
                        <Link href="/workspace-drafts" className="inline-flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-xs text-cyan-100 hover:bg-cyan-500/20">
                            <Send className="w-4 h-4" />
                            فتح المسودات
                        </Link>
                    </>
                }
            />

            {isLoading ? (
                <div className="rounded-3xl border border-white/10 bg-[rgba(15,23,42,0.55)] p-8 text-center text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin inline-block ml-2" />
                    جاري تجهيز طابور اليوم...
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
                    <section className="rounded-[28px] border border-white/10 bg-white/[0.03] p-4">
                        <SectionHeader
                            title="ما يجب أن تفعله الآن"
                            description={isChiefFlow ? 'هذه هي المواد التي دخلت نطاق قرارك مباشرة.' : 'ابدأ من هذه المواد قبل أي تصفح إضافي.'}
                            icon={Zap}
                            count={nowItems.length || null}
                        />
                        <div className="mt-4 space-y-3">
                            {nowItems.length === 0 ? (
                                <EmptyState
                                    title={isChiefFlow ? 'لا توجد مواد تحتاج قرارًا مباشرًا الآن.' : 'لا توجد مهام عاجلة للبدء الآن.'}
                                    description="إذا ظهر عنصر جديد سيظهر هنا أولًا بدل التشتت بين القوائم."
                                />
                            ) : (
                                nowItems.map((item, index) => (
                                    <div key={item.id} data-tutorial={showJournalistOverlay && index === 0 ? 'today-first-card' : undefined}>
                                        {renderQueueCard(item, 'now')}
                                    </div>
                                ))
                            )}
                        </div>
                    </section>

                    <section className="rounded-[28px] border border-white/10 bg-white/[0.03] p-4">
                        <SectionHeader
                            title="العاجل والحرج"
                            description="ما يجب أن ينتبه إليه التحرير الآن قبل أن يتحول إلى تأخير أو خسارة تغطية."
                            icon={ShieldAlert}
                            count={urgentItems.length || riskItems.length || null}
                        />
                        <div className="mt-4 space-y-3">
                            {urgentItems.length > 0 ? urgentItems.map((item) => renderQueueCard(item, 'urgent')) : null}
                            {riskItems.slice(0, Math.max(0, 4 - urgentItems.length)).map((item) => renderQueueCard(item, 'risk'))}
                            {urgentItems.length === 0 && riskItems.length === 0 && (
                                <EmptyState
                                    title="لا توجد عناصر حرجة الآن."
                                    description="الأولوية الحالية مستقرة، ويمكنك الانتقال إلى الخطوة التالية المقترحة."
                                />
                            )}
                        </div>
                    </section>

                    <section className="rounded-[28px] border border-white/10 bg-white/[0.03] p-4">
                        <SectionHeader
                            title="الإجراء التالي المقترح"
                            description="لا تحتاج للبحث بين الصفحات. هذا هو المسار المنطقي التالي بعد إنهاء ما بدأته."
                            icon={CheckCircle2}
                            count={nextItems.length || null}
                        />
                        <div className="mt-4 space-y-3">
                            {recommendedAction && (
                                <ActionCard
                                    title={recommendedAction.title}
                                    description={recommendedAction.subtitle}
                                    reason={recommendedAction.reason}
                                    actionLabel={recommendedAction.nextAction}
                                    actionHref={recommendedAction.href}
                                    actionTone={recommendedAction.tone === 'danger' ? 'danger' : recommendedAction.tone === 'warn' ? 'warn' : 'success'}
                                    onAction={() => {
                                        trackFirstAction(recommendedAction.nextAction, { queue_section: 'recommended', item_id: recommendedAction.id });
                                        trackNextAction('today', recommendedAction.nextAction, {
                                            ...surfaceDetails,
                                            queue_section: 'recommended',
                                            item_id: recommendedAction.id,
                                            workflow_label: recommendedAction.workflowLabel,
                                            target_href: recommendedAction.href,
                                        });
                                    }}
                                    meta={
                                        <>
                                            <StatusBadge tone="info">{recommendedAction.workflowLabel}</StatusBadge>
                                            {recommendedAction.timestamp && (
                                                <StatusBadge tone="default">{new Date(recommendedAction.timestamp).toLocaleDateString('ar-DZ')}</StatusBadge>
                                            )}
                                        </>
                                    }
                                />
                            )}

                            {nextItems.slice(0, 2).map((item) => renderQueueCard(item, 'next'))}

                            {(eventSummaryItems.length > 0 || (eventReminders?.t6 || []).length > 0 || (eventReminders?.t24 || []).length > 0) && (
                                <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
                                    <div className="flex items-center justify-between gap-3">
                                        <div>
                                            <h3 className="text-sm font-semibold text-white">ملخص تشغيلي للأحداث</h3>
                                            <p className="mt-1 text-[11px] leading-6 text-slate-400">حتى لا تضيع المواعيد القريبة خارج صفحة اليوم.</p>
                                        </div>
                                        <Link
                                            href="/events"
                                            onClick={() =>
                                                trackMetricEvent('today', 'open_events_from_today', {
                                                    ...surfaceDetails,
                                                    source: 'event_summary',
                                                })
                                            }
                                            className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-[11px] text-slate-200 hover:text-white"
                                        >
                                            فتح مكتب الأحداث
                                        </Link>
                                    </div>
                                    <div className="mt-3 flex flex-wrap gap-2">
                                        {eventSummaryItems.map((item) => (
                                            <StatusBadge key={item.label} tone={item.tone}>
                                                {item.label}: {item.value}
                                            </StatusBadge>
                                        ))}
                                    </div>
                                    {(eventReminders?.t6 || [])[0] && (
                                        <div className="mt-3 rounded-xl border border-amber-500/20 bg-amber-500/10 px-3 py-3 text-xs text-amber-100">
                                            <p className="font-semibold">أقرب حدث يتحرك الآن</p>
                                            <p className="mt-1">{eventReminders?.t6?.[0]?.title}</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </section>
                </div>
            )}
        </div>
    );
}
