import Link from 'next/link';
import { useRouter } from 'next/router';
import React, { ReactNode } from 'react';
import UserManagement from './UserManagement';
import { useAuth } from '../context/AuthContext';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const { isLoggedIn } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-2 py-2 xl:h-16 xl:flex-row xl:justify-between xl:py-0">
            <div className="flex flex-wrap items-center gap-x-4">
              <div className="shrink-0 flex items-center">
                <Link href="/" className="text-primary-dark font-bold text-xl">
                  Meal Maker
                </Link>
              </div>
              <nav className="flex flex-wrap gap-x-3 sm:ml-6 sm:gap-x-8">
                {/* <Link
                  href="/"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 ${router.pathname === '/'
                    ? 'border-primary text-gray-900'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                >
                  Home
                </Link> */}
                <Link
                  href="/recipes"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 ${router.pathname.startsWith('/recipes')
                    ? 'border-primary text-gray-900'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                >
                  Recipes
                </Link>
                {/* <Link
                  href="/ingredients"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 ${
                    router.pathname.startsWith('/ingredients')
                      ? 'border-primary text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                  >
                    Ingredients
                </Link> */}
                {isLoggedIn && (
                  <>
                    <Link
                      href="/shopping-list"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 ${
                        router.pathname === '/shopping-list'
                          ? 'border-primary text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                    >
                      Shopping List
                    </Link>
                    <Link
                      href="/fridge"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 ${
                        router.pathname === '/fridge'
                          ? 'border-primary text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                    >
                      Fridge
                    </Link>
                    <Link
                      href="/favourites"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 ${
                        router.pathname === '/favourites'
                          ? 'border-primary text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                    >
                      Favourites
                    </Link>
                  </>
                )}
              </nav>
            </div>
            <UserManagement />
          </div>
        </div>
      </header>
      <main className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 grow">
        {children}
      </main>
      <footer className="bg-white border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm">
            &copy; {new Date().getFullYear()} Meal Maker. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
