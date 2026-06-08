import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi, tokenStore } from '../services/api.js'

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isLoading: false,
      isAuthenticated: false,

      // Lưu cặp token (access + refresh) sau khi đăng nhập / refresh
      setTokens: (access, refresh) => {
        tokenStore.set(access, refresh)
        set({ accessToken: access })
      },

      fetchMe: async () => {
        set({ isLoading: true })
        try {
          const { data } = await authApi.getMe()
          set({ user: data, isAuthenticated: true })
          return data
        } catch {
          set({ user: null, isAuthenticated: false })
          return null
        } finally {
          set({ isLoading: false })
        }
      },

      // Backend không có endpoint logout → chỉ xóa token phía client
      logout: async () => {
        tokenStore.clear()
        set({ user: null, accessToken: null, isAuthenticated: false })
      },
    }),
    {
      name: 'plant-auth',
      partialize: (s) => ({ accessToken: s.accessToken }),
    }
  )
)
