"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { api } from "@/utils/api"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { useToast } from "@/components/ui/use-toast"

interface SettingsFormProps {
  user: {
    id: string
    name?: string | null
    email?: string | null
    image?: string | null
  }
  initialSettings: {
    id: string
    modelName: string
    temperature: number
    maxTokens: number
    theme: string
    fontSize: string
  }
}

export default function SettingsForm({ user, initialSettings }: SettingsFormProps) {
  const { toast } = useToast()
  const [settings, setSettings] = useState(initialSettings)
  const [loading, setLoading] = useState(false)

  const updateSettings = api.settings.update.useMutation({
    onSuccess: () => {
      toast({
        title: "Settings updated",
        description: "Your settings have been saved successfully.",
      })
      setLoading(false)
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update settings. Please try again.",
        variant: "destructive",
      })
      setLoading(false)
    },
  })

  const handleChange = (field: string, value: string | number) => {
    setSettings((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    updateSettings.mutate({
      modelName: settings.modelName,
      temperature: settings.temperature,
      maxTokens: settings.maxTokens,
      theme: settings.theme,
      fontSize: settings.fontSize,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Tabs defaultValue="model" className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-secondary">
          <TabsTrigger value="model" className="data-[state=active]:bg-background">
            AI Model
          </TabsTrigger>
          <TabsTrigger value="interface" className="data-[state=active]:bg-background">
            Interface
          </TabsTrigger>
        </TabsList>

        <TabsContent value="model" className="space-y-4 pt-4">
          <Card className="bg-background border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Model Settings</CardTitle>
              <CardDescription className="text-muted-foreground">
                Configure the AI model behavior to customize your chat experience
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="modelName" className="text-foreground">
                  Model
                </Label>
                <Select value={settings.modelName} onValueChange={(value) => handleChange("modelName", value)}>
                  <SelectTrigger id="modelName" className="bg-secondary/50 border-border text-foreground">
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent className="bg-background border-border">
                    <SelectItem value="gpt-4o">GPT-4o (Recommended)</SelectItem>
                    <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                    <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo (Faster)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  Different models have different capabilities and response speeds
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label htmlFor="temperature" className="text-foreground">
                    Temperature: {settings.temperature}
                  </Label>
                </div>
                <Slider
                  id="temperature"
                  min={0}
                  max={2}
                  step={0.1}
                  value={[settings.temperature]}
                  onValueChange={(value) => handleChange("temperature", value[0])}
                  className="[&_[role=slider]]:bg-primary"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Precise</span>
                  <span>Balanced</span>
                  <span>Creative</span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  Lower values produce more consistent outputs, higher values produce more creative outputs
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxTokens" className="text-foreground">
                  Max Tokens
                </Label>
                <Input
                  id="maxTokens"
                  type="number"
                  value={settings.maxTokens}
                  onChange={(e) => handleChange("maxTokens", Number.parseInt(e.target.value))}
                  min={100}
                  max={4000}
                  className="bg-secondary/50 border-border text-foreground"
                />
                <p className="text-sm text-muted-foreground">
                  Maximum number of tokens to generate in the response (1 token ≈ 4 characters)
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="interface" className="space-y-4 pt-4">
          <Card className="bg-background border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Interface Settings</CardTitle>
              <CardDescription className="text-muted-foreground">
                Customize the appearance and behavior of the chat interface
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="theme" className="text-foreground">
                  Theme
                </Label>
                <Select value={settings.theme} onValueChange={(value) => handleChange("theme", value)}>
                  <SelectTrigger id="theme" className="bg-secondary/50 border-border text-foreground">
                    <SelectValue placeholder="Select theme" />
                  </SelectTrigger>
                  <SelectContent className="bg-background border-border">
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="fontSize" className="text-foreground">
                  Font Size
                </Label>
                <Select value={settings.fontSize} onValueChange={(value) => handleChange("fontSize", value)}>
                  <SelectTrigger id="fontSize" className="bg-secondary/50 border-border text-foreground">
                    <SelectValue placeholder="Select font size" />
                  </SelectTrigger>
                  <SelectContent className="bg-background border-border">
                    <SelectItem value="small">Small</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="large">Large</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="markdown_rendering" className="text-foreground">
                    Markdown Rendering
                  </Label>
                  <p className="text-sm text-muted-foreground">Enable formatting in AI responses</p>
                </div>
                <Switch id="markdown_rendering" checked={true} disabled />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="sound_effects" className="text-foreground">
                    Sound Effects
                  </Label>
                  <p className="text-sm text-muted-foreground">Play sounds for new messages</p>
                </div>
                <Switch id="sound_effects" checked={false} disabled />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Button type="submit" className="w-full bg-primary hover:bg-primary/90" disabled={loading}>
        {loading ? "Saving..." : "Save Settings"}
      </Button>
    </form>
  )
}
