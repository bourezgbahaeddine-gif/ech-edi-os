'use client';

import type { ComponentType } from 'react';
import {
    Activity,
    Archive,
    BookOpen,
    CalendarClock,
    FileSearch,
    FileText,
    Film,
    FolderGit2,
    Gauge,
    HelpCircle,
    KeyRound,
    LayoutDashboard,
    Library,
    Megaphone,
    MessagesSquare,
    Mic2,
    MousePointerClick,
    Newspaper,
    Radar,
    Rss,
    ScrollText,
    ShieldCheck,
    TrendingUp,
    UserCheck,
    Users,
} from 'lucide-react';

export type Role =
    | 'director'
    | 'editor_chief'
    | 'journalist'
    | 'presenter'
    | 'show_host'
    | 'social_media'
    | 'print_editor'
    | 'fact_checker'
    | 'observer';

export type NavSection = 'primary' | 'knowledge' | 'tools' | 'ops';

export type NavItem = {
    href: string;
    label: string;
    shortLabel?: string;
    description?: string;
    icon: ComponentType<{ className?: string }>;
    roles: Role[];
    section: NavSection;
    roleLabels?: Partial<Record<Role, string>>;
};

export function normalizeRole(role: string): Role | null {
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

export const navItems: NavItem[] = [
    {
        href: '/today',
        label: 'اليوم',
        description: 'نقطة البداية اليومية والإجراء التالي المقترح.',
        icon: LayoutDashboard,
        roles: ['director', 'editor_chief', 'journalist', 'presenter', 'show_host', 'social_media', 'print_editor', 'fact_checker', 'observer'],
        section: 'primary',
    },
    {
        href: '/',
        label: 'لوحة الأداء',
        shortLabel: 'الأداء',
        description: 'لوحة تشغيل وإدارة للمدير.',
        icon: Gauge,
        roles: ['director'],
        section: 'primary',
    },
    {
        href: '/dashboard',
        label: 'لوحة المؤشرات',
        shortLabel: 'المؤشرات',
        description: 'لوحة ذكاء تنفيذية للمدير.',
        icon: LayoutDashboard,
        roles: ['director'],
        section: 'ops',
    },
    {
        href: '/news',
        label: 'الأخبار',
        description: 'طابور الأخبار والتحرير السريع.',
        icon: Newspaper,
        roles: ['director', 'editor_chief', 'journalist', 'presenter', 'social_media', 'print_editor', 'fact_checker'],
        section: 'primary',
    },
    {
        href: '/workspace-drafts',
        label: 'الكتابة والمسودات',
        shortLabel: 'المسودات',
        description: 'مساحة العمل الأساسية للكتابة والتحقق والجاهزية.',
        icon: FolderGit2,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'primary',
    },
    {
        href: '/editorial',
        label: 'الاعتماد والتحرير',
        shortLabel: 'الاعتماد',
        description: 'طابور القرارات التحريرية والمواد الجاهزة للاعتماد.',
        icon: UserCheck,
        roles: ['director', 'editor_chief', 'social_media'],
        section: 'primary',
        roleLabels: {
            social_media: 'نشر واعتماد',
        },
    },
    {
        href: '/stories',
        label: 'القصص',
        description: 'المتابعة السياقية والخطوط التحريرية المستمرة.',
        icon: Library,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'primary',
    },
    {
        href: '/events',
        label: 'التغطيات والأحداث',
        shortLabel: 'التغطيات',
        description: 'جدول الأحداث والمتابعات الميدانية.',
        icon: CalendarClock,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'primary',
    },
    {
        href: '/digital',
        label: 'التغطية الرقمية',
        description: 'غرفة توزيع وتكييف المحتوى الرقمي.',
        icon: Megaphone,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'primary',
    },
    {
        href: '/archive',
        label: 'الأرشيف',
        description: 'الرجوع إلى المواد السابقة والمراجع المنشورة.',
        icon: Archive,
        roles: ['director', 'editor_chief', 'journalist', 'presenter', 'show_host', 'social_media', 'print_editor', 'fact_checker'],
        section: 'knowledge',
    },
    {
        href: '/memory',
        label: 'الذاكرة التحريرية',
        description: 'مساحة الذاكرة التحريرية والدروس المتراكمة.',
        icon: BookOpen,
        roles: ['director', 'editor_chief', 'journalist', 'show_host', 'social_media', 'print_editor'],
        section: 'knowledge',
    },
    {
        href: '/constitution',
        label: 'الدستور التحريري',
        description: 'مرجع السياسات التحريرية والحوكمة.',
        icon: FileText,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor', 'fact_checker', 'observer'],
        section: 'knowledge',
    },
    {
        href: '/help',
        label: 'مركز المساعدة',
        description: 'شرح المنصة ومسارات العمل.',
        icon: HelpCircle,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor', 'fact_checker', 'observer'],
        section: 'knowledge',
    },
    {
        href: '/services/document-intel',
        label: 'تحليل الوثائق',
        description: 'استخراج ومعالجة محتوى الوثائق.',
        icon: FileSearch,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'tools',
    },
    {
        href: '/services/media-logger',
        label: 'تفريغ التسجيلات',
        description: 'تحويل الصوت إلى نص وسجل مراجعة.',
        icon: Mic2,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'tools',
    },
    {
        href: '/services/multimedia',
        label: 'الوسائط',
        description: 'خدمات الصور والإنفوغراف والميديا.',
        icon: Film,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'tools',
    },
    {
        href: '/services/fact-check',
        label: 'التحقق والاستقصاء',
        description: 'أدوات التحقق السريع والاستقصاء.',
        icon: ShieldCheck,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'fact_checker', 'print_editor'],
        section: 'tools',
    },
    {
        href: '/scripts',
        label: 'السكربت',
        description: 'بناء النصوص والسيناريوهات التحريرية.',
        icon: ScrollText,
        roles: ['director', 'editor_chief', 'journalist', 'presenter', 'show_host', 'social_media', 'print_editor'],
        section: 'tools',
    },
    {
        href: '/trends',
        label: 'الترندات',
        description: 'رصد الاهتمامات والزخم اليومي.',
        icon: TrendingUp,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'tools',
    },
    {
        href: '/simulator',
        label: 'محاكاة التفاعل',
        description: 'اختبار تأثير العناوين والنسخ قبل النشر.',
        icon: MessagesSquare,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'tools',
    },
    {
        href: '/competitor-xray',
        label: 'رصد المنافسين',
        description: 'تحليل المشهد التنافسي والتحركات المقارنة.',
        icon: Radar,
        roles: ['director', 'editor_chief', 'journalist', 'social_media', 'print_editor'],
        section: 'tools',
    },
    {
        href: '/ux-insights',
        label: 'سلوك الاستخدام',
        description: 'مؤشرات UX واعتماد الأنماط التشغيلية.',
        icon: MousePointerClick,
        roles: ['director', 'editor_chief'],
        section: 'ops',
    },
    {
        href: '/team',
        label: 'فريق التحرير',
        description: 'إدارة فريق التحرير والأدوار.',
        icon: Users,
        roles: ['director'],
        section: 'ops',
    },
    {
        href: '/sources',
        label: 'المصادر',
        description: 'إدارة المصادر والتغذيات.',
        icon: Rss,
        roles: ['director'],
        section: 'ops',
    },
    {
        href: '/agents',
        label: 'مراقبة النظام',
        description: 'مراقبة الوكلاء والبنية التشغيلية.',
        icon: Activity,
        roles: ['director'],
        section: 'ops',
    },
    {
        href: '/settings',
        label: 'إعدادات APIs',
        description: 'إدارة الإعدادات والتكاملات.',
        icon: KeyRound,
        roles: ['director'],
        section: 'ops',
    },
];

export const sectionLabels: Array<{ key: Exclude<NavSection, 'primary'>; label: string }> = [
    { key: 'knowledge', label: 'معرفة مساندة' },
    { key: 'tools', label: 'أدوات إضافية' },
    { key: 'ops', label: 'تشغيل وإدارة' },
];

const rolePrimaryOrder: Record<Role, string[]> = {
    director: ['/', '/dashboard', '/today', '/news', '/workspace-drafts', '/editorial', '/stories', '/events'],
    editor_chief: ['/today', '/editorial', '/news', '/workspace-drafts', '/stories', '/events', '/ux-insights'],
    journalist: ['/today', '/workspace-drafts', '/news', '/memory', '/stories'],
    presenter: ['/today', '/news', '/scripts', '/archive'],
    show_host: ['/today', '/scripts', '/archive', '/memory'],
    social_media: ['/today', '/workspace-drafts', '/news', '/digital', '/stories'],
    print_editor: ['/today', '/workspace-drafts', '/news', '/archive', '/stories'],
    fact_checker: ['/today', '/news', '/memory', '/services/fact-check', '/help'],
    observer: ['/today', '/help', '/constitution'],
};

export function getVisibleNav(role: Role | null): NavItem[] {
    return role ? navItems.filter((item) => item.roles.includes(role)) : [];
}

export function getPrimaryNav(role: Role | null): NavItem[] {
    if (!role) return [];
    const visible = getVisibleNav(role);
    const order = rolePrimaryOrder[role] || [];
    const byHref = new Map(visible.map((item) => [item.href, item]));
    const ordered = order.map((href) => byHref.get(href)).filter(Boolean) as NavItem[];
    const orderedHrefs = new Set(ordered.map((item) => item.href));
    const fallbacks = visible.filter((item) => item.section === 'primary' && !orderedHrefs.has(item.href));
    return [...ordered, ...fallbacks];
}

export function getSecondaryNav(role: Role | null): Array<{ key: Exclude<NavSection, 'primary'>; label: string; items: NavItem[] }> {
    if (!role) return [];
    const visible = getVisibleNav(role);
    const primaryHrefs = new Set(getPrimaryNav(role).map((item) => item.href));
    return sectionLabels
        .map((section) => ({
            ...section,
            items: visible.filter((item) => item.section === section.key && !primaryHrefs.has(item.href)),
        }))
        .filter((section) => section.items.length > 0);
}

export function showSecondarySidebar(role: Role | null): boolean {
    return role === 'director' || role === 'editor_chief';
}
