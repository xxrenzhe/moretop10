'use client'

import { useEffect, useState, useCallback } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, Filter, Star, Clock, Loader, AlertCircle } from 'lucide-react'
import LoadingSpinner from './LoadingSpinner'
import ErrorBoundary from './ErrorBoundary'
import type { SearchResult } from '@/lib/search-api'

interface SearchResponse {
  results: SearchResult[]
  total: number
  query: string
  suggestions?: string[]
  cached?: boolean
  meta?: {
    offset: number
    limit: number
    hasMore: boolean
  }
}

export default function SearchResults() {
  const searchParams = useSearchParams()
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [localQuery, setLocalQuery] = useState('')
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [sortBy, setSortBy] = useState('relevance')

  // 执行搜索 - wrapped with useCallback to avoid dependency issues
  const performSearch = useCallback(async (
    query: string = localQuery,
    types: string[] = selectedTypes,
    categories: string[] = selectedCategories,
    limit = 20,
    offset = 0
  ) => {
    setIsLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams()
      if (query) params.set('q', query)
      if (types.length > 0) params.set('type', types.join(','))
      if (categories.length > 0) params.set('category', categories.join(','))
      params.set('limit', limit.toString())
      params.set('offset', offset.toString())

      const response = await fetch(`/api/search?${params.toString()}`)

      if (!response.ok) {
        throw new Error(`搜索失败: ${response.status}`)
      }

      const data: SearchResponse = await response.json()
      setSearchResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '搜索时发生错误')
      console.error('Search error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [localQuery, selectedTypes, selectedCategories])

  // 从URL参数初始化搜索
  useEffect(() => {
    const query = searchParams.get('q') || ''
    const category = searchParams.get('category') || ''
    const type = searchParams.get('type') || ''

    setLocalQuery(query)
    if (category) setSelectedCategories([category])
    if (type) setSelectedTypes([type])

    if (query || category || type) {
      performSearch(query, type ? [type] : [], category ? [category] : [])
    }
  }, [searchParams, performSearch])

  // 处理搜索表单提交
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    performSearch()
  }

  // 类型和类别选项
  const typeOptions = [
    { value: 'review', label: '产品评测' },
    { value: 'category', label: '产品类别' },
    { value: 'topic', label: '主题页面' },
    { value: 'article', label: '文章' }
  ]

  const categoryOptions = [
    { value: 'Electronics', label: '电子产品' },
    { value: 'Home & Kitchen', label: '家居厨房' },
    { value: 'Baby', label: '婴儿用品' },
    { value: 'Beauty & Health', label: '美容健康' },
    { value: 'Automotive', label: '汽车用品' },
    { value: 'Pets', label: '宠物用品' }
  ]

  return (
    <ErrorBoundary>
      <div className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* 搜索头部 */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">搜索结果</h1>

            {/* 搜索表单 */}
            <form onSubmit={handleSearch} className="mb-6">
              <div className="relative max-w-2xl">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <Input
                  type="text"
                  placeholder="搜索产品、评测、文章..."
                  value={localQuery}
                  onChange={(e) => setLocalQuery(e.target.value)}
                  className="pl-12 pr-4 py-3 text-lg"
                />
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-orange-600 hover:bg-orange-700"
                >
                  {isLoading ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    '搜索'
                  )}
                </Button>
              </div>
            </form>

            {/* 筛选器 */}
            <div className="flex flex-wrap gap-4 items-center">
              {/* 类型筛选 */}
              <div className="flex flex-wrap gap-2">
                <span className="text-sm font-medium text-gray-700">类型:</span>
                {typeOptions.map(option => (
                  <Button
                    key={option.value}
                    variant={selectedTypes.includes(option.value) ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => {
                      const newTypes = selectedTypes.includes(option.value)
                        ? selectedTypes.filter(t => t !== option.value)
                        : [...selectedTypes, option.value]
                      setSelectedTypes(newTypes)
                      performSearch(localQuery, newTypes, selectedCategories)
                    }}
                  >
                    {option.label}
                  </Button>
                ))}
              </div>

              {/* 类别筛选 */}
              <div className="flex flex-wrap gap-2">
                <span className="text-sm font-medium text-gray-700">类别:</span>
                {categoryOptions.map(option => (
                  <Button
                    key={option.value}
                    variant={selectedCategories.includes(option.value) ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => {
                      const newCategories = selectedCategories.includes(option.value)
                        ? selectedCategories.filter(c => c !== option.value)
                        : [...selectedCategories, option.value]
                      setSelectedCategories(newCategories)
                      performSearch(localQuery, selectedTypes, newCategories)
                    }}
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* 加载状态 */}
          {isLoading && (
            <LoadingSpinner size="lg" message="搜索中..." />
          )}

          {/* 错误状态 */}
          {error && !isLoading && (
            <Card className="mb-8">
              <CardContent className="p-6 text-center">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">搜索失败</h3>
                <p className="text-gray-600 mb-4">{error}</p>
                <Button
                  onClick={() => performSearch()}
                  className="bg-orange-600 hover:bg-orange-700"
                >
                  重试
                </Button>
              </CardContent>
            </Card>
          )}

          {/* 搜索结果 */}
          {searchResults && !isLoading && !error && (
            <>
              {/* 结果摘要 */}
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <p className="text-gray-600">
                    {searchResults.total > 0 ? (
                      <>
                        找到 <span className="font-semibold">{searchResults.total}</span> 个结果
                        {searchResults.query && (
                          <> 关于 "<span className="font-semibold">{searchResults.query}</span>"</>
                        )}
                        {searchResults.cached && (
                          <Badge variant="secondary" className="ml-2">缓存结果</Badge>
                        )}
                      </>
                    ) : (
                      <>没有找到相关结果</>
                    )}
                  </p>
                </div>
              </div>

              {/* 搜索建议 */}
              {searchResults.suggestions && searchResults.suggestions.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">搜索建议:</h3>
                  <div className="flex flex-wrap gap-2">
                    {searchResults.suggestions.map((suggestion, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setLocalQuery(suggestion)
                          performSearch(suggestion)
                        }}
                      >
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* 结果列表 */}
              {searchResults.results.length === 0 ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">没有找到结果</h3>
                    <p className="text-gray-600 mb-4">
                      尝试使用不同的关键词或调整筛选条件
                    </p>
                    <Button
                      onClick={() => {
                        setLocalQuery('')
                        setSelectedTypes([])
                        setSelectedCategories([])
                        setSearchResults(null)
                      }}
                      variant="outline"
                    >
                      清除筛选
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {searchResults.results.map((result) => (
                    <Card key={result.id} className="group hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
                      <a href={result.url} className="block">
                        {result.imageUrl && (
                          <div className="aspect-video relative overflow-hidden">
                            <img
                              src={result.imageUrl}
                              alt={result.title}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            />
                            {result.rating && (
                              <div className="absolute top-4 right-4">
                                <Badge className="bg-white text-gray-900 shadow-sm">
                                  <Star className="w-3 h-3 mr-1 fill-yellow-400 text-yellow-400" />
                                  {result.rating}
                                </Badge>
                              </div>
                            )}
                          </div>
                        )}
                        <CardContent className="p-6">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary" className="text-xs">
                              {getTypeLabel(result.type)}
                            </Badge>
                            {result.category && (
                              <Badge variant="outline" className="text-xs">
                                {result.category}
                              </Badge>
                            )}
                          </div>
                          <h3 className="font-bold text-lg text-gray-900 group-hover:text-orange-600 transition-colors mb-2">
                            {result.title}
                          </h3>
                          <p className="text-gray-600 text-sm leading-relaxed mb-3 line-clamp-3">
                            {result.description}
                          </p>
                          <div className="flex items-center justify-between text-sm text-gray-500">
                            {result.author && <span>作者: {result.author}</span>}
                            {result.publishedAt && (
                              <span>{new Date(result.publishedAt).toLocaleDateString()}</span>
                            )}
                            {result.reviewCount && (
                              <span>{result.reviewCount} 条评论</span>
                            )}
                          </div>
                        </CardContent>
                      </a>
                    </Card>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </ErrorBoundary>
  )
}

// 类型标签转换
function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    review: '评测',
    category: '类别',
    topic: '主题',
    article: '文章',
    product: '产品'
  }
  return labels[type] || type
}
