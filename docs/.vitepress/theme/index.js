import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import '../style.css'

export default {
    extends: DefaultTheme,
    Layout: () => {
        return h(DefaultTheme.Layout)
    },
    enhanceApp({ app, router, siteData }) {
        // The VitePress DefaultTheme automatically manages the <html> 'dark' class
        // and synchronizes with localStorage. No custom observer is needed here.
    }
}