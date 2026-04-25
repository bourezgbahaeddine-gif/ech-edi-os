'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { CheckCircle, FileText } from 'lucide-react';

import { constitutionApi } from '@/lib/constitution-api';
import { useAuth } from '@/lib/auth';
import { cn } from '@/lib/utils';
import CommandPalette from '@/components/layout/CommandPalette';
import Sidebar from '@/components/layout/Sidebar';
import TopBar from '@/components/layout/TopBar';
import { UxShellModeProvider, useUxShellMode } from '@/components/layout/UxShellModeContext';

const PUBLIC_PATHS = ['/login'];

export default function AppShell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const isPublic = PUBLIC_PATHS.includes(pathname);

    if (isPublic) return <>{children}</>;

    return (
        <UxShellModeProvider>
            <AppShellChrome>{children}</AppShellChrome>
        </UxShellModeProvider>
    );
}

function AppShellChrome({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const { user } = useAuth();
    const { mode } = useUxShellMode();
    const chromeHidden = mode === 'focus' || mode === 'emergency' || mode === 'deep_work';
    const queryClient = useQueryClient();

    const [ack, setAck] = useState(false);
    const [ackDismissed, setAckDismissed] = useState(false);
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
    const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
    const [theme, setTheme] = useState<'light' | 'dark'>(() => {
        if (typeof window === 'undefined') return 'light';
        return localStorage.getItem('ech_theme') === 'dark' ? 'dark' : 'light';
    });

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        if (typeof window !== 'undefined') {
            localStorage.setItem('ech_theme', theme);
        }
    }, [theme]);

    useEffect(() => {
        if (pathname.startsWith('/workspace-drafts')) return;
        const handler = (event: KeyboardEvent) => {
            const target = event.target as HTMLElement | null;
            const isInput = target?.tagName === 'INPUT' || target?.tagName === 'TEXTAREA' || Boolean(target?.isContentEditable);
            if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k' && !isInput) {
                event.preventDefault();
                setCommandPaletteOpen(true);
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [pathname]);

    const toggleTheme = () => {
        setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
    };

    const { data: latest } = useQuery({
        queryKey: ['constitution-latest'],
        queryFn: () => constitutionApi.latest(),
    });

    const { data: ackStatus } = useQuery({
        queryKey: ['constitution-ack'],
        queryFn: () => constitutionApi.ackStatus(),
        enabled: !!user,
    });

    const ackMutation = useMutation({
        mutationFn: (version: string) => constitutionApi.acknowledge(version),
        onSuccess: async () => {
            setAckDismissed(true);
            await queryClient.invalidateQueries({ queryKey: ['constitution-ack'] });
        },
    });

    const shouldShowConstitutionGate = Boolean(
        !ackDismissed &&
            user &&
            latest?.data &&
            ackStatus?.data &&
            !ackStatus.data.acknowledged,
    );

    const confirm = () => {
        const version = latest?.data?.version;
        if (!version) return;
        ackMutation.mutate(version);
    };

    return (
        <div className={cn('flex overflow-x-hidden app-theme-shell', chromeHidden && 'bg-[#020817]')}>
            {!chromeHidden && (
                <Sidebar
                    collapsed={sidebarCollapsed}
                    onToggleCollapsed={() => setSidebarCollapsed((prev) => !prev)}
                    mobileOpen={chromeHidden ? false : mobileSidebarOpen}
                    onCloseMobile={() => setMobileSidebarOpen(false)}
                />
            )}

            <main
                className={cn(
                    'min-h-screen min-w-0 flex-1 overflow-x-hidden transition-all duration-300',
                    chromeHidden ? 'md:mr-0' : sidebarCollapsed ? 'md:mr-[72px]' : 'md:mr-[260px]',
                )}
            >
                {!chromeHidden && (
                    <TopBar
                        theme={theme}
                        onToggleTheme={toggleTheme}
                        onOpenSidebar={() => setMobileSidebarOpen(true)}
                        onOpenCommandPalette={() => setCommandPaletteOpen(true)}
                    />
                )}
                <div className={cn('min-h-[calc(100vh-64px)] mesh-gradient', chromeHidden ? 'p-0' : 'p-3 md:p-6')}>{children}</div>
            </main>

            <CommandPalette open={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />

            {shouldShowConstitutionGate && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
                    <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-gray-900/90 p-6 app-surface">
                        <div className="mb-3 flex items-center gap-2 text-white">
                            <FileText className="h-5 w-5 text-emerald-400" />
                            <h2 className="text-lg font-semibold">تأكيد قراءة الدستور</h2>
                        </div>
                        <p className="text-sm leading-relaxed text-gray-300">
                            الدستور التحريري هو المرجع الإلزامي لجميع المراحل. يرجى الاطلاع عليه قبل المتابعة.
                        </p>
                        <div className="mt-3">
                            <a href="/constitution" className="text-sm text-emerald-300 underline hover:text-emerald-200" target="_blank" rel="noreferrer">
                                فتح الدستور
                            </a>
                        </div>
                        <label className="mt-4 flex items-center gap-2 text-sm text-gray-300">
                            <input
                                type="checkbox"
                                checked={ack}
                                onChange={(event) => setAck(event.target.checked)}
                                className="accent-emerald-500"
                            />
                            أقر أنني قرأت الدستور وسألتزم به
                        </label>
                        <button
                            onClick={confirm}
                            disabled={!ack || ackMutation.isPending}
                            className="mt-4 flex h-11 w-full items-center justify-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/20 text-emerald-300 transition-colors hover:bg-emerald-500/30 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <CheckCircle className="h-4 w-4" />
                            متابعة
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
