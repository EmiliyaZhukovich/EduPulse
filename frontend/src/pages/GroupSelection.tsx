import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Users, Building2 } from 'lucide-react'
import { getSurveyGroups } from '../services/api'

interface Group {
  id: number
  name: string
  faculty_name: string
  year: number
}

export default function GroupSelection() {
  const navigate = useNavigate()
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadGroups()
  }, [])

  const loadGroups = async () => {
    setLoading(true)
    try {
      const data = await getSurveyGroups()
      setGroups(data.groups)
    } catch (err) {
      setError('Не удалось загрузить список групп')
    } finally {
      setLoading(false)
    }
  }

  const handleContinue = () => {
    if (selectedGroup) {
      navigate(`/survey/${selectedGroup}`)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка групп...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Выберите вашу группу
          </h1>
          <p className="text-gray-600">
            Выберите группу, к которой вы принадлежите, для прохождения опроса
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {groups.map((group) => (
              <div
                key={group.id}
                onClick={() => setSelectedGroup(group.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedGroup === group.id
                    ? 'border-primary bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center mb-2">
                  <Users className="w-5 h-5 text-primary mr-2" />
                  <h3 className="font-semibold text-gray-900">{group.name}</h3>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Building2 className="w-4 h-4 mr-1" />
                  <span>{group.faculty_name}</span>
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {group.year} курс
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center">
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
            >
              Назад
            </button>

            <button
              onClick={handleContinue}
              disabled={!selectedGroup}
              className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-secondary transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              Продолжить
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          </div>
        </div>

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            Важно знать
          </h3>
          <ul className="text-blue-800 space-y-1">
            <li>• Опрос полностью анонимен</li>
            <li>• Ваши ответы не связаны с вашей личностью</li>
            <li>• Результаты используются только для анализа группы</li>
            <li>• После отправки изменить ответы нельзя</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
