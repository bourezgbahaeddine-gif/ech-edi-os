'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Activity, ShieldCheck } from 'lucide-react';

import { dashboardApi, newsApi } from '@/lib/api';
import StatsCards from '@/components/dashboard/StatsCards';
import NewsFeed from '@/components/dashboard/NewsFeed';
import PipelineMonitor from '@/components/dashboard/PipelineMonitor';
import AgentControl from '@/components/dashboard/AgentControl';
import MsiWidget from '@/components/dashboard/MsiWidget';
import CompetitorXrayWidget from '@/components/dashboard/CompetitorXrayWidget';
import TimeIntegrityWidget from '@/components/dashboard/TimeIntegrityWidget';
import { useAuth } from '@/lib/auth';
import { PageHeader, StatusBadge } from '@/components/ux/SurfacePrimitives';

export default function DashboardPage() {
    const router = useRouter();
    const { user } = useAuth();
    const role = (user?.role || '').toLowerCase();
    const isDirectorView = role === 'director';

    const { data: statsData, isLoading: statsLoading } = useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: () => dashboardApi.stats(),
        refetchInterval: 20_000,
        refetchOnWindowFocus: true,
        enabled: isDirectorView,
    });

    const { data: breakingData, isLoading: breakingLoading } = useQuery({
        queryKey: ['breaking-news'],
        queryFn: () => newsApi.breaking(5),
        refetchInterval: 12_000,
        refetchOnWindowFocus: true,
        enabled: isDirectorView,
    });

    const { data: pendingData, isLoading: pendingLoading } = useQuery({
        queryKey: ['pending-articles'],
        queryFn: () => newsApi.pending(10),
        refetchInterval: 15_000,
        refetchOnWindowFocus: true,
        enabled: isDirectorView,
    });

    const { data: pipelineData, isLoading: pipelineLoading } = useQuery({
        queryKey: ['pipeline-runs'],
        queryFn: () => dashboardApi.pipelineRuns(10),
        refetchInterval: 15_000,
        refetchOnWindowFocus: true,
        enabled: isDirectorView,
    });

    const { data: agentsData } = useQuery({
        queryKey: ['agents-status'],
        queryFn: () => dashboardApi.agentStatus(),
        refetchInterval: 20_000,
        refetchOnWindowFocus: true,
        enabled: isDirectorView,
    });

    useEffect(() => {
        if (user && !isDirectorView) {
            router.replace('/today');
        }
    }, [isDirectorView, router, user]);

    if (user && !isDirectorView) {
        return (
            <div className="rounded-2xl border app-surface p-8 text-center app-text-muted">
                جاري تحويلك إلى مساحة العمل اليومية...
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <PageHeader
                eyebrow="طبقة المدير"
                title="لوحة الأداء التشغيلية"
                icon={Activity}
                description="هذه شاشة المتابعة الإدارية العليا: صحة المنصة، تدفق الأخبار، مؤشرات التشغيل، والعوامل التي قد تعطل غرفة الأخبار. تبقى منفصلة عن تجربة الصحفي اليومية."
                meta={
                    <>
                        <StatusBadge tone="info">تشغيل وإدارة</StatusBadge>
                        <StatusBadge tone="warn">ليست واجهة العمل اليومي للصحفي</StatusBadge>
                    </>
                }
                actions={
                    <a
                        href="/dashboard"
                        className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-200 hover:text-white"
                    >
                        <ShieldCheck className="h-4 w-4" />
                        فتح لوحة الاستخبارات التنفيذية
                    </a>
                }
            />

            <div className="animate-fade-in-up" style={{ animationDelay: '100ms' }}>
                <StatsCards stats={statsData?.data} isLoading={statsLoading} />
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                <div className="space-y-6 lg:col-span-2">
                    <div className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
                        <NewsFeed articles={breakingData?.data} isLoading={breakingLoading} title="أخبار عاجلة" />
                    </div>

                    <div className="animate-fade-in-up" style={{ animationDelay: '300ms' }}>
                        <NewsFeed articles={pendingData?.data} isLoading={pendingLoading} title="بانتظار المراجعة" />
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="animate-fade-in-up" style={{ animationDelay: '250ms' }}>
                        <AgentControl agents={agentsData?.data} />
                    </div>

                    <div className="animate-fade-in-up" style={{ animationDelay: '300ms' }}>
                        <MsiWidget />
                    </div>

                    <div className="animate-fade-in-up" style={{ animationDelay: '380ms' }}>
                        <PipelineMonitor runs={pipelineData?.data} isLoading={pipelineLoading} />
                    </div>

                    <div className="animate-fade-in-up" style={{ animationDelay: '400ms' }}>
                        <TimeIntegrityWidget />
                    </div>

                    <div className="animate-fade-in-up" style={{ animationDelay: '420ms' }}>
                        <CompetitorXrayWidget />
                    </div>
                </div>
            </div>
        </div>
    );
}
