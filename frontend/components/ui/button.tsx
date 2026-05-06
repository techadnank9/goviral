import * as React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg" | "icon";
}

function Button({ className, variant = "default", size = "default", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-lg font-medium transition-colors disabled:pointer-events-none disabled:opacity-50",
        variant === "default" && "bg-gray-900 text-white hover:bg-gray-800",
        variant === "outline" && "border border-gray-200 bg-white hover:bg-gray-50 text-gray-900",
        variant === "ghost" && "hover:bg-gray-100 text-gray-900",
        size === "default" && "h-9 px-4 py-2 text-sm",
        size === "sm" && "h-7 px-3 text-xs",
        size === "lg" && "h-11 px-6 text-base",
        size === "icon" && "h-9 w-9",
        className
      )}
      {...props}
    />
  );
}

export { Button };
