"use client"

import { useSession } from "next-auth/react"
import { useRouter } from "next/router"
import { useEffect } from "react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { api } from "@/utils/api"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import SettingsForm from "@/components/settings-form"

export default function SettingsPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const { data: settings, isLoading } = api.settings.get.useQuery(undefined, {
    enabled: !!session,
  })

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login")
    }
  }, [status, router])

  if (status === "loading" || isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    )
  }

  if (!session || !settings) {
    return null
  }

  return (
    <div className="container max-w-4xl mx-auto py-8 px-4 bg-background min-h-screen">
      <div className="mb-6">
        <Link href="/chat" className="flex items-center text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft size={16} className="mr-1" /> Back to Chat
        </Link>
      </div>

      <h1 className="text-2xl font-bold mb-6 text-foreground">Settings</h1>

      <Tabs defaultValue="user" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6 bg-secondary">
          <TabsTrigger value="user" className="data-[state=active]:bg-background">
            User Settings
          </TabsTrigger>
          <TabsTrigger value="account" className="data-[state=active]:bg-background">
            Account
          </TabsTrigger>
        </TabsList>

        <TabsContent value="user" className="space-y-6">
          <div className="bg-background border border-border rounded-lg shadow-sm p-6">
            <SettingsForm user={session.user} initialSettings={settings} />
          </div>
        </TabsContent>

        <TabsContent value="account" className="space-y-6">
          <div className="bg-background border border-border rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Account Information</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="text-foreground">{session.user.name || "Not set"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="text-foreground">{session.user.email}</p>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
