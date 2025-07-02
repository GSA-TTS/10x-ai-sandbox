import typography from '@tailwindcss/typography';
import '@gsa-tts/graymatter-style-tokens/dist/css/token-list.json';

/** @type {import('tailwindcss').Config} */
export default {
	darkMode: 'class',
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				colors: {
					white: 'ai-color-white": "#ffffff',
					black: 'ai-color-black": "#000000'
				},
				neutral: {
					0: 'var(--ai-color-neutral-0)', // white
					50: 'var(--ai-color-neutral-50)',
					100: 'var(--ai-color-neutral-100)',
					200: 'var(--ai-color-neutral-200)',
					300: 'var(--ai-color-neutral-300)',
					400: 'var(--ai-color-neutral-400)',
					500: 'var(--ai-color-neutral-500)',
					600: 'var(--ai-color-neutral-600)',
					700: 'var(--ai-color-neutral-700)',
					800: 'var(--ai-color-neutral-800)',
					850: 'var(--ai-color-neutral-850)',
					900: 'var(--ai-color-neutral-900)',
					950: 'var(--ai-color-neutral-950)',
					1000: 'var(--ai-color-neutral-1000)'
				},
				steel: {
					50: 'var(--ai-color-steel-50)',
					100: 'var(--ai-color-steel-100)',
					200: 'var(--ai-color-steel-200)',
					300: 'var(--ai-color-steel-300)',
					400: 'var(--ai-color-steel-400)',
					500: 'var(--ai-color-steel-500)',
					600: 'var(--ai-color-steel-600)',
					700: 'var(--ai-color-steel-700)',
					800: 'var(--ai-color-steel-800)',
					900: 'var(--ai-color-steel-900)'
				},
				blue: {
					50: 'var(--ai-color-blue-50)',
					100: 'var(--ai-color-blue-100)',
					200: 'var(--ai-color-blue-200)',
					300: 'var(--ai-color-blue-300)',
					400: 'var(--ai-color-blue-400)',
					500: 'var(--ai-color-blue-500)',
					600: 'var(--ai-color-blue-600)',
					700: 'var(--ai-color-blue-700)',
					800: 'var(--ai-color-blue-800)',
					900: 'var(--ai-color-blue-900)'
				},
				violet: {
					50: 'var(--ai-color-violet-50)',
					100: 'var(--ai-color-violet-100)',
					200: 'var(--ai-color-violet-200)',
					300: 'var(--ai-color-violet-300)',
					400: 'var(--ai-color-violet-400)',
					500: 'var(--ai-color-violet-500)',
					600: 'var(--ai-color-violet-600)',
					700: 'var(--ai-color-violet-700)',
					800: 'var(--ai-color-violet-800)',
					900: 'var(--ai-color-violet-900)'
				},
				pink: {
					50: 'var(--ai-color-pink-50)',
					100: 'var(--ai-color-pink-100)',
					200: 'var(--ai-color-pink-200)',
					300: 'var(--ai-color-pink-300)',
					400: 'var(--ai-color-pink-400)',
					500: 'var(--ai-color-pink-500)',
					600: 'var(--ai-color-pink-600)',
					700: 'var(--ai-color-pink-700)',
					800: 'var(--ai-color-pink-800)',
					900: 'var(--ai-color-pink-900)'
				},
				red: {
					50: 'var(--ai-color-red-50)',
					100: 'var(--ai-color-red-100)',
					200: 'var(--ai-color-red-200)',
					300: 'var(--ai-color-red-300)',
					400: 'var(--ai-color-red-400)',
					500: 'var(--ai-color-red-500)',
					600: 'var(--ai-color-red-600)',
					700: 'var(--ai-color-red-700)',
					800: 'var(--ai-color-red-800)',
					900: 'var(--ai-color-red-900)'
				},
				orange: {
					50: 'var(--ai-color-orange-50)',
					100: 'var(--ai-color-orange-100)',
					200: 'var(--ai-color-orange-200)',
					300: 'var(--ai-color-orange-300)',
					400: 'var(--ai-color-orange-400)',
					500: 'var(--ai-color-orange-500)',
					600: 'var(--ai-color-orange-600)',
					700: 'var(--ai-color-orange-700)',
					800: 'var(--ai-color-orange-800)',
					900: 'var(--ai-color-orange-900)'
				},
				yellow: {
					50: 'var(--ai-color-yellow-50)',
					100: 'var(--ai-color-yellow-100)',
					200: 'var(--ai-color-yellow-200)',
					300: 'var(--ai-color-yellow-300)',
					400: 'var(--ai-color-yellow-400)',
					500: 'var(--ai-color-yellow-500)',
					600: 'var(--ai-color-yellow-600)',
					700: 'var(--ai-color-yellow-700)',
					800: 'var(--ai-color-yellow-800)',
					900: 'var(--ai-color-yellow-900)'
				},
				green: {
					50: 'var(--ai-color-green-50)',
					100: 'var(--ai-color-green-10)',
					200: 'var(--ai-color-green-200)',
					300: 'var(--ai-color-green-300)',
					400: 'var(--ai-color-green-400)',
					500: 'var(--ai-color-green-500)',
					600: 'var(--ai-color-green-600)',
					700: 'var(--ai-color-green-700)',
					800: 'var(--ai-color-green-800)',
					900: 'var(--ai-color-green-900)'
				},
				//existing tailwind gray - dark mode is using gray palette.
				gray: {
					50: '#f9f9f9',
					100: '#ececec',
					200: '#e3e3e3',
					300: '#cdcdcd',
					400: '#b4b4b4',
					500: '#9b9b9b',
					600: '#676767',
					700: '#4e4e4e',
					800: 'var(--color-gray-800, #333)',
					850: 'var(--color-gray-850, #262626)',
					900: 'var(--color-gray-900, #171717)',
					950: 'var(--color-gray-950, #0d0d0d)'
				}
			},
			typography: {
				DEFAULT: {
					css: {
						pre: false,
						code: false,
						'pre code': false,
						'code::before': false,
						'code::after': false
					}
				}
			},
			zIndex: {
				100: '100',
				1000: '1000'
			},
			padding: {
				'safe-bottom': 'env(safe-area-inset-bottom)'
			}
		}
	},
	plugins: [typography]
};
