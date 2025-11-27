import { useState, useEffect } from 'react'
import { getCurrentUser, startLogin } from '../services/api'
import { Users, Building2, TrendingUp, Plus, Edit, Trash2 } from 'lucide-react'
import { getAllStatistics, getFaculties, createFaculty, updateFaculty, deleteFaculty, getAllGroups, createGroup, updateGroup, deleteGroup } from '../services/api'

interface Faculty {
  id: number
  name: string
  description?: string
  group_count: number
}

interface Group {
  id: number
  name: string
  faculty_id: number
  faculty_name: string
  year: number
  submission_count: number
}

export default function AdminDashboard() {
  const [statistics, setStatistics] = useState<any>(null)
  const [faculties, setFaculties] = useState<Faculty[]>([])
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(true)
  const [accessDenied, setAccessDenied] = useState(false)
  const [activeTab, setActiveTab] = useState<'statistics' | 'faculties' | 'groups'>('statistics')

  // Forms
  const [showFacultyForm, setShowFacultyForm] = useState(false)
  const [showGroupForm, setShowGroupForm] = useState(false)
  const [editingFaculty, setEditingFaculty] = useState<Faculty | null>(null)
  const [editingGroup, setEditingGroup] = useState<Group | null>(null)

  // Form data
  const [facultyForm, setFacultyForm] = useState({ name: '', description: '' })
  const [groupForm, setGroupForm] = useState({ name: '', faculty_id: 0, year: 1 })

  useEffect(() => {
    const check = async () => {
      try {
        const response = await getCurrentUser()

        if (response?.user) {
          const roles: string[] = (response.user.roles || []).map((r: string) => String(r).toLowerCase())

          const rawGroups: string[] = (response.user.raw?.groups || [])
            .filter((g: any) => typeof g === 'string')
            .map((g: string) => g.split('/').filter(Boolean).pop()!.toLowerCase())

          console.debug('Admin auth - roles:', roles, 'raw.groups:', rawGroups)

          const isAdmin = roles.includes('admins') || roles.includes('администраторы') || roles.includes('admin') || rawGroups.includes('admins') || rawGroups.includes('администраторы') || rawGroups.includes('admin')

          if (isAdmin) {
            setAccessDenied(false)
            await loadData()
            return
          }

          // Authenticated but not an admin
          console.error('Access denied: user is not an admin')
          setAccessDenied(true)
          setLoading(false)
          return
        }

        // If no user info, redirect to login
        startLogin('/admin')
      } catch (error: unknown) {
        // Redirect only for 401 responses
        if (typeof error === 'object' && error && 'response' in error && (error as any).response?.status === 401) {
          startLogin('/admin')
        } else {
          console.error('Error checking admin authentication:', error)
          // Show access denied to avoid redirect loops
          setAccessDenied(true)
          setLoading(false)
        }
      }
    }

    check()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [statsData, facultiesData, groupsData] = await Promise.all([
        getAllStatistics(),
        getFaculties(),
        getAllGroups()
      ])

      setStatistics(statsData)
      setFaculties(facultiesData.faculties)
      setGroups(groupsData.groups)
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateFaculty = async () => {
    try {
      await createFaculty(facultyForm)
      setFacultyForm({ name: '', description: '' })
      setShowFacultyForm(false)
      loadData()
    } catch (err) {
      console.error('Failed to create faculty:', err)
    }
  }

  const handleUpdateFaculty = async () => {
    if (!editingFaculty) return

    try {
      await updateFaculty(editingFaculty.id, facultyForm)
      setEditingFaculty(null)
      setFacultyForm({ name: '', description: '' })
      loadData()
    } catch (err) {
      console.error('Failed to update faculty:', err)
    }
  }

  const handleDeleteFaculty = async (facultyId: number) => {
    if (!confirm('Вы уверены, что хотите удалить факультет?')) return

    try {
      await deleteFaculty(facultyId)
      loadData()
    } catch (err) {
      console.error('Failed to delete faculty:', err)
    }
  }

  const handleCreateGroup = async () => {
    try {
      await createGroup(groupForm)
      setGroupForm({ name: '', faculty_id: 0, year: 1 })
      setShowGroupForm(false)
      loadData()
    } catch (err) {
      console.error('Failed to create group:', err)
    }
  }

  const handleUpdateGroup = async () => {
    if (!editingGroup) return

    try {
      await updateGroup(editingGroup.id, groupForm)
      setEditingGroup(null)
      setGroupForm({ name: '', faculty_id: 0, year: 1 })
      loadData()
    } catch (err) {
      console.error('Failed to update group:', err)
    }
  }

  const handleDeleteGroup = async (groupId: number) => {
    if (!confirm('Вы уверены, что хотите удалить группу?')) return

    try {
      await deleteGroup(groupId)
      loadData()
    } catch (err) {
      console.error('Failed to delete group:', err)
    }
  }

  const openEditFaculty = (faculty: Faculty) => {
    setEditingFaculty(faculty)
    setFacultyForm({ name: faculty.name, description: faculty.description || '' })
    setShowFacultyForm(true)
  }

  const openEditGroup = (group: Group) => {
    setEditingGroup(group)
    setGroupForm({ name: group.name, faculty_id: group.faculty_id, year: group.year })
    setShowGroupForm(true)
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <p className="text-center text-gray-600">Загрузка данных...</p>
      </div>
    )
  }

  if (accessDenied) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Доступ запрещён</h1>
          <p className="text-gray-600 mb-4">Ваш аккаунт не состоит в группе администратора. Пожалуйста, обратитесь к администратору.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Административная панель
        </h1>
        <p className="text-gray-600">
          Управление факультетами, группами и просмотр статистики
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('statistics')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'statistics'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Статистика
            </button>
            <button
              onClick={() => setActiveTab('faculties')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'faculties'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Факультеты
            </button>
            <button
              onClick={() => setActiveTab('groups')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'groups'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Группы
            </button>
            {/* Survey tab removed */}
          </nav>
        </div>
      </div>

      {/* Statistics Tab */}
      {activeTab === 'statistics' && statistics && (
        <>
          {/* Overall stats */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <Users className="w-8 h-8 text-primary mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Всего ответов</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {statistics.overall.total_submissions}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <Building2 className="w-8 h-8 text-primary mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Факультетов</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {statistics.overall.total_faculties}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <TrendingUp className="w-8 h-8 text-primary mr-3" />
                <div>
                  <p className="text-sm text-gray-600">Групп</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {statistics.overall.total_groups}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Faculty statistics */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Статистика по факультетам</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Факультет
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Групп
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ответов
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {statistics.faculties.map((faculty: any) => (
                    <tr key={faculty.faculty}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {faculty.faculty}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {faculty.total_groups}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {faculty.total_submissions}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Faculties Tab */}
      {activeTab === 'faculties' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Управление факультетами</h2>
            <button
              onClick={() => setShowFacultyForm(true)}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-secondary transition flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Добавить факультет
            </button>
          </div>

          {/* Faculty Form Modal */}
          {showFacultyForm && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h3 className="text-lg font-semibold mb-4">
                  {editingFaculty ? 'Редактировать факультет' : 'Добавить факультет'}
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Название
                    </label>
                    <input
                      type="text"
                      value={facultyForm.name}
                      onChange={(e) => setFacultyForm({ ...facultyForm, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Описание
                    </label>
                    <textarea
                      value={facultyForm.description}
                      onChange={(e) => setFacultyForm({ ...facultyForm, description: e.target.value })}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    onClick={() => {
                      setShowFacultyForm(false)
                      setEditingFaculty(null)
                      setFacultyForm({ name: '', description: '' })
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    Отмена
                  </button>
                  <button
                    onClick={editingFaculty ? handleUpdateFaculty : handleCreateFaculty}
                    className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-secondary"
                  >
                    {editingFaculty ? 'Сохранить' : 'Создать'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Faculties List */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Название
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Описание
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Групп
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {faculties.map((faculty) => (
                  <tr key={faculty.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {faculty.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {faculty.description || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {faculty.group_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => openEditFaculty(faculty)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteFaculty(faculty.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Groups Tab */}
      {activeTab === 'groups' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Управление группами</h2>
            <button
              onClick={() => setShowGroupForm(true)}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-secondary transition flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Добавить группу
            </button>
          </div>

          {/* Group Form Modal */}
          {showGroupForm && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h3 className="text-lg font-semibold mb-4">
                  {editingGroup ? 'Редактировать группу' : 'Добавить группу'}
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Название группы
                    </label>
                    <input
                      type="text"
                      value={groupForm.name}
                      onChange={(e) => setGroupForm({ ...groupForm, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Факультет
                    </label>
                    <select
                      value={groupForm.faculty_id}
                      onChange={(e) => setGroupForm({ ...groupForm, faculty_id: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    >
                      <option value={0}>Выберите факультет</option>
                      {faculties.map((faculty) => (
                        <option key={faculty.id} value={faculty.id}>
                          {faculty.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Курс
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="6"
                      value={groupForm.year}
                      onChange={(e) => setGroupForm({ ...groupForm, year: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    onClick={() => {
                      setShowGroupForm(false)
                      setEditingGroup(null)
                      setGroupForm({ name: '', faculty_id: 0, year: 1 })
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    Отмена
                  </button>
                  <button
                    onClick={editingGroup ? handleUpdateGroup : handleCreateGroup}
                    className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-secondary"
                  >
                    {editingGroup ? 'Сохранить' : 'Создать'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Groups List */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Название
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Факультет
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Курс
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ответов
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {groups.map((group) => (
                  <tr key={group.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {group.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {group.faculty_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {group.year}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {group.submission_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => openEditGroup(group)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteGroup(group.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

  {/* Survey tab removed from admin panel */}
    </div>
  )
}
