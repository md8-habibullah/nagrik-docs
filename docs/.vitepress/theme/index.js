import { h } from 'vue'
import Theme from 'vitepress/theme'
import { watchEffect } from 'vue'
import '../style.css'

export default {
    ...Theme,
    Layout() {
        return h(Theme.Layout)
    },
    enhanceApp({ app, router, siteData }) {
        // Ensure dark mode switcher works properly
        if (typeof window !== 'undefined') {
            // Set initial theme based on system preference or localStorage
            const isDark = localStorage.getItem('vitepress-theme-appearance') === 'dark' ||
                (!localStorage.getItem('vitepress-theme-appearance') &&
                    window.matchMedia('(prefers-color-scheme: dark)').matches)

            document.documentElement.classList.toggle('dark', isDark)

            // Listen for theme changes
            router.afterEach(() => {
                const isDarkMode = document.documentElement.classList.contains('dark')
                localStorage.setItem('vitepress-theme-appearance', isDarkMode ? 'dark' : 'light')
            })

            // Watch for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('vitepress-theme-appearance')) {
                    document.documentElement.classList.toggle('dark', e.matches)
                }
            })
        }
    }
}
