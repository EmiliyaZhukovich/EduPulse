import React, { useState, useEffect } from 'react'
import { getCurrentUser, startLogin } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Users, TrendingUp } from 'lucide-react'
import { getGroups, getGroupStatistics } from '../services/api'

interface Faculty {
  id: number
  name: string
  description?: string
  group_count: number
}

interface Group {
  id: number
  name: string
  faculty?: Faculty
  year: number
}

interface UserResponse {
  user: {
    id: string
    username: string
    roles: string[]
    raw: Record<string, any>
  }
}

interface ChartDataPoint {
  name: string
  value: number
  count: number
  code?: string
}


interface Statistics {
  group_id: number
  group_name: string
  total_submissions: number
  question_stats: Array<{
    question_code: string
    average: number
    count: number
  }>
  open_answers?: Array<{
    question_code: string
    question_text?: string
    text_value: string
    submitted_at: string
  }>
}

export default function CuratorDashboard() {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(false)
  const [accessDenied, setAccessDenied] = useState(false)

  useEffect(() => {
    const check = async () => {
      try {
        // Try to get current user info
        const response = await getCurrentUser() as UserResponse

        // If we have a valid user response, check roles and groups
        if (response?.user) {
          // Normalize backend-provided roles to lower-case strings
          const roles: string[] = (response.user.roles || []).map((r: string) => String(r).toLowerCase())

          // Also inspect raw.groups (Keycloak may include groups in the raw claim)
          const rawGroups: string[] = (response.user.raw?.groups || [])
            .filter((g: any) => typeof g === 'string')
            .map((g: string) => g.split('/').filter(Boolean).pop()!.toLowerCase())

          console.debug('Auth check - roles:', roles, 'raw.groups:', rawGroups)

          const isCurator = roles.includes('curators') || roles.includes('кураторы') || rawGroups.includes('curators') || rawGroups.includes('кураторы')

          if (isCurator) {
            // Only load groups if explicitly confirmed as curator
            await loadGroups()
            setAccessDenied(false)
          } else {
            // User is authenticated but not a curator — show access denied instead of redirecting to login.
            console.error('Access denied: user is not a curator')
            setAccessDenied(true)
          }
        }
      } catch (error: unknown) {
        // Only redirect on actual 401 errors
        if (typeof error === 'object' && error && 'response' in error && (error as any).response?.status === 401) {
          startLogin('/curator')
        } else {
          console.error('Error checking authentication:', error)
        }
      }
    }

    check()
  }, [])

  useEffect(() => {
    if (selectedGroup) {
      loadStatistics(selectedGroup)
    }
  }, [selectedGroup])

  const loadGroups = async () => {
    try {
      const data = await getGroups()
      setGroups(data.groups)
      if (data.groups.length > 0) {
        setSelectedGroup(data.groups[0].id)
      }
    } catch (err) {
      console.error('Failed to load groups:', err)
    }
  }

  const loadStatistics = async (groupId: number) => {
    setLoading(true)
    try {
      const data = await getGroupStatistics(groupId)
      setStatistics(data)
    } catch (err) {
      console.error('Failed to load statistics:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleViewReport = async (): Promise<void> => {
    if (!selectedGroup) return

    try {
      const response = await fetch(`http://localhost:8000/api/reports/group/${selectedGroup}/report`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const html = await response.text()
      const newWindow = window.open('', '_blank')
      if (newWindow) {
        newWindow.document.write(html)
        newWindow.document.close()
      }
    } catch (error) {
      console.error('Failed to view report:', error instanceof Error ? error.message : 'Unknown error')
    }
  }

  // Словарь перевода кодов вопросов на короткие русские названия (для диаграмм и таблицы)
  const questionLabels: { [key: string]: string } = {
    'comfort': 'Комфорт',
    'engagement': 'Вовлеченность',
    'conflicts': 'Конфликтность',
    'stress': 'Стресс',
    'support': 'Поддержка',
    'open_feedback': 'Доп. отзывы'
  }

  // (deprecated) raw chartData removed - use aggregated normalized stats below

  // Normalize and aggregate stats so duplicates (english codes, q1..q6, or full text)
  // are merged into canonical question codes and displayed with Russian labels only.
  const canonicalKeys = ['comfort', 'engagement', 'conflicts', 'stress', 'support', 'open_feedback']

  // Map legacy numeric codes (q1..q6) to canonical codes
  const qnumToCanonical: { [key: string]: string } = {
    'q1': 'comfort',
    'q2': 'engagement',
    'q3': 'conflicts',
    'q4': 'stress',
    'q5': 'support',
    'q6': 'open_feedback'
  }

  // Reverse mapping from Russian label back to canonical code for cases where backend stored full text
  const reverseLabelToCanonical: { [label: string]: string } = {}
  canonicalKeys.forEach(k => {
    const label = questionLabels[k]
    if (label) reverseLabelToCanonical[label] = k
  })

  const aggregated = React.useMemo(() => {
    if (!statistics) return [] as ChartDataPoint[]

    const map: Record<string, { totalWeighted: number; totalCount: number }> = {}

    statistics.question_stats.forEach((stat) => {
      // determine canonical code
      let canonical: string | undefined = undefined

      if (qnumToCanonical[stat.question_code]) {
        canonical = qnumToCanonical[stat.question_code]
      } else if (canonicalKeys.includes(stat.question_code)) {
        canonical = stat.question_code
      } else if (reverseLabelToCanonical[stat.question_code]) {
        canonical = reverseLabelToCanonical[stat.question_code]
      } else {
        // try lowercase match (e.g., accidental case differences)
        const lower = stat.question_code.toLowerCase()
        const found = canonicalKeys.find(k => k.toLowerCase() === lower)
        if (found) canonical = found
      }

      // fallback: use the raw code as canonical (will still be labeled)
      if (!canonical) canonical = stat.question_code

      const weighted = (stat.average || 0) * (stat.count || 0)
      if (!map[canonical]) map[canonical] = { totalWeighted: weighted, totalCount: stat.count || 0 }
      else {
        map[canonical].totalWeighted += weighted
        map[canonical].totalCount += stat.count || 0
      }
    })

    // produce array sorted by canonicalKeys order (preferred) then others
    const result: ChartDataPoint[] = []
    canonicalKeys.forEach((k) => {
      if (map[k]) {
        const entry = map[k]
        const avg = entry.totalCount > 0 ? entry.totalWeighted / entry.totalCount : 0
        result.push({ code: k, name: questionLabels[k] || k, value: avg, count: entry.totalCount })
        delete map[k]
      }
    })

    // remaining (unknown) keys
    Object.keys(map).forEach(k => {
      const entry = map[k]
      const avg = entry.totalCount > 0 ? entry.totalWeighted / entry.totalCount : 0
      result.push({ code: k, name: questionLabels[k] || k, value: avg, count: entry.totalCount })
    })

    return result
  }, [statistics])

  // Numeric-only aggregated data for charts (exclude text/open feedback)
  const aggregatedNumeric = React.useMemo(() => {
    return aggregated.filter(item => item.code !== 'open_feedback')
  }, [aggregated])

  // Include open_feedback as a row in the detailed table using open_answers count from API
  const aggregatedWithOpen = React.useMemo(() => {
    const copy = [...aggregated]
    const openCount = (statistics as any)?.open_answers ? (statistics as any).open_answers.length : 0
    const existing = copy.find(i => i.code === 'open_feedback')
    if (openCount > 0) {
      if (existing) {
        existing.count = Math.max(existing.count || 0, openCount)
      } else {
        copy.push({ code: 'open_feedback', name: questionLabels['open_feedback'] || 'Доп. отзывы', value: 0, count: openCount })
      }
    }
    return copy
  }, [aggregated, statistics])

  const COLORS = ['#2563eb', '#1e40af', '#1d4ed8', '#3b82f6', '#60a5fa']

  if (accessDenied) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Доступ запрещён</h1>
          <p className="text-gray-600 mb-4">Ваш аккаунт не состоит в группе куратора. Пожалуйста, обратитесь к администратору.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Кабинет куратора
        </h1>
        <p className="text-gray-600">
          Просмотр статистики по группам
        </p>
      </div>

      {/* Group selector */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Выберите группу
        </label>
        <select
          value={selectedGroup || ''}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedGroup(parseInt(e.target.value))}
          className="w-full md:w-1/3 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
        >
          {groups.map(group => (
            <option key={group.id} value={group.id}>
              {group.name} ({group.faculty?.name}, {group.year} курс)
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="text-center py-12">
          <p className="text-gray-600">Загрузка данных...</p>
        </div>
      )}

      {statistics && !loading && (
        <>
          {/* Stats cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <Users className="w-8 h-8 text-primary mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Всего ответов</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {statistics.total_submissions}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <TrendingUp className="w-8 h-8 text-primary mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Группа</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {statistics.group_name}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <button
                onClick={handleViewReport}
                className="w-full flex items-center justify-center px-4 py-3 bg-primary text-white rounded-lg hover:bg-secondary transition"
              >
                <TrendingUp className="w-5 h-5 mr-2" />
                Просмотреть отчёт
              </button>
            </div>
          </div>

          {/* Charts */}
          {aggregated.length > 0 && (
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-4">Средние баллы по вопросам</h2>
                <ResponsiveContainer width="100%" height={340}>
                  <BarChart data={aggregatedNumeric} margin={{ bottom: 80 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    {/* rotate X labels and reserve space so long Russian labels fit */}
                    <XAxis dataKey="name" angle={-45} textAnchor="end" interval={0} height={80} />
                    <YAxis domain={[0, 5]} />
                    <Tooltip />
                    <Bar dataKey="value" fill="#2563eb" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-4">Распределение ответов</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={aggregatedNumeric}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value.toFixed(1)}`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {aggregatedNumeric.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Detailed statistics */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Детальная статистика</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Вопрос
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Средний балл
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Количество ответов
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {aggregatedWithOpen.map((stat) => (
                    <tr key={stat.name}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {stat.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {stat.code === 'open_feedback' ? '-' : stat.value.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {stat.count}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          {/* Open (text) answers list */}
          {statistics.open_answers && statistics.open_answers.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6 mt-6">
              <h2 className="text-xl font-semibold mb-4">Текстовые ответы</h2>
              <div className="space-y-4">
                {statistics.open_answers.map((ans: any, idx: number) => (
                  <div key={idx} className="border rounded p-4">
                    <div className="text-sm text-gray-500 mb-2">{questionLabels[ans.question_code] || ans.question_text || ans.question_code} • {new Date(ans.submitted_at).toLocaleString()}</div>
                    <div className="text-gray-800">{ans.text_value}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
