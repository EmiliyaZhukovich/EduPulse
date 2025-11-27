import { Users, BarChart3, Shield, FileText } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Система мониторинга социально-психологического климата
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Анонимные опросы для студентов и аналитика для кураторов
          </p>
          <div className="flex items-center justify-center">
            <Link
              to="/survey"
              className="inline-block px-8 py-3 bg-primary text-white rounded-lg shadow hover:bg-secondary transition"
            >
              Пройти опрос
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition">
            <Users className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Анонимность</h3>
            <p className="text-gray-600">
              Полностью анонимные опросы без регистрации
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition">
            <BarChart3 className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Аналитика</h3>
            <p className="text-gray-600">
              Детальная статистика и визуализация данных
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition">
            <Shield className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Безопасность</h3>
            <p className="text-gray-600">
              Защищённая авторизация через Keycloak
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition">
            <FileText className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Отчёты</h3>
            <p className="text-gray-600">
              Генерация отчётов для кураторов
            </p>
          </div>
        </div>

        {/* How it works */}
        <div className="bg-white rounded-lg shadow-lg p-8" id="survey">
          <h2 className="text-3xl font-bold text-center mb-8">Как это работает?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Нажмите на кнопку "Пройти опрос"</h3>
              <p className="text-gray-600">
                Выберите свою группу для прохождения опроса
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Заполните опрос</h3>
              <p className="text-gray-600">
                Ответьте на вопросы анонимно
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Получите результаты</h3>
              <p className="text-gray-600">
                Кураторы видят агрегированную статистику
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
