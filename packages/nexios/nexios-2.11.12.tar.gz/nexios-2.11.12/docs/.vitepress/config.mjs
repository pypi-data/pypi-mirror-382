import { defineConfig } from 'vitepress'

export default defineConfig({
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/./logo.png' }],
    ['meta', { name: 'theme-color', content: '#ff7e17' }],
    ['meta', { property: 'og:title', content: "Nexios - Python Web Framework" }],
    ['meta', { property: 'og:description', content: "Nexios is a modern, fast, and secure web framework for Python. It is designed to be easy to use and understand, while also being powerful and flexible." }],
    ['meta', { property: 'og:image', content: "/./logo.png" }],
    ['meta', { property: 'og:type', content: 'website' }],
  ],
  
  
  title: 'Nexios',
  base: "/nexios/",
  description: 'Nexios is a modern, fast, and secure web framework for Python. It is designed to be easy to use and understand, while also being powerful and flexible.',

  themeConfig: {
    siteTitle: 'Nexios',
    logo: '/logo.png',
    favicon: '/logo.png',
    themeSwitcher: true,

    socialLinks: [
      { icon: "github", link: "https://github.com/nexios-labs/nexios" },
      { icon: "twitter", link: "https://twitter.com/nexioslabs" },
    ],

    search: {
      provider: 'local'
    },

    nav: [
      { text: 'Intro', link: '/intro' },
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Examples', link: '/api-examples' },
      { text : "Community", link:"/community"},
      { text: "Discussions", link:"https://github.com/orgs/nexios-labs/discussions"},
      { text: 'Team', link: 'team' },
    ],

    sidebar: {
      '/intro/': [
        { text: 'What is Nexios?', link: '/intro' },
        { text: "What is Asgi?", link: '/intro/asgi' },
        { text: 'Nexios And FastAPI', link: '/intro/nexios-and-fastapi' },
        { text: "Quick Start", link: '/intro/quick-start' },
        { text : "Core Concepts", link: '/intro/concepts' },
        { text : "Async Python", link: '/intro/async-python' },
        {text: 'Migrating To Nexios',link: '/intro/migrating-to-nexios'},
      ],
      '/community/': [
        { text: 'Welcome', link: '/community' },
        { text: 'FAQ', link: '/community/faq' },
        { text : "Contribution Guide", link:"/community/contribution-guide"},
        { text: 'Discussions', link: 'https://github.com/orgs/nexios-labs/discussions' },
        { text: 'Team', link: '/team' },
      ],
      '/guide/': [
        
        { text: 'Getting Started', link: '/guide/getting-started' },
        { text: 'CLI', link: '/guide/cli' },
        { text : "Why Nexios?", link: '/guide/why-nexios' },
        {
          text: 'Core Concepts',
          collapsed: false,
          items: [
            { text: 'Routing', link: '/guide/routing' },
            { text: 'Handlers', link: '/guide/handlers' },
            { text: 'Startups and Shutdowns', link: '/guide/startups-and-shutdowns' },
            { text: 'Request Inputs', link: '/guide/request-inputs' },
            { text: 'Configuration', link: '/guide/configuration' },
            { text: 'Sending Responses', link: '/guide/sending-responses' },
            { text: 'Routers and Subapps', link: '/guide/routers-and-subapps' },
            { text: 'Middleware', link: '/guide/middleware' },
          ] 
        },
        {
          text: 'Request Lifecycle',
          collapsed: false,
          items: [
            { text: 'Cookies', link: '/guide/cookies' },
            { text: 'Headers', link: '/guide/headers' },
            { text: 'Sessions', link: '/guide/sessions' },
            { text: 'Request Info', link: '/guide/request-info' },
          ]
        },
        {
          text: 'Advanced Topics',
          collapsed: false,
          items: [
            { text: 'Error Handling', link: '/guide/error-handling' },
            { text: 'Pagination', link: '/guide/pagination' },
            { text: 'Authentication', link: '/guide/authentication' },
            { text: "Handler Hooks", link: '/guide/handler-hooks' },
            { text: 'Class Based Handlers', link: '/guide/class-based-handlers' },
            { text: 'Events', link: '/guide/events' },
            { text: 'Streaming Response',  link: '/guide/streaming-response' },
            { text: 'Dependency Injection', link: '/guide/dependency-injection' },
            { text : "Templating", link:"/guide/templating/index"},
            { text: 'Static Files', link: '/guide/static-files' },
            { text: 'File Upload', link: '/guide/file-upload' },
            { text: 'Cors', link: '/guide/cors' },
            { text: 'CSRF', link: '/guide/csrf' },
            { text: 'File Router', link: '/guide/file-router' },
            { text: 'Concurrency Utilities', link: '/guide/concurrency' },
            { text: 'Security', link: '/guide/security' },
            { text: 'Pydantic Integration', link: '/guide/pydantic-integration' },
          ]
        },
        {
          text: 'Websockets',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/guide/websockets/index' },
            { text: 'Channels', link: '/guide/websockets/channels' },
            { text: 'Groups', link: '/guide/websockets/groups' },
            { text: 'Events', link: '/guide/websockets/events' },
            { text: 'Consumer', link: '/guide/websockets/consumer' },
          ]
        },
        {
          text: 'OpenAPI',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/guide/openapi/index' },
            { text: 'Response Models with Pydantic', link: '/guide/openapi/response-models' },
            { text: 'Request Schemas', link: '/guide/openapi/request-schemas' },
            { text: 'Request Parameters', link: '/guide/openapi/request-parameters' },
            { text: 'Customizing OpenAPI Config', link: '/guide/openapi/customizing-openapi-configuration' },
            { text: 'Authentication Docs', link: '/guide/openapi/authentication-documentation' },
          ]
        }
      ],

      '/architecture/': [
        {
          text: 'Architecture',
          items: [
            { text: 'Async Python', link: '/architecture/async-python' },
            { text: 'Asgi', link: '/architecture/asgi' },
          ]
        }
      ],
      '/course/': [
        {
          text: 'Course',
          items: [
            { text: 'Day 1: Welcome & Your First Nexios App', link: '/course/day01' },
            { text: 'Day 2: Routing: Mapping URLs to Code', link: '/course/day02' },
            { text: 'Day 3: Async, Request & Response Essentials', link: '/course/day03' },
            { text: 'Day 4: Class-Based Views & APIHandler', link: '/course/day04' },
            { text: 'Day 5: Middleware: Built-in & Custom', link: '/course/day05' },
            { text: 'Day 6: Environment & CORS Configuration', link: '/course/day06' },
            { text: 'Day 7: Project: Mini To-Do API', link: '/course/day07' },
            { text: 'Day 8: JWT Authentication (Part 1)', link: '/course/day08' },
            { text: 'Day 9: JWT Authentication (Part 2)', link: '/course/day09' },
            { text: 'Day 10: Testing Nexios Applications', link: '/course/day10' },
            { text: 'Day 11: Request Validation with Pydantic', link: '/course/day11' },
            { text: 'Day 12: File Uploads & Multipart Data', link: '/course/day12' },
            { text: 'Day 13: WebSocket Basics', link: '/course/day13' },
            { text: 'Day 14: Real-Time Chat App with ChannelBox', link: '/course/day14' },
            { text: 'Day 15: Background Tasks & Scheduling', link: '/course/day15' },
            { text: 'Day 16: Real-Time Application Patterns', link: '/course/day16' },
            { text: 'Day 17: Advanced Middleware Techniques', link: '/course/day17' },
            { text: 'Day 18: Custom Decorators & Utilities', link: '/course/day18' },
            { text: 'Day 19: Dependency Injection in Nexios', link: '/course/day19' },
            { text: 'Day 20: Concurrency & Async Utilities', link: '/course/day20' },
            { text: 'Day 21: Project: Real-Time Chat Application', link: '/course/day21' },
            { text: 'Day 22: Testing Strategies & Best Practices', link: '/course/day22' },
            { text: 'Day 23: Logging & Monitoring', link: '/course/day23' },
            { text: 'Day 24: Performance Optimization', link: '/course/day24' },
            { text: 'Day 25: Event System & WebSocket Events', link: '/course/day25' },
            { text: 'Day 26: Deployment Strategies', link: '/course/day26' },
            { text: 'Day 27: Docker & Containerization', link: '/course/day27' },
            { text: 'Day 28: Project: Production-Ready API', link: '/course/day28' },
          ]
        }
      ]
    }
  },

  markdown: {
    // lineNumbers: true
  },

  ignoreDeadLinks: true,
})