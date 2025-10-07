"""
Environment Templates System
Pre-configured environment templates for different project types
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ProjectTemplate:
    """Template for a specific project type"""
    name: str
    description: str
    frameworks: List[str]
    env_template: str
    setup_steps: List[str]
    required_services: List[str]

class TemplateManager:
    """Manages environment templates for different project types"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, ProjectTemplate]:
        """Load all available project templates"""
        return {
            'nextjs-supabase': self._nextjs_supabase_template(),
            'nextjs-full-stack': self._nextjs_full_stack_template(),
            'python-fastapi': self._python_fastapi_template(),
            'react-spa': self._react_spa_template(),
            'nodejs-api': self._nodejs_api_template(),
            'spec-kit': self._spec_kit_template()
        }
    
    def get_template(self, template_name: str) -> ProjectTemplate:
        """Get a specific template by name"""
        return self.templates.get(template_name)
    
    def get_matching_template(self, frameworks: List[str], project_type: str) -> ProjectTemplate:
        """Get the best matching template for given frameworks and project type"""
        # Exact matches first
        for template in self.templates.values():
            if set(frameworks).issubset(set(template.frameworks)):
                return template
        
        # Partial matches
        best_match = None
        best_score = 0
        
        for template in self.templates.values():
            score = len(set(frameworks) & set(template.frameworks))
            if score > best_score:
                best_score = score
                best_match = template
        
        return best_match or self._default_template()
    
    def _nextjs_supabase_template(self) -> ProjectTemplate:
        """Next.js + Supabase template"""
        return ProjectTemplate(
            name='nextjs-supabase',
            description='Next.js application with Supabase backend',
            frameworks=['nextjs', 'supabase', 'tailwind'],
            env_template='''# Next.js + Supabase Configuration
# Generated for web application with authentication and database

# Core Application
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
PORT=3000

# Supabase Configuration
# Get these from: https://supabase.com/dashboard → Settings → API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... # Only for admin operations
# SUPABASE_PROJECT_REF=abcdefghijklmnop # Project reference ID
# SUPABASE_MCP_TOKEN=sbp_mcp_... # For MCP integration (if needed)
# SUPABASE_ACCESS_TOKEN=sbp_... # Personal access token for API access

# NextAuth.js (if using authentication)
NEXTAUTH_SECRET=your-random-secret-here
NEXTAUTH_URL=http://localhost:3000

# Development
DEBUG=false
LOG_LEVEL=info
''',
            setup_steps=[
                'Create Supabase project at supabase.com',
                'Copy project URL and anon key from Settings → API',
                'Generate NextAuth secret: openssl rand -base64 32',
                'Configure authentication providers in Supabase',
                'Set up database tables and RLS policies'
            ],
            required_services=['supabase']
        )
    
    def _nextjs_full_stack_template(self) -> ProjectTemplate:
        """Next.js full-stack template with multiple services"""
        return ProjectTemplate(
            name='nextjs-full-stack',
            description='Full-stack Next.js with payments and AI',
            frameworks=['nextjs', 'supabase', 'stripe', 'openai', 'tailwind'],
            env_template='''# Next.js Full-Stack Configuration
# Generated for complete web application with payments and AI

# Core Application
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
PORT=3000

# Supabase (Database & Auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# SUPABASE_PROJECT_REF=abcdefghijklmnop # Project reference ID
# SUPABASE_MCP_TOKEN=sbp_mcp_... # For MCP integration (if needed)
# SUPABASE_ACCESS_TOKEN=sbp_... # Personal access token for API access

# Stripe (Payments)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OpenAI (AI Services)
OPENAI_API_KEY=sk-...
# OPENAI_ORG_ID=org-... # Only if using organization

# NextAuth.js
NEXTAUTH_SECRET=your-random-secret-here
NEXTAUTH_URL=http://localhost:3000

# Development
DEBUG=false
LOG_LEVEL=info
''',
            setup_steps=[
                'Create Supabase project and configure database',
                'Set up Stripe account and get API keys',
                'Create OpenAI account and generate API key',
                'Generate NextAuth secret',
                'Configure webhooks for Stripe',
                'Set up payment flows and subscription logic'
            ],
            required_services=['supabase', 'stripe', 'openai']
        )
    
    def _python_fastapi_template(self) -> ProjectTemplate:
        """Python FastAPI template"""
        return ProjectTemplate(
            name='python-fastapi',
            description='Python FastAPI backend application',
            frameworks=['fastapi', 'postgresql', 'redis'],
            env_template='''# Python FastAPI Configuration
# Generated for API backend with database

# Core Application
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database

# Redis (Caching/Sessions)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
# REDIS_PASSWORD=your_redis_password

# Security
SECRET_KEY=your-secret-key-for-jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
# OPENAI_API_KEY=sk-...
# STRIPE_SECRET_KEY=sk_test_...

# Development
DEBUG=false
LOG_LEVEL=info
''',
            setup_steps=[
                'Set up PostgreSQL database',
                'Configure Redis for caching',
                'Generate secure secret key',
                'Install Python dependencies',
                'Run database migrations',
                'Configure API endpoints'
            ],
            required_services=['postgresql', 'redis']
        )
    
    def _react_spa_template(self) -> ProjectTemplate:
        """React SPA template"""
        return ProjectTemplate(
            name='react-spa',
            description='React Single Page Application',
            frameworks=['react', 'vite'],
            env_template='''# React SPA Configuration
# Generated for frontend-only application

# Core Application
NODE_ENV=development
PORT=3000
GENERATE_SOURCEMAP=true

# API Configuration
REACT_APP_API_URL=http://localhost:8000
# REACT_APP_API_KEY=your-api-key

# Third-party Services
# REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
# REACT_APP_SUPABASE_URL=https://your-project.supabase.co
# REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Development
FAST_REFRESH=true
''',
            setup_steps=[
                'Configure API endpoints',
                'Set up build process',
                'Configure routing',
                'Add state management if needed'
            ],
            required_services=[]
        )
    
    def _nodejs_api_template(self) -> ProjectTemplate:
        """Node.js API template"""
        return ProjectTemplate(
            name='nodejs-api',
            description='Node.js REST API backend',
            frameworks=['express', 'postgresql'],
            env_template='''# Node.js API Configuration
# Generated for REST API backend

# Core Application
NODE_ENV=development
PORT=8000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database

# Security
JWT_SECRET=your-jwt-secret
SESSION_SECRET=your-session-secret
CORS_ORIGIN=http://localhost:3000

# Third-party Services
# STRIPE_SECRET_KEY=sk_test_...
# OPENAI_API_KEY=sk-...
# SENDGRID_API_KEY=SG...

# Development
DEBUG=false
LOG_LEVEL=info
''',
            setup_steps=[
                'Set up database connection',
                'Configure authentication middleware',
                'Generate JWT secret',
                'Set up API routes',
                'Configure CORS for frontend'
            ],
            required_services=['postgresql']
        )
    
    def _spec_kit_template(self) -> ProjectTemplate:
        """Spec-kit project template"""
        return ProjectTemplate(
            name='spec-kit',
            description='Spec-kit project with AI assistant integration',
            frameworks=['spec-kit'],
            env_template='''# Spec-Kit Project Configuration
# Generated for AI-assisted development workflow

# Core Configuration
NODE_ENV=development
DEBUG=false
LOG_LEVEL=info

# GitHub Integration
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_USERNAME=your-github-username

# AI Services (optional)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Project-specific variables will be added based on your tech stack
# Run 'multiagent-core env-detect' to generate additional configuration
''',
            setup_steps=[
                'Generate GitHub personal access token',
                'Configure AI assistant API keys',
                'Set up project-specific environment variables',
                'Initialize spec-kit workflows'
            ],
            required_services=['github']
        )
    
    def _default_template(self) -> ProjectTemplate:
        """Default template for unknown project types"""
        return ProjectTemplate(
            name='default',
            description='Generic project template',
            frameworks=[],
            env_template='''# Project Configuration
# Generated for generic project

# Core
NODE_ENV=development
DEBUG=false
LOG_LEVEL=info

# Add your project-specific environment variables below
''',
            setup_steps=[
                'Identify your project dependencies',
                'Add required environment variables',
                'Configure development workflow'
            ],
            required_services=[]
        )
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates"""
        return [
            {
                'name': template.name,
                'description': template.description,
                'frameworks': ', '.join(template.frameworks)
            }
            for template in self.templates.values()
        ]