import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [sveltekit()],
    resolve: {
        alias: {
            $components: '/src/components',
            $stores: '/src/stores',
            $utils: '/src/utils',
        },
    },
    css: {
        preprocessorOptions: {
            sass: {
                api: 'modern',
            },
        },
    },
    esbuild: {
        target: 'es2020',
    },
});
