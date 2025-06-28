'use client'

import React, { Component, type ErrorInfo, type ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import Link from 'next/link'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({
      error,
      errorInfo
    })
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  private handleRefresh = () => {
    window.location.reload()
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
          <Card className="max-w-2xl w-full">
            <CardContent className="p-8 text-center">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-8 h-8 text-red-600" />
                </div>
              </div>

              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                出现了一些问题
              </h1>

              <p className="text-lg text-gray-600 mb-6">
                抱歉，页面遇到了意外错误。我们已经记录了这个问题，请稍后重试。
              </p>

              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="mb-6 p-4 bg-gray-100 rounded-lg text-left overflow-auto">
                  <h3 className="font-semibold text-gray-900 mb-2">错误详情：</h3>
                  <pre className="text-sm text-gray-700">
                    {this.state.error.toString()}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  onClick={this.handleRetry}
                  className="bg-orange-600 hover:bg-orange-700 flex items-center"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  重试
                </Button>

                <Button
                  onClick={this.handleRefresh}
                  variant="outline"
                  className="flex items-center"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  刷新页面
                </Button>

                <Link href="/">
                  <Button variant="outline" className="flex items-center w-full sm:w-auto">
                    <Home className="w-4 h-4 mr-2" />
                    返回首页
                  </Button>
                </Link>
              </div>

              <div className="mt-8 text-sm text-gray-500">
                <p>如果问题持续存在，请联系我们的技术支持。</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

// 简化版错误边界，用于小组件
export function SimpleErrorBoundary({
  children,
  fallback
}: {
  children: ReactNode
  fallback?: ReactNode
}) {
  return (
    <ErrorBoundary
      fallback={
        fallback || (
          <div className="p-4 text-center">
            <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p className="text-gray-600">加载失败，请刷新重试</p>
          </div>
        )
      }
    >
      {children}
    </ErrorBoundary>
  )
}
