'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { Activity, ChevronDown, ChevronLeft, ChevronRight, Wrench } from 'lucide-react';

import { useAuth } from '@/lib/auth';
import { cn } from '@/lib/utils';
import {
    getPrimaryNav,
    getSecondaryNav,
    normalizeRole,
    showSecondarySidebar,
    type NavItem,
} from '@/components/layout/navigation';

type SidebarProps = {
    collapsed: boolean;
    onToggleCollapsed: () => void;
    mobileOpen: boolean;
    onCloseMobile: () => void;
};

export default function Sidebar({
    collapsed,
    onToggleCollapsed,
    mobileOpen,
    onCloseMobile,
}: SidebarProps) {
    const pathname = usePathname();
    const { user } = useAuth();
    const role = normalizeRole(user?.role || '');
    const [secondaryOpen, setSecondaryOpen] = useState(false);

    const primaryItems = useMemo(() => getPrimaryNav(role), [role]);
    const secondarySections = useMemo(() => getSecondaryNav(role), [role]);
    const allowSecondarySidebar = showSecondarySidebar(role);

    const renderNavItem = (item: NavItem) => {
        const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
        const label = (role && item.roleLabels?.[role]) || item.shortLabel || item.label;

        return (
            <Link
                key={`${item.section}-${item.href}`}
                href={item.href}
                onClick={onCloseMobile}
                className={cn(
                    'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all duration-200',
                    isActive ? 'bg-blue-500/20 text-[#F8FAFC] shadow-inner' : 'text-[#CBD5E1] hover:bg-white/8 hover:text-[#F8FAFC]',
                )}
                title={item.label}
            >
                {isActive && <div className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-[#2563EB]" />}
                <item.icon className={cn('h-5 w-5 shrink-0', isActive && 'drop-shadow-[0_0_6px_rgba(37,99,235,0.5)]')} />
                {!collapsed && <span className="text-sm font-medium">{label}</span>}
            </Link>
        );
    };

    return (
        <>
            <button
                type="button"
                aria-label="Close sidebar overlay"
                onClick={onCloseMobile}
                className={cn(
                    'fixed inset-0 z-40 bg-black/55 backdrop-blur-[1px] transition-opacity md:hidden',
                    mobileOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0',
                )}
            />
            <aside
                className={cn(
                    'fixed right-0 top-0 z-50 flex h-screen flex-col border-l border-slate-800/70 bg-[#0F172A] transition-all duration-300 ease-in-out',
                    'w-[86vw] max-w-[280px] md:w-auto',
                    collapsed ? 'md:w-[72px]' : 'md:w-[260px]',
                    mobileOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0',
                )}
            >
                <div className="flex h-16 items-center gap-3 border-b border-white/10 px-4">
                    <div className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-xl border border-white/15 bg-white/5">
                        <Image src="/ech-logo.png" alt="Echorouk" width={28} height={28} className="h-7 w-7 object-contain" />
                    </div>
                    {!collapsed && (
                        <div className="overflow-hidden">
                            <h1 className="truncate text-sm font-bold text-[#F8FAFC]">Echorouk Editorial OS</h1>
                            <p className="text-[10px] font-medium text-[#CBD5E1]">غرفة تحرير الشروق الذكية</p>
                        </div>
                    )}
                </div>

                <nav className="flex-1 overflow-y-auto px-2 py-4">
                    <div className="space-y-1">{primaryItems.map(renderNavItem)}</div>

                    {!allowSecondarySidebar && !collapsed && (
                        <div className="mt-5 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-3 py-3 text-right">
                            <div className="text-xs font-medium text-cyan-100">أدوات إضافية عند الحاجة</div>
                            <p className="mt-1 text-[11px] leading-5 text-cyan-50/80">
                                بقية الصفحات موجودة في <span className="font-semibold">Command Palette</span> عبر <span className="font-semibold">Ctrl/Cmd + K</span>.
                            </p>
                        </div>
                    )}

                    {allowSecondarySidebar && secondarySections.length > 0 && (
                        <div className="mt-5 border-t border-white/10 pt-4">
                            {!collapsed && (
                                <button
                                    type="button"
                                    onClick={() => setSecondaryOpen((prev) => !prev)}
                                    className="mb-2 flex w-full items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-[#CBD5E1] hover:text-white"
                                >
                                    <span className="inline-flex items-center gap-2">
                                        <Wrench className="h-4 w-4" />
                                        المزيد من الأدوات
                                    </span>
                                    <ChevronDown className={cn('h-4 w-4 transition-transform', secondaryOpen && 'rotate-180')} />
                                </button>
                            )}

                            {(collapsed || secondaryOpen) && (
                                <div className="space-y-4">
                                    {secondarySections.map((section) => (
                                        <div key={section.key}>
                                            {!collapsed && (
                                                <div className="px-3 pb-1 text-[10px] uppercase tracking-[0.18em] text-[#64748B]">
                                                    {section.label}
                                                </div>
                                            )}
                                            <div className="space-y-1">{section.items.map(renderNavItem)}</div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </nav>

                {!collapsed && (
                    <div className="mx-2 mb-3 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3">
                        <div className="flex items-center gap-2">
                            <Activity className="h-4 w-4 text-[#2563EB]" />
                            <span className="text-xs text-[#CBD5E1]">النظام يعمل</span>
                            <span className="mr-auto h-2 w-2 animate-pulse rounded-full bg-[#2563EB]" />
                        </div>
                    </div>
                )}

                <button
                    onClick={onToggleCollapsed}
                    className="hidden h-10 items-center justify-center border-t border-white/10 text-[#94A3B8] transition-colors hover:text-[#F8FAFC] md:flex"
                >
                    {collapsed ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                </button>
            </aside>
        </>
    );
}
