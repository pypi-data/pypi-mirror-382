"""
Intelligent Environment Generator
Generates context-appropriate environment configuration based on detected tech stack
"""

import re
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .analyzer import TechStackAnalyzer, EnvironmentRequirements, ServiceRequirement

@dataclass
class EnvironmentVariable:
    """Represents an environment variable with metadata"""
    name: str
    value: str
    description: str
    required: bool
    category: str
    validation_pattern: Optional[str] = None
    example_value: Optional[str] = None

class EnvironmentGenerator:
    """Generates intelligent environment configuration"""
    
    def __init__(self, analyzer: TechStackAnalyzer):
        self.analyzer = analyzer
        self.env_requirements = analyzer.analyze()
        self.project_path = analyzer.detector.project_path
    
    def generate_env_example(self) -> str:
        """Generate .env.example file content"""
        env_vars = self._collect_environment_variables()
        return self._format_env_file(env_vars, include_values=False)
    
    def generate_env_template(self) -> str:
        """Generate .env file template with smart defaults"""
        env_vars = self._collect_environment_variables()
        return self._format_env_file(env_vars, include_values=True)
    
    def generate_interactive_prompts(self) -> List[Dict[str, Any]]:
        """Generate interactive prompts for configuration"""
        prompts = []
        env_vars = self._collect_environment_variables()
        
        # Group by category for better UX
        categories = self._group_vars_by_category(env_vars)
        
        for category, vars_in_category in categories.items():
            prompts.append({
                'type': 'category_header',
                'category': category,
                'description': f'Configuration for {category}'
            })
            
            for var in vars_in_category:
                if var.required:
                    prompts.append({
                        'type': 'input',
                        'name': var.name,
                        'description': var.description,
                        'required': var.required,
                        'validation_pattern': var.validation_pattern,
                        'example': var.example_value,
                        'category': var.category
                    })
        
        return prompts
    
    def validate_environment(self, env_vars: Dict[str, str]) -> List[str]:
        """Validate environment variables and return list of errors"""
        errors = []
        required_vars = self._collect_environment_variables()
        
        for var in required_vars:
            if var.required and var.name not in env_vars:
                errors.append(f"Missing required variable: {var.name}")
            elif var.name in env_vars and var.validation_pattern:
                if not re.match(var.validation_pattern, env_vars[var.name]):
                    errors.append(f"Invalid format for {var.name}: {var.description}")
        
        return errors
    
    def _collect_environment_variables(self) -> List[EnvironmentVariable]:
        """Collect all required environment variables"""
        env_vars = []
        
        # Core multiagent variables
        env_vars.extend(self._get_core_variables())
        
        # Service-specific variables
        for service in self.env_requirements.services:
            env_vars.extend(self._get_service_variables(service))
        
        # Framework-specific variables
        env_vars.extend(self._get_framework_variables())
        
        # Development-specific variables
        env_vars.extend(self._get_development_variables())
        
        return env_vars
    
    def _get_core_variables(self) -> List[EnvironmentVariable]:
        """Get core multiagent framework variables"""
        return [
            EnvironmentVariable(
                name='NODE_ENV',
                value='development',
                description='Environment mode (development/production)',
                required=True,
                category='Core'
            ),
            EnvironmentVariable(
                name='DEBUG',
                value='false',
                description='Enable debug logging',
                required=False,
                category='Core'
            ),
            EnvironmentVariable(
                name='LOG_LEVEL',
                value='info',
                description='Logging level (debug/info/warn/error)',
                required=False,
                category='Core'
            )
        ]
    
    def _get_service_variables(self, service: ServiceRequirement) -> List[EnvironmentVariable]:
        """Get environment variables for a specific service"""
        env_vars = []
        
        # Required variables
        for var_name in service.required_env_vars:
            example_value = self._generate_example_value(var_name, service)
            env_vars.append(EnvironmentVariable(
                name=var_name,
                value=example_value,
                description=f'{service.name}: {self._get_var_description(var_name)}',
                required=True,
                category=service.category,
                validation_pattern=service.validation_pattern,
                example_value=example_value
            ))
        
        # Optional variables
        for var_name in service.optional_env_vars or []:
            example_value = self._generate_example_value(var_name, service)
            env_vars.append(EnvironmentVariable(
                name=var_name,
                value='',
                description=f'{service.name}: {self._get_var_description(var_name)} (optional)',
                required=False,
                category=service.category,
                validation_pattern=service.validation_pattern,
                example_value=example_value
            ))
        
        return env_vars
    
    def _get_framework_variables(self) -> List[EnvironmentVariable]:
        """Get framework-specific environment variables"""
        env_vars = []
        frameworks = self.analyzer.project_info.frameworks
        
        # Next.js specific
        if 'nextjs' in frameworks:
            env_vars.extend([
                EnvironmentVariable(
                    name='NEXT_PUBLIC_APP_URL',
                    value='http://localhost:3000',
                    description='Public URL for the Next.js application',
                    required=True,
                    category='Frontend'
                )
            ])
        
        # Tailwind CSS specific
        if 'tailwind' in frameworks:
            env_vars.append(EnvironmentVariable(
                name='TAILWIND_CONFIG_PATH',
                value='./tailwind.config.js',
                description='Path to Tailwind config file',
                required=False,
                category='Frontend'
            ))
        
        return env_vars
    
    def _get_development_variables(self) -> List[EnvironmentVariable]:
        """Get development-specific environment variables"""
        env_vars = []
        
        # Port configuration
        if 'nextjs' in self.analyzer.project_info.frameworks:
            env_vars.append(EnvironmentVariable(
                name='PORT',
                value='3000',
                description='Port for development server',
                required=False,
                category='Development'
            ))
        elif self.analyzer.project_info.language == 'python':
            env_vars.append(EnvironmentVariable(
                name='PORT',
                value='8000',
                description='Port for API server',
                required=False,
                category='Development'
            ))
        
        # Database-specific development variables
        if self.analyzer.project_info.has_database and 'supabase' not in self.analyzer.project_info.frameworks:
            env_vars.extend([
                EnvironmentVariable(
                    name='DB_HOST',
                    value='localhost',
                    description='Database host for local development',
                    required=False,
                    category='Development'
                ),
                EnvironmentVariable(
                    name='DB_PORT',
                    value='5432',
                    description='Database port',
                    required=False,
                    category='Development'
                )
            ])
        
        return env_vars
    
    def _generate_example_value(self, var_name: str, service: ServiceRequirement) -> str:
        """Generate appropriate example value for environment variable"""
        var_name_lower = var_name.lower()
        
        # URL patterns
        if 'url' in var_name_lower:
            if 'supabase' in var_name_lower:
                return 'https://your-project.supabase.co'
            elif 'database' in var_name_lower:
                return 'postgresql://user:password@localhost:5432/dbname'
            elif 'redis' in var_name_lower:
                return 'redis://localhost:6379'
            else:
                return 'https://your-service-url.com'
        
        # Key patterns
        if 'key' in var_name_lower or 'token' in var_name_lower:
            if 'stripe' in var_name_lower and 'publishable' in var_name_lower:
                return 'pk_test_...'
            elif 'stripe' in var_name_lower:
                return 'sk_test_...'
            elif 'supabase' in var_name_lower and 'anon' in var_name_lower:
                return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
            elif 'supabase' in var_name_lower and 'service_role' in var_name_lower:
                return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
            elif 'supabase' in var_name_lower and 'mcp' in var_name_lower:
                return 'sbp_mcp_...'
            elif 'supabase' in var_name_lower and 'access' in var_name_lower:
                return 'sbp_...'
            elif 'openai' in var_name_lower:
                return 'sk-...'
            elif 'github' in var_name_lower:
                return 'ghp_...'
            else:
                return 'your-api-key-here'
        
        # Secret patterns
        if 'secret' in var_name_lower:
            if 'nextauth' in var_name_lower:
                return secrets.token_urlsafe(32)
            else:
                return 'your-secret-here'
        
        # ID patterns
        if 'id' in var_name_lower or 'ref' in var_name_lower:
            if 'supabase' in var_name_lower and ('project' in var_name_lower or 'ref' in var_name_lower):
                return 'abcdefghijklmnop'  # Supabase project ref format
            return 'your-id-here'
        
        # Default
        return f'your-{var_name.lower().replace("_", "-")}-here'
    
    def _get_var_description(self, var_name: str) -> str:
        """Get human-readable description for environment variable"""
        descriptions = {
            'SUPABASE_URL': 'Your Supabase project URL',
            'SUPABASE_ANON_KEY': 'Supabase anonymous/public API key',
            'SUPABASE_SERVICE_ROLE_KEY': 'Supabase service role key (admin access)',
            'SUPABASE_PROJECT_REF': 'Supabase project reference ID',
            'SUPABASE_MCP_TOKEN': 'Supabase MCP (Model Context Protocol) token',
            'SUPABASE_ACCESS_TOKEN': 'Supabase personal access token for API access',
            'STRIPE_PUBLISHABLE_KEY': 'Stripe publishable key (client-side)',
            'STRIPE_SECRET_KEY': 'Stripe secret key (server-side)',
            'STRIPE_WEBHOOK_SECRET': 'Stripe webhook endpoint secret',
            'OPENAI_API_KEY': 'OpenAI API key for AI services',
            'OPENAI_ORG_ID': 'OpenAI organization ID',
            'NEXTAUTH_SECRET': 'NextAuth.js secret for JWT encryption',
            'NEXTAUTH_URL': 'Base URL for NextAuth.js callbacks',
            'DATABASE_URL': 'Complete database connection string',
            'REDIS_URL': 'Redis connection string',
            'GITHUB_TOKEN': 'GitHub personal access token',
            'VERCEL_TOKEN': 'Vercel API token for deployments'
        }
        
        return descriptions.get(var_name, f'Configuration value for {var_name}')
    
    def _group_vars_by_category(self, env_vars: List[EnvironmentVariable]) -> Dict[str, List[EnvironmentVariable]]:
        """Group environment variables by category"""
        categories = {}
        for var in env_vars:
            category = var.category
            if category not in categories:
                categories[category] = []
            categories[category].append(var)
        
        # Sort categories by importance
        category_order = ['Core', 'Database & Auth', 'Payments', 'AI Services', 'Frontend', 'Development']
        ordered_categories = {}
        
        for category in category_order:
            if category in categories:
                ordered_categories[category] = categories[category]
        
        # Add any remaining categories
        for category, vars_list in categories.items():
            if category not in ordered_categories:
                ordered_categories[category] = vars_list
        
        return ordered_categories
    
    def _format_env_file(self, env_vars: List[EnvironmentVariable], include_values: bool = False) -> str:
        """Format environment variables as .env file content"""
        content = []
        content.append('# Environment Configuration')
        content.append(f'# Generated for {self.analyzer.project_info.project_type} project')
        content.append('')
        
        categories = self._group_vars_by_category(env_vars)
        
        for category, vars_in_category in categories.items():
            content.append(f'# {category}')
            
            for var in vars_in_category:
                # Add description as comment
                content.append(f'# {var.description}')
                
                # Add example if available and not including values
                if not include_values and var.example_value:
                    content.append(f'# Example: {var.name}={var.example_value}')
                
                # Add the variable
                if include_values and var.value:
                    content.append(f'{var.name}={var.value}')
                elif var.required:
                    content.append(f'{var.name}=')
                else:
                    content.append(f'# {var.name}=')
                
                content.append('')
        
        return '\n'.join(content)
    
    def write_env_files(self, project_path: Optional[Path] = None) -> Tuple[Path, Path]:
        """Write .env.example and .env.template files"""
        if project_path is None:
            project_path = self.project_path
        
        # Write .env.example (no values, for git)
        env_example_path = project_path / '.env.example'
        env_example_content = self.generate_env_example()
        env_example_path.write_text(env_example_content)
        
        # Write .env.template (with example values, not for git)
        env_template_path = project_path / '.env.template'
        env_template_content = self.generate_env_template()
        env_template_path.write_text(env_template_content)
        
        return env_example_path, env_template_path
    
    def get_setup_instructions(self) -> List[str]:
        """Get setup instructions for all detected services"""
        instructions = []
        
        for service in self.env_requirements.services:
            if service.setup_instructions:
                instructions.append(f"{service.name}: {service.setup_instructions}")
        
        return instructions