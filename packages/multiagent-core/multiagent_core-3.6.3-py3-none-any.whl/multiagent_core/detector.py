"""
Project Structure Detection Engine
Analyzes project directory to identify project type and structure
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

@dataclass
class ProjectInfo:
    """Information about detected project structure"""
    project_type: str
    language: str
    frameworks: Set[str]
    structure: str
    config_files: List[Path]
    has_backend: bool
    has_frontend: bool
    has_database: bool
    deployment_target: Optional[str] = None

class ProjectDetector:
    """Detects project structure and technology stack"""
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.project_info = None
    
    def detect(self) -> ProjectInfo:
        """Main detection method that analyzes project structure"""
        config_files = self._find_config_files()
        project_type = self._detect_project_type(config_files)
        language = self._detect_language(config_files)
        frameworks = self._detect_frameworks(config_files)
        structure = self._detect_structure()
        backend, frontend, database = self._detect_components(config_files)
        deployment = self._detect_deployment_target(config_files)
        
        self.project_info = ProjectInfo(
            project_type=project_type,
            language=language,
            frameworks=frameworks,
            structure=structure,
            config_files=config_files,
            has_backend=backend,
            has_frontend=frontend,
            has_database=database,
            deployment_target=deployment
        )
        
        return self.project_info
    
    def _find_config_files(self) -> List[Path]:
        """Find all configuration files in project"""
        config_patterns = [
            'package.json',
            'pyproject.toml',
            'requirements.txt',
            'Cargo.toml',
            'composer.json',
            'pom.xml',
            'build.gradle',
            'Gemfile',
            'go.mod',
            '.specify/**/*',
            'next.config.js',
            'next.config.ts',
            'tailwind.config.js',
            'tailwind.config.ts',
            'tsconfig.json',
            'jsconfig.json',
            'vite.config.js',
            'vite.config.ts',
            'webpack.config.js',
            'vercel.json',
            'netlify.toml',
            'Dockerfile',
            'docker-compose.yml',
            '.env*',
            '.github/workflows/*.yml',
            '.github/workflows/*.yaml'
        ]
        
        found_files = []
        for pattern in config_patterns:
            if '**' in pattern:
                # Handle glob patterns
                for file in self.project_path.glob(pattern):
                    if file.is_file():
                        found_files.append(file)
            else:
                file_path = self.project_path / pattern
                if file_path.exists():
                    found_files.append(file_path)
        
        return found_files
    
    def _detect_project_type(self, config_files: List[Path]) -> str:
        """Detect the primary project type"""
        file_names = {f.name for f in config_files}
        
        # Spec-kit project detection
        if any('.specify' in str(f) for f in config_files):
            return 'spec-kit'
        
        # Web application detection
        if 'package.json' in file_names:
            package_json = self.project_path / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                        deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                        
                        if 'next' in deps or 'next.js' in deps:
                            return 'web-app-nextjs'
                        elif 'react' in deps:
                            return 'web-app-react'
                        elif 'vue' in deps:
                            return 'web-app-vue'
                        elif 'angular' in deps:
                            return 'web-app-angular'
                        elif 'express' in deps or 'fastify' in deps:
                            return 'api-nodejs'
                        else:
                            return 'javascript'
                except (json.JSONDecodeError, FileNotFoundError):
                    return 'javascript'
        
        # Python project detection
        if 'pyproject.toml' in file_names or 'requirements.txt' in file_names:
            return 'python'
        
        # Other language detection
        if 'Cargo.toml' in file_names:
            return 'rust'
        elif 'composer.json' in file_names:
            return 'php'
        elif 'pom.xml' in file_names or 'build.gradle' in file_names:
            return 'java'
        elif 'Gemfile' in file_names:
            return 'ruby'
        elif 'go.mod' in file_names:
            return 'go'
        
        return 'unknown'
    
    def _detect_language(self, config_files: List[Path]) -> str:
        """Detect primary programming language"""
        file_names = {f.name for f in config_files}
        
        if 'package.json' in file_names:
            # Check for TypeScript
            if 'tsconfig.json' in file_names:
                return 'typescript'
            return 'javascript'
        elif 'pyproject.toml' in file_names or 'requirements.txt' in file_names:
            return 'python'
        elif 'Cargo.toml' in file_names:
            return 'rust'
        elif 'composer.json' in file_names:
            return 'php'
        elif 'pom.xml' in file_names or 'build.gradle' in file_names:
            return 'java'
        elif 'Gemfile' in file_names:
            return 'ruby'
        elif 'go.mod' in file_names:
            return 'go'
        
        return 'unknown'
    
    def _detect_frameworks(self, config_files: List[Path]) -> Set[str]:
        """Detect frameworks and major dependencies"""
        frameworks = set()
        
        # JavaScript/Node.js frameworks
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    all_deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    # Frontend frameworks
                    if 'next' in all_deps:
                        frameworks.add('nextjs')
                    if 'react' in all_deps:
                        frameworks.add('react')
                    if 'vue' in all_deps:
                        frameworks.add('vue')
                    if '@angular/core' in all_deps:
                        frameworks.add('angular')
                    
                    # CSS frameworks
                    if 'tailwindcss' in all_deps:
                        frameworks.add('tailwind')
                    if '@shadcn/ui' in all_deps or 'shadcn-ui' in all_deps:
                        frameworks.add('shadcn')
                    
                    # Backend frameworks
                    if 'express' in all_deps:
                        frameworks.add('express')
                    if 'fastify' in all_deps:
                        frameworks.add('fastify')
                    
                    # Database and services
                    if '@supabase/supabase-js' in all_deps:
                        frameworks.add('supabase')
                    if 'stripe' in all_deps:
                        frameworks.add('stripe')
                    if 'openai' in all_deps:
                        frameworks.add('openai')
                    if 'prisma' in all_deps:
                        frameworks.add('prisma')
                    if 'mongoose' in all_deps:
                        frameworks.add('mongoose')
                    
                    # Testing frameworks
                    if 'vitest' in all_deps:
                        frameworks.add('vitest')
                    if 'playwright' in all_deps:
                        frameworks.add('playwright')
                    if 'jest' in all_deps:
                        frameworks.add('jest')
                    
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Python frameworks
        requirements_files = [
            self.project_path / 'requirements.txt',
            self.project_path / 'pyproject.toml'
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                try:
                    content = req_file.read_text()
                    if 'fastapi' in content.lower():
                        frameworks.add('fastapi')
                    if 'django' in content.lower():
                        frameworks.add('django')
                    if 'flask' in content.lower():
                        frameworks.add('flask')
                    if 'sqlalchemy' in content.lower():
                        frameworks.add('sqlalchemy')
                    if 'pydantic' in content.lower():
                        frameworks.add('pydantic')
                    if 'pytest' in content.lower():
                        frameworks.add('pytest')
                except FileNotFoundError:
                    continue
        
        # Config file detection
        config_names = {f.name for f in config_files}
        if 'next.config.js' in config_names or 'next.config.ts' in config_names:
            frameworks.add('nextjs')
        if 'tailwind.config.js' in config_names or 'tailwind.config.ts' in config_names:
            frameworks.add('tailwind')
        if 'vite.config.js' in config_names or 'vite.config.ts' in config_names:
            frameworks.add('vite')
        
        return frameworks
    
    def _detect_structure(self) -> str:
        """Detect project structure pattern"""
        dirs = [d for d in self.project_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        dir_names = {d.name for d in dirs}
        
        # Web application patterns
        if 'frontend' in dir_names and 'backend' in dir_names:
            return 'frontend-backend'
        elif 'client' in dir_names and 'server' in dir_names:
            return 'client-server'
        elif 'app' in dir_names and 'api' in dir_names:
            return 'app-api'
        elif 'src' in dir_names and 'api' in dir_names:
            return 'src-api'
        
        # Mobile patterns
        if 'ios' in dir_names or 'android' in dir_names:
            return 'mobile'
        
        # Single project patterns
        if 'src' in dir_names:
            return 'src-based'
        elif 'lib' in dir_names:
            return 'lib-based'
        
        return 'flat'
    
    def _detect_components(self, config_files: List[Path]) -> tuple[bool, bool, bool]:
        """Detect if project has backend, frontend, and database components"""
        frameworks = self._detect_frameworks(config_files)
        structure = self._detect_structure()
        
        # Backend detection
        has_backend = (
            'backend' in structure or
            'server' in structure or
            'api' in structure or
            any(fw in frameworks for fw in ['express', 'fastify', 'fastapi', 'django', 'flask'])
        )
        
        # Frontend detection
        has_frontend = (
            'frontend' in structure or
            'client' in structure or
            'app' in structure or
            any(fw in frameworks for fw in ['react', 'vue', 'angular', 'nextjs'])
        )
        
        # Database detection
        has_database = any(fw in frameworks for fw in [
            'supabase', 'prisma', 'mongoose', 'sqlalchemy'
        ])
        
        return has_backend, has_frontend, has_database
    
    def _detect_deployment_target(self, config_files: List[Path]) -> Optional[str]:
        """Detect likely deployment target"""
        config_names = {f.name for f in config_files}
        
        if 'vercel.json' in config_names:
            return 'vercel'
        elif 'netlify.toml' in config_names:
            return 'netlify'
        elif 'Dockerfile' in config_names:
            return 'docker'
        elif any('heroku' in str(f).lower() for f in config_files):
            return 'heroku'
        
        # Check for framework-based deployment hints
        frameworks = self._detect_frameworks(config_files)
        if 'nextjs' in frameworks:
            return 'vercel'  # Next.js commonly deployed on Vercel
        
        return None
    
    def get_summary(self) -> Dict:
        """Get a summary of the detected project information"""
        if not self.project_info:
            self.detect()
        
        return {
            'project_type': self.project_info.project_type,
            'language': self.project_info.language,
            'frameworks': list(self.project_info.frameworks),
            'structure': self.project_info.structure,
            'components': {
                'backend': self.project_info.has_backend,
                'frontend': self.project_info.has_frontend,
                'database': self.project_info.has_database
            },
            'deployment_target': self.project_info.deployment_target,
            'config_files_found': len(self.project_info.config_files)
        }