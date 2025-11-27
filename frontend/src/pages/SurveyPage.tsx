import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'
import { submitSurveyByGroup, getSurveyQuestions } from '../services/api'

interface Question {
  code: string
  text: string
  type: 'numeric' | 'text'
  category: string
}

export default function SurveyPage() {
  const { groupId } = useParams()
  const navigate = useNavigate()
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<string, number | string>>({})
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    try {
      const data = await getSurveyQuestions()
      setQuestions(data.questions)

      // Initialize answers
      const initialAnswers: Record<string, number | string> = {}
      data.questions.forEach((q: Question) => {
        if (q.type === 'text') {
          initialAnswers[q.code] = ''
        } else {
          initialAnswers[q.code] = 1
        }
      })
      setAnswers(initialAnswers)
    } catch (err) {
      setError('Не удалось загрузить вопросы')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!groupId) return

    setLoading(true)
    setError(null)

    try {
      const submissionAnswers = Object.entries(answers).map(([code, value]) => ({
        question_code: code,
        question_text: questions.find(q => q.code === code)?.text || '',
        numeric_value: typeof value === 'number' ? value : null,
        text_value: typeof value === 'string' ? value : null
      }))

      await submitSurveyByGroup(parseInt(groupId), submissionAnswers)
      setSubmitted(true)
    } catch (err) {
      setError('Не удалось отправить опрос. Попробуйте позже.')
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-lg text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Спасибо за участие!
          </h2>
          <p className="text-gray-600 mb-6">
            Ваши ответы успешно отправлены анонимно.
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-secondary transition"
          >
            Вернуться на главную
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Анонимный опрос
          </h1>
          <p className="text-gray-600 mb-8">
            Ваши ответы полностью анонимны
          </p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {questions.map((question, index) => (
              <div key={question.code} className="border-b pb-6">
                <label className="block text-lg font-medium text-gray-900 mb-4">
                  {index + 1}. {question.text}
                </label>

                {question.type === 'numeric' ? (
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-600">1 - Минимум</span>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={answers[question.code] as number || 1}
                      onChange={(e) => setAnswers({
                        ...answers,
                        [question.code]: parseInt(e.target.value)
                      })}
                      className="flex-1 h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      aria-label={question.text}
                    />
                    <span className="text-2xl font-bold text-primary w-12 text-center">
                      {answers[question.code] || 1}
                    </span>
                    <span className="text-sm text-gray-600">5 - Максимум</span>
                  </div>
                ) : (
                  <textarea
                    value={answers[question.code] as string || ''}
                    onChange={(e) => setAnswers({
                      ...answers,
                      [question.code]: e.target.value
                    })}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="Введите ваш комментарий..."
                  />
                )}
              </div>
            ))}

            <div className="flex justify-end space-x-4 pt-6">
              <button
                type="button"
                onClick={() => navigate('/')}
                className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-secondary transition disabled:opacity-50"
              >
                {loading ? 'Отправка...' : 'Отправить ответы'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
