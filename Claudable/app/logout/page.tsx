'use client'

import { useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'

export default function LogoutPage() {
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    const doLogout = async () => {
      await supabase.auth.signOut()
      router.push('/login')
      router.refresh()
    }
    doLogout()
  }, [router, supabase])

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-gray-900">Signing out...</h2>
      </div>
    </div>
  )
}
