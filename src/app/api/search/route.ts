import { type NextRequest, NextResponse } from 'next/server'
import {
  searchContent,
  getSearchSuggestions,
  getPopularSearches,
  getRelatedSearches,
  searchCache,
  type SearchResponse
} from '@/lib/search-api'

export const dynamic = "force-static";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)

    // 获取查询参数
    const query = searchParams.get('q') || ''
    const type = searchParams.get('type')?.split(',').filter(Boolean) || []
    const category = searchParams.get('category')?.split(',').filter(Boolean) || []
    const limit = Math.min(Number.parseInt(searchParams.get('limit') || '20'), 100) // 最大100条
    const offset = Math.max(Number.parseInt(searchParams.get('offset') || '0'), 0)
    const action = searchParams.get('action') // suggestions, popular, related

    // 处理特殊操作
    if (action === 'suggestions') {
      const suggestions = await getSearchSuggestions(query)
      return NextResponse.json({ suggestions })
    }

    if (action === 'popular') {
      const popularSearches = await getPopularSearches()
      return NextResponse.json({ popularSearches })
    }

    if (action === 'related') {
      const relatedSearches = await getRelatedSearches(query)
      return NextResponse.json({ relatedSearches })
    }

    // 生成缓存键
    const cacheKey = JSON.stringify({
      query,
      type: type.sort(),
      category: category.sort(),
      limit,
      offset
    })

    // 检查缓存
    const cachedResult = searchCache.get(cacheKey)
    if (cachedResult) {
      return NextResponse.json({
        ...cachedResult,
        cached: true
      })
    }

    // 执行搜索
    const searchResult: SearchResponse = await searchContent(query, {
      types: type,
      categories: category,
      limit,
      offset
    })

    // 存储到缓存
    searchCache.set(cacheKey, searchResult)

    // 添加额外的元数据
    const response = {
      ...searchResult,
      cached: false,
      timestamp: new Date().toISOString(),
      meta: {
        offset,
        limit,
        hasMore: offset + limit < searchResult.total
      }
    }

    return NextResponse.json(response)

  } catch (error) {
    console.error('Search API error:', error)

    return NextResponse.json(
      {
        error: 'Internal server error',
        message: 'Failed to process search request',
        results: [],
        total: 0,
        query: ''
      },
      { status: 500 }
    )
  }
}

// 支持POST请求以处理复杂查询
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      query = '',
      filters = {},
      sorting = {},
      pagination = {}
    } = body

    const {
      types = [],
      categories = [],
      ratings = [],
      dateRange = null
    } = filters

    const {
      field = 'relevance',
      direction = 'desc'
    } = sorting

    const {
      limit = 20,
      offset = 0
    } = pagination

    // 执行搜索
    const searchResult = await searchContent(query, {
      types,
      categories,
      limit,
      offset
    })

    // 应用额外筛选
    if (ratings.length > 0) {
      searchResult.results = searchResult.results.filter(item =>
        item.rating && ratings.some((rating: number) => Math.floor(item.rating!) === rating)
      )
    }

    // 应用排序
    if (field !== 'relevance') {
      searchResult.results.sort((a, b) => {
        let aValue: string | number
        let bValue: string | number

        switch (field) {
          case 'rating':
            aValue = a.rating || 0
            bValue = b.rating || 0
            break
          case 'date':
            aValue = a.publishedAt ? new Date(a.publishedAt).getTime() : 0
            bValue = b.publishedAt ? new Date(b.publishedAt).getTime() : 0
            break
          case 'title':
            aValue = a.title
            bValue = b.title
            break
          default:
            return 0
        }

        if (direction === 'asc') {
          return aValue > bValue ? 1 : -1
        } else {
          return aValue < bValue ? 1 : -1
        }
      })
    }

    // 重新计算总数
    searchResult.total = searchResult.results.length

    return NextResponse.json({
      ...searchResult,
      meta: {
        query,
        filters,
        sorting,
        pagination,
        timestamp: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Advanced search API error:', error)

    return NextResponse.json(
      {
        error: 'Invalid request',
        message: 'Failed to process advanced search request'
      },
      { status: 400 }
    )
  }
}
