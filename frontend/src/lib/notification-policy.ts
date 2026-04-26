'use client';

import type { DashboardNotification } from '@/lib/api';

type Role = 'director' | 'editor_chief' | 'journalist' | 'presenter' | 'show_host' | 'social_media' | 'print_editor' | 'fact_checker' | 'observer' | 'guest';
export type NotificationInterruptionLevel = 'interrupt_now' | 'defer' | 'batch' | 'hidden_from_role';

export function normalizeUxRole(role: string | null | undefined): Role {
    const value = String(role || '').trim().toLowerCase();
    if (value === 'chief_editor' || value === 'editor-chief' || value === 'editor_in_chief') return 'editor_chief';
    if (
        value === 'director' ||
        value === 'editor_chief' ||
        value === 'journalist' ||
        value === 'presenter' ||
        value === 'show_host' ||
        value === 'social_media' ||
        value === 'print_editor' ||
        value === 'fact_checker' ||
        value === 'observer'
    ) {
        return value;
    }
    return 'guest';
}

export function classifyNotificationInterruption(
    item: DashboardNotification,
    roleValue: string | null | undefined,
): NotificationInterruptionLevel {
    const role = normalizeUxRole(roleValue);
    const type = String(item.type || '').toLowerCase();
    const severity = String(item.severity || '').toLowerCase();

    if (role === 'journalist' || role === 'presenter' || role === 'show_host' || role === 'social_media' || role === 'print_editor' || role === 'fact_checker') {
        if (type === 'published_quality') return 'hidden_from_role';
    }

    if (type === 'breaking' || severity === 'high') return 'interrupt_now';
    if (type === 'candidate' || severity === 'medium') return 'defer';
    return 'batch';
}

export function filterNotificationsForRole(
    items: DashboardNotification[],
    roleValue: string | null | undefined,
): DashboardNotification[] {
    return items.filter((item) => classifyNotificationInterruption(item, roleValue) !== 'hidden_from_role');
}

export function interruptionLabel(level: NotificationInterruptionLevel): string {
    if (level === 'interrupt_now') return 'يصل الآن';
    if (level === 'defer') return 'يؤجل قليلًا';
    if (level === 'batch') return 'دفعة مجمعة';
    return 'مخفي عن هذا الدور';
}
