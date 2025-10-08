"""
Tech Stack Analysis Engine
Deep analysis of detected technologies to determine environment requirements
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass

from .detector import ProjectDetector, ProjectInfo

@dataclass
class ServiceRequirement:
    """Represents a required service/dependency"""
    name: str
    category: str
    required_env_vars: List[str]
    optional_env_vars: List[str] = None
    description: str = ""
    setup_instructions: str = ""
    validation_pattern: Optional[str] = None

@dataclass
class EnvironmentRequirements:
    """Complete environment requirements for a project"""
    services: List[ServiceRequirement]
    database_requirements: List[str]
    deployment_requirements: List[str]
    development_requirements: List[str]
    testing_requirements: List[str]

class TechStackAnalyzer:
    """Analyzes detected tech stack to determine environment requirements"""
    
    def __init__(self, project_detector: ProjectDetector):
        self.detector = project_detector
        self.project_info = project_detector.project_info or project_detector.detect()
        self.service_catalog = self._build_service_catalog()
    
    def analyze(self) -> EnvironmentRequirements:
        """Analyze project and return complete environment requirements"""
        services = self._detect_required_services()
        database_reqs = self._analyze_database_requirements()
        deployment_reqs = self._analyze_deployment_requirements()
        dev_reqs = self._analyze_development_requirements()
        test_reqs = self._analyze_testing_requirements()
        
        return EnvironmentRequirements(
            services=services,
            database_requirements=database_reqs,
            deployment_requirements=deployment_reqs,
            development_requirements=dev_reqs,
            testing_requirements=test_reqs
        )
    
    def _build_service_catalog(self) -> Dict[str, ServiceRequirement]:
        """Build catalog of known services and their requirements"""
        return {
            'supabase': ServiceRequirement(
                name='Supabase',
                category='Database & Auth',
                required_env_vars=['SUPABASE_URL', 'SUPABASE_ANON_KEY'],
                optional_env_vars=[
                    'SUPABASE_SERVICE_ROLE_KEY', 
                    'SUPABASE_PROJECT_REF', 
                    'SUPABASE_MCP_TOKEN',
                    'SUPABASE_ACCESS_TOKEN'
                ],
                description='Backend-as-a-Service with PostgreSQL database and authentication',
                setup_instructions='Create project at supabase.com → Settings → API → Copy URL, anon key, and optional service role key',
                validation_pattern=r'https://[a-z]+\.supabase\.co'
            ),
            'stripe': ServiceRequirement(
                name='Stripe',
                category='Payments',
                required_env_vars=['STRIPE_PUBLISHABLE_KEY'],
                optional_env_vars=['STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET'],
                description='Payment processing service',
                setup_instructions='Create account at stripe.com → Developers → API Keys',
                validation_pattern=r'pk_(test_|live_)[a-zA-Z0-9]+'
            ),
            'openai': ServiceRequirement(
                name='OpenAI',
                category='AI Services',
                required_env_vars=['OPENAI_API_KEY'],
                optional_env_vars=['OPENAI_ORG_ID'],
                description='AI/LLM API service',
                setup_instructions='Create account at openai.com → API → Create new secret key',
                validation_pattern=r'sk-[a-zA-Z0-9]+'
            ),
            'nextauth': ServiceRequirement(
                name='NextAuth.js',
                category='Authentication',
                required_env_vars=['NEXTAUTH_SECRET', 'NEXTAUTH_URL'],
                optional_env_vars=[],
                description='Authentication library for Next.js',
                setup_instructions='Generate secret: openssl rand -base64 32',
                validation_pattern=None
            ),
            'postgresql': ServiceRequirement(
                name='PostgreSQL',
                category='Database',
                required_env_vars=['DATABASE_URL'],
                optional_env_vars=['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'],
                description='PostgreSQL database connection',
                setup_instructions='Set up local PostgreSQL or use cloud provider',
                validation_pattern=r'postgresql://.*'
            ),
            'redis': ServiceRequirement(
                name='Redis',
                category='Cache/Session Store',
                required_env_vars=['REDIS_URL'],
                optional_env_vars=['REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD'],
                description='In-memory data store for caching and sessions',
                setup_instructions='Set up local Redis or use cloud provider like Upstash',
                validation_pattern=r'redis://.*'
            ),
            'mongodb': ServiceRequirement(
                name='MongoDB',
                category='Database',
                required_env_vars=['MONGODB_URI'],
                optional_env_vars=['MONGODB_DB_NAME'],
                description='NoSQL document database',
                setup_instructions='Set up local MongoDB or use MongoDB Atlas',
                validation_pattern=r'mongodb(\+srv)?://.*'
            ),
            'github': ServiceRequirement(
                name='GitHub',
                category='Development',
                required_env_vars=['GITHUB_TOKEN'],
                optional_env_vars=['GITHUB_USERNAME'],
                description='GitHub API access for automation',
                setup_instructions='GitHub → Settings → Developer settings → Personal access tokens',
                validation_pattern=r'ghp_[a-zA-Z0-9]+'
            ),
            'vercel': ServiceRequirement(
                name='Vercel',
                category='Deployment',
                required_env_vars=['VERCEL_TOKEN'],
                optional_env_vars=['VERCEL_ORG_ID', 'VERCEL_PROJECT_ID'],
                description='Deployment platform for frontend applications',
                setup_instructions='Vercel Dashboard → Settings → Tokens → Create',
                validation_pattern=None
            )
        }
    
    def _detect_required_services(self) -> List[ServiceRequirement]:
        """Detect which services are required based on frameworks"""
        required_services = []
        frameworks = self.project_info.frameworks
        
        # Direct framework-to-service mapping
        service_mappings = {
            'supabase': 'supabase',
            'stripe': 'stripe',
            'openai': 'openai',
            'mongoose': 'mongodb',
            'prisma': self._detect_prisma_database(),
        }
        
        for framework, service_name in service_mappings.items():
            if framework in frameworks and service_name in self.service_catalog:
                required_services.append(self.service_catalog[service_name])
        
        # Next.js specific services
        if 'nextjs' in frameworks:
            # NextAuth is common with Next.js
            if self._has_nextauth():
                required_services.append(self.service_catalog['nextauth'])
        
        # Development services
        if self._needs_github_integration():
            required_services.append(self.service_catalog['github'])
        
        # Deployment services
        if self.project_info.deployment_target == 'vercel':
            required_services.append(self.service_catalog['vercel'])
        
        return required_services
    
    def _detect_prisma_database(self) -> str:
        """Detect database type when using Prisma"""
        schema_file = self.detector.project_path / 'prisma' / 'schema.prisma'
        if schema_file.exists():
            try:
                content = schema_file.read_text()
                if 'postgresql' in content.lower():
                    return 'postgresql'
                elif 'mysql' in content.lower():
                    return 'mysql'
                elif 'sqlite' in content.lower():
                    return 'sqlite'
            except FileNotFoundError:
                pass
        return 'postgresql'  # Default assumption
    
    def _has_nextauth(self) -> bool:
        """Check if project uses NextAuth.js"""
        # Check package.json
        package_json = self.detector.project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    all_deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    if 'next-auth' in all_deps or '@next-auth/core' in all_deps:
                        return True
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Check for NextAuth files
        nextauth_patterns = [
            'pages/api/auth/[...nextauth].js',
            'pages/api/auth/[...nextauth].ts',
            'app/api/auth/[...nextauth]/route.js',
            'app/api/auth/[...nextauth]/route.ts',
        ]
        
        for pattern in nextauth_patterns:
            if (self.detector.project_path / pattern).exists():
                return True
        
        return False
    
    def _needs_github_integration(self) -> bool:
        """Check if project needs GitHub integration"""
        # Check for GitHub Actions
        github_actions = self.detector.project_path / '.github' / 'workflows'
        if github_actions.exists() and any(github_actions.iterdir()):
            return True
        
        # Check for spec-kit (often uses GitHub)
        if any('.specify' in str(f) for f in self.project_info.config_files):
            return True
        
        return False
    
    def _analyze_database_requirements(self) -> List[str]:
        """Analyze database requirements"""
        requirements = []
        frameworks = self.project_info.frameworks
        
        if 'supabase' in frameworks:
            requirements.extend([
                'Supabase project with PostgreSQL database',
                'Row Level Security (RLS) policies configured',
                'Real-time subscriptions enabled if needed'
            ])
        elif 'prisma' in frameworks:
            requirements.extend([
                'Database server (PostgreSQL/MySQL/SQLite)',
                'Prisma migrations applied',
                'Database schema synchronized'
            ])
        elif 'mongoose' in frameworks:
            requirements.extend([
                'MongoDB database server or Atlas cluster',
                'Appropriate database indexes configured'
            ])
        
        return requirements
    
    def _analyze_deployment_requirements(self) -> List[str]:
        """Analyze deployment requirements"""
        requirements = []
        
        deployment_target = self.project_info.deployment_target
        if deployment_target == 'vercel':
            requirements.extend([
                'Vercel account and project configured',
                'Environment variables set in Vercel dashboard',
                'Custom domain configured if needed'
            ])
        elif deployment_target == 'netlify':
            requirements.extend([
                'Netlify account and site configured',
                'Build settings configured',
                'Environment variables set in Netlify'
            ])
        elif deployment_target == 'docker':
            requirements.extend([
                'Docker installed and configured',
                'Container registry access (Docker Hub, etc.)',
                'Kubernetes cluster if using orchestration'
            ])
        
        if 'nextjs' in self.project_info.frameworks:
            requirements.append('Static export or server deployment support')
        
        return requirements
    
    def _analyze_development_requirements(self) -> List[str]:
        """Analyze development environment requirements"""
        requirements = []
        
        language = self.project_info.language
        if language == 'typescript':
            requirements.extend([
                'Node.js 18+ installed',
                'TypeScript configured',
                'IDE with TypeScript support'
            ])
        elif language == 'javascript':
            requirements.extend([
                'Node.js 18+ installed',
                'Package manager (npm/yarn/pnpm)'
            ])
        elif language == 'python':
            requirements.extend([
                'Python 3.8+ installed',
                'Virtual environment configured',
                'Package dependencies installed'
            ])
        
        # Framework-specific requirements
        frameworks = self.project_info.frameworks
        if 'nextjs' in frameworks:
            requirements.append('Next.js development server configuration')
        if 'tailwind' in frameworks:
            requirements.append('Tailwind CSS build process configured')
        
        return requirements
    
    def _analyze_testing_requirements(self) -> List[str]:
        """Analyze testing environment requirements"""
        requirements = []
        frameworks = self.project_info.frameworks
        
        if 'vitest' in frameworks:
            requirements.extend([
                'Vitest test runner configured',
                'Test coverage reporting setup'
            ])
        elif 'jest' in frameworks:
            requirements.extend([
                'Jest test runner configured',
                'Test environment setup for React/Node.js'
            ])
        
        if 'playwright' in frameworks:
            requirements.extend([
                'Playwright browsers installed',
                'End-to-end test configuration',
                'CI/CD pipeline for browser testing'
            ])
        
        if 'pytest' in frameworks:
            requirements.extend([
                'pytest and testing dependencies installed',
                'Test database configuration',
                'API testing setup'
            ])
        
        return requirements
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Get a summary of environment requirements"""
        env_reqs = self.analyze()
        
        return {
            'total_services': len(env_reqs.services),
            'service_categories': list(set(service.category for service in env_reqs.services)),
            'required_env_vars': sum(len(service.required_env_vars) for service in env_reqs.services),
            'optional_env_vars': sum(len(service.optional_env_vars or []) for service in env_reqs.services),
            'database_setup_needed': len(env_reqs.database_requirements) > 0,
            'deployment_setup_needed': len(env_reqs.deployment_requirements) > 0,
            'services_by_category': self._group_services_by_category(env_reqs.services)
        }
    
    def _group_services_by_category(self, services: List[ServiceRequirement]) -> Dict[str, List[str]]:
        """Group services by category"""
        categories = {}
        for service in services:
            category = service.category
            if category not in categories:
                categories[category] = []
            categories[category].append(service.name)
        return categories