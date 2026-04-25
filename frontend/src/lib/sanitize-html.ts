import DOMPurify from 'dompurify';

const ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u',
    'h1', 'h2', 'h3',
    'ul', 'ol', 'li',
    'blockquote',
    'a',
    'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
];

const ALLOWED_ATTR = [
    'href',
    'src',
    'alt',
    'title',
    'target',
    'rel',
    'colspan',
    'rowspan',
    'scope',
];

let hooksRegistered = false;

function stripShellTags(html: string): string {
    return String(html || '')
        .replace(/<\/?(html|head|body|meta|title|link|doctype)[^>]*>/gi, '')
        .trim();
}

function isSafeUrl(value: string, allowImageData = false): boolean {
    const normalized = (value || '').trim().toLowerCase();
    if (!normalized) return false;
    if (normalized.startsWith('javascript:')) return false;
    if (normalized.startsWith('data:')) {
        return allowImageData && /^data:image\/(?:png|gif|jpeg|jpg|webp);base64,/i.test(normalized);
    }
    if (
        normalized.startsWith('http://')
        || normalized.startsWith('https://')
        || normalized.startsWith('mailto:')
        || normalized.startsWith('tel:')
        || normalized.startsWith('/')
        || normalized.startsWith('./')
        || normalized.startsWith('../')
        || normalized.startsWith('#')
    ) {
        return true;
    }
    return false;
}

function ensureHooksRegistered() {
    if (hooksRegistered) return;

    DOMPurify.addHook('afterSanitizeAttributes', (node) => {
        if (!node || !('removeAttribute' in node)) return;

        const attributeNames = Array.from((node.attributes || []) as ArrayLike<Attr>).map((attr) => attr.name);
        for (const attrName of attributeNames) {
            if (/^on/i.test(attrName)) {
                node.removeAttribute(attrName);
            }
        }

        if (node.tagName === 'A') {
            const href = node.getAttribute('href') || '';
            if (!isSafeUrl(href)) {
                node.removeAttribute('href');
                node.removeAttribute('target');
            }
            if (node.getAttribute('target') === '_blank') {
                node.setAttribute('rel', 'noopener noreferrer');
            }
        }

        if (node.tagName === 'IMG') {
            const src = node.getAttribute('src') || '';
            if (!isSafeUrl(src, false)) {
                node.removeAttribute('src');
            }
        }
    });

    hooksRegistered = true;
}

export function sanitizeArticleHtml(html: string): string {
    const normalized = stripShellTags(html);
    if (!normalized) return '';

    ensureHooksRegistered();

    return DOMPurify.sanitize(normalized, {
        ALLOWED_TAGS,
        ALLOWED_ATTR,
        FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed'],
        FORBID_ATTR: ['style'],
        ALLOW_DATA_ATTR: false,
        ALLOW_UNKNOWN_PROTOCOLS: false,
        KEEP_CONTENT: true,
    });
}
