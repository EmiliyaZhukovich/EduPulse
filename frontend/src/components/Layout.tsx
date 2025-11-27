import { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Home, BarChart3, Settings } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center px-4 text-primary font-bold text-xl">
                🧠 PsyMonitor
              </Link>
            </div>
            <div className="flex space-x-4">
              <Link
                to="/"
                className="flex items-center px-4 text-gray-600 hover:text-primary transition"
              >
                <Home className="w-5 h-5 mr-2" />
                Главная
              </Link>
              <Link
                to="/curator"
                className="flex items-center px-4 text-gray-600 hover:text-primary transition"
              >
                <BarChart3 className="w-5 h-5 mr-2" />
                Кабинет куратора
              </Link>
              <Link
                to="/admin"
                className="flex items-center px-4 text-gray-600 hover:text-primary transition"
              >
                <Settings className="w-5 h-5 mr-2" />
                Админ-панель
              </Link>
            </div>
          </div>
        </div>
      </nav>
      <main>{children}</main>
    </div>
  )
}
