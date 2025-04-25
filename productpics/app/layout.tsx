import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { cn } from "@/lib/utils";
import { Header } from "@/src/components/layout/header"; // Assuming this path
import { Footer } from "@/src/components/layout/footer"; // Import Footer
import { ThemeProvider } from "@/src/components/theme-provider"; // Import ThemeProvider
import { Toaster } from "@/components/ui/sonner"; // Import Toaster
import "./globals.css";

const fontSans = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "PixelChat - AI Product Photo Editing",
  description: "Transform product images into professional, high-converting visuals with AI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          fontSans.variable
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <Header />
          {children}
          <Footer />
          <Toaster />
        </ThemeProvider>
        {/* TODO: Add Analytics */}
      </body>
    </html>
  );
}
