import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground",
        outline:
          "text-foreground",
        // File type specific variants
        pdf: "border-transparent bg-red-100 text-red-800",
        docx: "border-transparent bg-blue-100 text-blue-800",
        jpg: "border-transparent bg-purple-100 text-purple-800",
        png: "border-transparent bg-green-100 text-green-800",
        mp4: "border-transparent bg-amber-100 text-amber-800",
        mp3: "border-transparent bg-pink-100 text-pink-800",
        gif: "border-transparent bg-indigo-100 text-indigo-800",
        heic: "border-transparent bg-teal-100 text-teal-800",
      },
      size: {
        default: "px-2.5 py-0.5 text-xs",
        sm: "px-2 py-0.5 text-[10px]",
        lg: "px-3 py-1 text-sm",
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  )
}

export { Badge, badgeVariants } 