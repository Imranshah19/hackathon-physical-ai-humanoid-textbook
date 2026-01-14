import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import path from 'path';

// GitHub Pages configuration
const organizationName = process.env.GITHUB_REPOSITORY_OWNER || 'your-username';
const projectName = 'hackathon-physical-ai-humanoid-textbook';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A Comprehensive Textbook for Building Intelligent Robots',
  favicon: 'img/favicon.ico',

  // GitHub Pages URL
  url: `https://${organizationName}.github.io`,
  baseUrl: `/${projectName}/`,

  // GitHub Pages deployment config
  organizationName,
  projectName,
  trailingSlash: false,
  deploymentBranch: 'gh-pages',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // Plugins - RAG Chatbot for interactive learning
  plugins: [
    [
      path.resolve(__dirname, '../docusaurus-plugin'),
      {
        apiUrl: process.env.VITE_API_URL || 'http://localhost:8000/api/v1',
        position: 'bottom-right',
        defaultOpen: false,
        excludePages: ['^/404'],
      },
    ],
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          path: '../book',
          routeBasePath: '/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
          editUrl: `https://github.com/${organizationName}/${projectName}/tree/master/`,
          // Module structure
          numberPrefixParser: false,
          breadcrumbs: true,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Social card image
    image: 'img/social-card.png',

    // Announcement bar (optional)
    announcementBar: {
      id: 'wip_notice',
      content: '🚧 This textbook is under active development. Some sections may be incomplete.',
      backgroundColor: '#fef3c7',
      textColor: '#92400e',
      isCloseable: true,
    },

    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Textbook Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'bookSidebar',
          position: 'left',
          label: 'Modules',
        },
        {
          type: 'dropdown',
          label: 'Quick Links',
          position: 'left',
          items: [
            {
              label: 'Module 1: ROS2 Foundations',
              to: '/module-1/',
            },
            {
              label: 'Module 2: Simulation & Digital Twins',
              to: '/module-2/',
            },
            {
              label: 'Module 3: Isaac & Reinforcement Learning',
              to: '/module-3/',
            },
            {
              label: 'Module 4: Vision-Language-Action',
              to: '/module-4/',
            },
          ],
        },
        {
          href: `https://github.com/${organizationName}/${projectName}`,
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Modules',
          items: [
            {
              label: 'Module 1: ROS2 Foundations',
              to: '/module-1/',
            },
            {
              label: 'Module 2: Simulation',
              to: '/module-2/',
            },
            {
              label: 'Module 3: Isaac & RL',
              to: '/module-3/',
            },
            {
              label: 'Module 4: VLA',
              to: '/module-4/',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'ROS2 Documentation',
              href: 'https://docs.ros.org/en/humble/',
            },
            {
              label: 'NVIDIA Isaac',
              href: 'https://developer.nvidia.com/isaac-sim',
            },
            {
              label: 'OpenVLA',
              href: 'https://openvla.github.io/',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub Discussions',
              href: `https://github.com/${organizationName}/${projectName}/discussions`,
            },
            {
              label: 'Report an Issue',
              href: `https://github.com/${organizationName}/${projectName}/issues`,
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Textbook. Built with Docusaurus.`,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: [
        'python',
        'cpp',
        'bash',
        'yaml',
        'json',
        'toml',
        'cmake',
        'csharp',
      ],
    },

    // Table of Contents
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },

    // Docs configuration
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },

    // Color mode
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },

    // Algolia DocSearch (optional - configure if you have an account)
    // algolia: {
    //   appId: 'YOUR_APP_ID',
    //   apiKey: 'YOUR_SEARCH_API_KEY',
    //   indexName: 'physical-ai-textbook',
    //   contextualSearch: true,
    // },
  } satisfies Preset.ThemeConfig,
};

export default config;
