import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  message?: string
}

export default function LoadingSpinner({
  size = 'md',
  className,
  message = 'Loading...'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  }

  return (
    <div className={cn('flex flex-col items-center justify-center p-8', className)}>
      <div
        className={cn(
          'animate-spin rounded-full border-2 border-gray-200 border-t-orange-600',
          sizeClasses[size]
        )}
      />
      {message && (
        <p className="mt-4 text-gray-600 text-center">{message}</p>
      )}
    </div>
  )
}

export function PageLoader({ message = 'Loading page...' }: { message?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <LoadingSpinner size="lg" message={message} />
    </div>
  )
}

export function InlineLoader({ message }: { message?: string }) {
  return (
    <div className="flex items-center justify-center py-8">
      <LoadingSpinner size="sm" message={message} />
    </div>
  )
}
