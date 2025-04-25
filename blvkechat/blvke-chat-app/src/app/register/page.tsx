import { redirect } from "next/navigation"
import { getCurrentUser } from "@/lib/auth"
import RegisterForm from "@/components/register-form"

export default async function RegisterPage() {
  const user = await getCurrentUser()

  if (user) {
    redirect("/chat")
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-foreground">Create an account</h1>
          <p className="mt-2 text-muted-foreground">Sign up to get started</p>
        </div>
        <RegisterForm />
      </div>
    </div>
  )
}
