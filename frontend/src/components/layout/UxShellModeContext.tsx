'use client';

import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

export type UxShellMode = 'normal' | 'focus' | 'emergency' | 'deep_work';

type UxShellModeContextValue = {
    mode: UxShellMode;
    setMode: (mode: UxShellMode) => void;
};

const UxShellModeContext = createContext<UxShellModeContextValue>({
    mode: 'normal',
    setMode: () => undefined,
});

export function UxShellModeProvider({ children }: { children: ReactNode }) {
    const [mode, setMode] = useState<UxShellMode>('normal');
    const value = useMemo(() => ({ mode, setMode }), [mode]);
    return <UxShellModeContext.Provider value={value}>{children}</UxShellModeContext.Provider>;
}

export function useUxShellMode() {
    return useContext(UxShellModeContext);
}
