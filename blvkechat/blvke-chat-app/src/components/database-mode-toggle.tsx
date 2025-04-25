"use client"

import { useState, useEffect } from "react"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { USE_REAL_DATABASE } from "@/lib/config"

export default function DatabaseModeToggle() {
  const [isRealDb, setIsRealDb] = useState(USE_REAL_DATABASE)
  const [isClient, setIsClient] = useState(false)

  // This ensures the component only renders on the client
  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient) {
    return null
  }

  return (
    <Card className="w-full max-w-md mx-auto bg-background border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Database Mode</CardTitle>
        <CardDescription className="text-muted-foreground">
          Toggle between test mode (mock database) and production mode (real database)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div>
            <Label htmlFor="db-mode" className="text-base text-foreground">
              {isRealDb ? "Production Mode (Real Database)" : "Test Mode (Mock Database)"}
            </Label>
            <p className="text-sm text-muted-foreground">
              {isRealDb ? "Using Neon PostgreSQL database" : "Using in-memory mock database with test data"}
            </p>
          </div>
          <Switch
            id="db-mode"
            checked={isRealDb}
            onCheckedChange={(checked) => {
              setIsRealDb(checked)
              // In a real implementation, this would update the config
              // For demo purposes, we'll just show an alert
              alert(
                `This would switch to ${
                  checked ? "production mode (real database)" : "test mode (mock database)"
                }. In a real implementation, this would update the config.ts file.`,
              )
            }}
          />
        </div>
        {isRealDb ? (
          <p className="mt-4 text-sm text-amber-500">
            Note: Production mode requires a real Neon database connection. Make sure your DATABASE_URL environment
            variable is set.
          </p>
        ) : (
          <p className="mt-4 text-sm text-emerald-500">
            Test mode is active. You can log in with test@example.com / password
          </p>
        )}
      </CardContent>
    </Card>
  )
}
