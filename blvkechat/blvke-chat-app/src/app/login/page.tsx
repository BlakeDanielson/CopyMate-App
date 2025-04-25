import { redirect } from "next/navigation"
import { getCurrentUser } from "@/lib/auth"
import LoginForm from "@/components/login-form"
import { USE_REAL_DATABASE } from "@/lib/config"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { InfoIcon } from "lucide-react"

export default async function LoginPage() {
  const user = await getCurrentUser()

  if (user) {
    redirect("/chat")
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-foreground">AI Chat</h1>
          <p className="mt-2 text-muted-foreground">Sign in to your account</p>
        </div>

        {!USE_REAL_DATABASE && (
          <Alert className="bg-secondary/50 border-primary/20">
            <InfoIcon className="h-4 w-4 text-primary" />
            <AlertTitle>Test Mode Active</AlertTitle>
            <AlertDescription className="text-muted-foreground">
              The application is running in test mode with a mock database.
              <br />
              You can log in with:
              <br />
              <strong className="text-foreground">Email:</strong> test@example.com
              <br />
              <strong className="text-foreground">Password:</strong> password
            </AlertDescription>
          </Alert>
        )}

        <LoginForm />
      </div>
    </div>
  )
}
