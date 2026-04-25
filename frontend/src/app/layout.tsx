import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { AuthProvider } from "@/lib/auth";
import AppShell from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "Echorouk Editorial OS | The Intelligent Newsroom Operating System",
  description:
    "Echorouk Editorial OS is a newsroom operating system that manages the editorial lifecycle from signal capture to Ready for Manual Publish, with strict governance and mandatory Human-in-the-Loop.",
  keywords: ["echorouk", "editorial", "newsroom", "algeria", "workflows", "governance"],
  authors: [{ name: "Echorouk Editorial OS Team" }],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl">
      <body className="min-h-screen app-main-shell antialiased">
        <Providers>
          <AuthProvider>
            <AppShell>{children}</AppShell>
          </AuthProvider>
        </Providers>
      </body>
    </html>
  );
}

