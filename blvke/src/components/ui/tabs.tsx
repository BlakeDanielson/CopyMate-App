import * as React from "react"

import { cn } from "@/lib/utils"

const Tabs = React.forwardRef<React.ElementRef<"div">, React.ComponentPropsWithoutRef<"div">>(
  ({ className, children, ...props }, ref) => (
    <div className={cn("relative", className)} {...props} ref={ref}>
      {children}
    </div>
  ),
)
Tabs.displayName = "Tabs"

const TabsList = React.forwardRef<React.ElementRef<"div">, React.ComponentPropsWithoutRef<"div">>(
  ({ className, children, ...props }, ref) => (
    <div
      className={cn("inline-flex items-center justify-center rounded-md bg-muted p-1 text-muted-foreground", className)}
      {...props}
      ref={ref}
    >
      {children}
    </div>
  ),
)
TabsList.displayName = "TabsList"

const TabsTrigger = React.forwardRef<React.ElementRef<"button">, React.ComponentPropsWithoutRef<"button">>(
  ({ className, children, ...props }, ref) => (
    <button
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm",
        className,
      )}
      {...props}
      ref={ref}
    >
      {children}
    </button>
  ),
)
TabsTrigger.displayName = "TabsTrigger"

const TabsContent = React.forwardRef<React.ElementRef<"div">, React.ComponentPropsWithoutRef<"div">>(
  ({ className, children, ...props }, ref) => (
    <div
      className={cn(
        "mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        className,
      )}
      {...props}
      ref={ref}
    >
      {children}
    </div>
  ),
)
TabsContent.displayName = "TabsContent"

const Card = React.forwardRef<React.ElementRef<"div">, React.ComponentPropsWithoutRef<"div">>(
  ({ className, children, ...props }, ref) => (
    <div className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)} {...props} ref={ref}>
      {children}
    </div>
  ),
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<React.ElementRef<"div">, React.ComponentPropsWithoutRef<"div">>(
  ({ className, children, ...props }, ref) => (
    <div className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} ref={ref}>
      {children}
    </div>
  ),
)
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<React.ElementRef<"p">, React.ComponentPropsWithoutRef<"p">>(
  ({ className, children, ...props }, ref) => (
    <p className={cn("text-2xl font-semibold leading-none tracking-tight", className)} {...props} ref={ref}>
      {children}
    </p>
  ),
)
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<React.ElementRef<"p">, React.ComponentPropsWithoutRef<"p">>(
  ({ className, children, ...props }, ref) => (
    <p className={cn("text-sm text-muted-foreground", className)} {...props} ref={ref}>
      {children}
    </p>
  ),
)
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<React.ElementRef<"div">, React.ComponentPropsWithoutRef<"div">>(
  ({ className, children, ...props }, ref) => (
    <div className={cn("p-6 pt-0", className)} {...props} ref={ref}>
      {children}
    </div>
  ),
)
CardContent.displayName = "CardContent"

export { Tabs, TabsList, TabsTrigger, TabsContent, Card, CardHeader, CardTitle, CardDescription, CardContent }
