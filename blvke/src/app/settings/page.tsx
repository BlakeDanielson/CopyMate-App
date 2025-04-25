import { redirect } from "next/navigation"
import { getCurrentUser } from "@/lib/auth"
import { getUserSettings } from "@/lib/settings"
import SettingsForm from "@/components/settings-form"
import DatabaseModeToggle from "@/components/database-mode-toggle"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default async function SettingsPage() {
  const user = await getCurrentUser()

  if (!user) {
    redirect("/login")
  }

  const settings = await getUserSettings(user.id)

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
          <TabsTrigger value="system" className="data-[state=active]:bg-background">
            System Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="user" className="space-y-6">
          <div className="bg-background border border-border rounded-lg shadow-sm p-6">
            <SettingsForm user={user} initialSettings={settings} />
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          <DatabaseModeToggle />
        </TabsContent>
      </Tabs>
    </div>
  )
}
