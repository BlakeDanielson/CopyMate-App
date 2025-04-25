import type { Session } from "next-auth"
import { SessionProvider } from "next-auth/react"
import type { AppType } from "next/app"
import { api } from "@/utils/api"
import { ThemeProvider } from "next-themes"
import "@/styles/globals.css"

const MyApp: AppType<{ session: Session | null }> = ({ Component, pageProps: { session, ...pageProps } }) => {
  return (
    <SessionProvider session={session}>
      <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
        <Component {...pageProps} />
      </ThemeProvider>
    </SessionProvider>
  )
}

export default api.withTRPC(MyApp)
