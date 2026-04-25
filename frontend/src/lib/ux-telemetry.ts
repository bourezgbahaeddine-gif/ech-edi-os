'use client';

import { useEffect, useRef } from 'react';

import { telemetryApi, type UxTelemetryEventPayload } from '@/lib/api';

type UxDetails = Record<string, unknown>;

function withPagePath(payload: UxTelemetryEventPayload): UxTelemetryEventPayload {
    if (payload.page_path || typeof window === 'undefined') {
        return payload;
    }
    return {
        ...payload,
        page_path: window.location.pathname,
    };
}

export function trackUxEvent(payload: UxTelemetryEventPayload): void {
    if (typeof window === 'undefined') return;
    void telemetryApi.logUxEvent(withPagePath(payload)).catch(() => undefined);
}

export function useTrackSurfaceView(surface: string, details?: UxDetails): void {
    const sentRef = useRef(false);

    useEffect(() => {
        if (sentRef.current) return;
        sentRef.current = true;
        trackUxEvent({
            event_name: 'surface_view',
            surface,
            details,
        });
    }, [surface, details]);
}

export function trackNextAction(surface: string, actionLabel: string, details?: UxDetails): void {
    trackUxEvent({
        event_name: 'next_action_click',
        surface,
        action_label: actionLabel,
        details,
    });
}

export function trackUiAction(surface: string, actionLabel: string, details?: UxDetails): void {
    trackUxEvent({
        event_name: 'ui_action',
        surface,
        action_label: actionLabel,
        details,
    });
}

export function trackModeChange(surface: string, mode: string, details?: UxDetails): void {
    trackUxEvent({
        event_name: 'page_mode_change',
        surface,
        action_label: mode,
        details,
    });
}

export function trackMetricEvent(surface: string, eventName: string, details?: UxDetails): void {
    trackUxEvent({
        event_name: eventName,
        surface,
        details,
    });
}

export function useTrackFirstAction(surface: string, details?: UxDetails) {
    const startedAtRef = useRef<number>(0);
    const sentRef = useRef(false);

    useEffect(() => {
        startedAtRef.current = Date.now();
        sentRef.current = false;
    }, [surface]);

    return (actionLabel: string, extraDetails?: UxDetails) => {
        if (!sentRef.current) {
            sentRef.current = true;
            trackUxEvent({
                event_name: 'time_to_first_action',
                surface,
                action_label: actionLabel,
                details: {
                    ...(details || {}),
                    ...(extraDetails || {}),
                    elapsed_ms: Date.now() - startedAtRef.current,
                },
            });
        }
    };
}
